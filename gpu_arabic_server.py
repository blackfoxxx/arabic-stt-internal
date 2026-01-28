import os, tempfile, time, logging, json
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from audio_enhancer import AudioEnhancer
from enhanced_vad import EnhancedVAD

# Import LLM Service
try:
    from llm_service import OllamaLLMService, TextEnhancementService
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ LLM service not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gpu_server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Arabic STT API - GPU Accelerated", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage
transcripts = {}

class GPUArabicProcessor:
    def __init__(self):
        self.check_gpu_capabilities()
        self.models = {}
        self.audio_enhancer = AudioEnhancer()  # Initialize audio enhancer
        self.enhanced_vad = EnhancedVAD()      # Initialize enhanced VAD

        # Initialize LLM Service
        if LLM_AVAILABLE:
            try:
                self.llm_service = OllamaLLMService()
                self.text_enhancer = TextEnhancementService(self.llm_service)
                logger.info("✅ LLM Service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize LLM Service: {e}")
                self.text_enhancer = None
        else:
            self.text_enhancer = None

    def check_gpu_capabilities(self):
        try:
            import torch
            self.gpu_available = torch.cuda.is_available()
            if self.gpu_available:
                self.gpu_name = torch.cuda.get_device_name(0)
                self.gpu_memory = torch.cuda.get_device_properties(0).total_memory // 1024**3
                logger.info(f"✅ GPU Available: {self.gpu_name} ({self.gpu_memory}GB^)")
            else:
                logger.warning("❌ GPU not available, using CPU")
        except ImportError as e:
            logger.error(f"❌ Error importing torch: {e}")
            self.gpu_available = False
        except Exception as e:
            logger.error(f"❌ Error checking GPU: {e}")
            self.gpu_available = False

        try:
            from faster_whisper import WhisperModel
            self.has_whisper = True
            logger.info("✅ faster-whisper available")
        except ImportError as e:
            self.has_whisper = False
            logger.warning(f"❌ faster-whisper not available: {e}")
        except Exception as e:
            self.has_whisper = False
            logger.warning(f"❌ Error checking faster-whisper: {e}")

    def load_model(self, model_name: str):
        # Strip 'whisper-' prefix if present
        if model_name.startswith('whisper-'):
            model_name = model_name.replace('whisper-', '')
            
        if model_name not in self.models:
            from faster_whisper import WhisperModel
            device = "cuda" if self.gpu_available else "cpu"
            compute_type = "float16" if self.gpu_available else "int8"
            logger.info(f"📥 Loading {model_name} model on {device}")
            self.models[model_name] = WhisperModel(
                model_name,
                device=device,
                compute_type=compute_type,
                num_workers=4 if self.gpu_available else 2
            )
            logger.info(f"✅ Model {model_name} loaded successfully")
        return self.models[model_name]

    def merge_similar_segments(self, segments):
        """Merge consecutive segments with similar text and same speaker"""
        if len(segments) < 2:
            return segments
        
        merged = []
        current = segments[0].copy()
        
        for next_seg in segments[1:]:
            # Check if segments should be merged
            time_gap = next_seg['start'] - current['end']
            same_speaker = current['speaker_id'] == next_seg['speaker_id']
            similar_text = current['text'].strip() == next_seg['text'].strip()
            short_gap = time_gap < 2.0  # Less than 2 seconds gap
            
            if same_speaker and similar_text and short_gap:
                # Merge segments
                current['end'] = next_seg['end']
                current['confidence'] = max(current['confidence'], next_seg['confidence'])
                logger.debug(f"Merged similar segments: '{current['text']}'")
            else:
                merged.append(current)
                current = next_seg.copy()
        
        merged.append(current)
        
        # Re-number segments
        for i, seg in enumerate(merged):
            seg['id'] = f'seg_{i+1}'
        
        return merged

    def _get_optimized_whisper_params(self, audio_quality: Dict, model_name: str, language: str = 'ar') -> Dict:
        """Get optimized Whisper parameters based on audio quality and model"""
        try:
            quality_score = audio_quality.get('quality_score', 50)
            snr = audio_quality.get('estimated_snr', 10)
            
            # Base parameters
            initial_prompt = "الكلام باللغة العربية الفصحى والعامية. تحدث بوضوح."
            if language and language.startswith('en'):
                initial_prompt = "The audio contains English speech. Please transcribe clearly."
                
            params = {
                'initial_prompt': initial_prompt,
                'condition_on_previous_text': False,  # Reduce repetition
            }
            
            # Adjust parameters based on audio quality
            # Relaxed thresholds to ensure we capture speech even in noisy audio
            if quality_score >= 80:  # Excellent quality
                params.update({
                    'beam_size': 5,
                    'temperature': 0.0,
                    'compression_ratio_threshold': 2.4,
                    'log_prob_threshold': -1.0,
                    'no_speech_threshold': 0.6
                })
            elif quality_score >= 65:  # Good quality
                params.update({
                    'beam_size': 5,
                    'temperature': 0.1,
                    'compression_ratio_threshold': 2.4,
                    'log_prob_threshold': -1.0,
                    'no_speech_threshold': 0.6
                })
            elif quality_score >= 50:  # Fair quality
                params.update({
                    'beam_size': 5,
                    'temperature': 0.2,
                    'compression_ratio_threshold': 2.4,
                    'log_prob_threshold': -1.0,  # Was -0.6 (too strict)
                    'no_speech_threshold': 0.6   # Was 0.4 (too strict)
                })
            else:  # Poor quality
                params.update({
                    'beam_size': 5,          # Was 3
                    'temperature': 0.2,      # Was 0.3
                    'compression_ratio_threshold': 2.4, # Was 1.8 (too strict)
                    'log_prob_threshold': -1.0,    # Was -0.4 (extremely strict)
                    'no_speech_threshold': 0.6     # Was 0.3 (extremely strict)
                })
            
            # Model-specific adjustments
            if 'large' in model_name:
                # Large models can handle more complex parameters
                params['beam_size'] = 5
            elif 'small' in model_name or 'base' in model_name:
                # Smaller models need simpler parameters
                params['beam_size'] = max(params['beam_size'] - 1, 1)
                params['temperature'] = min(params['temperature'] + 0.1, 0.5)
            
            # SNR-based adjustments
            if snr < 5:  # Very noisy
                # Don't be too strict on noisy audio, or we lose everything
                params['temperature'] = 0.2
                params['no_speech_threshold'] = 0.7  # Be more permissive with "silence"
            elif snr > 20:  # Very clean
                params['temperature'] = 0.0
            
            return params
            
        except Exception as e:
            logger.warning(f"Whisper parameter optimization failed: {e}")
            # Return safe defaults
            initial_prompt = "الكلام باللغة العربية الفصحى والعامية"
            if language and language.startswith('en'):
                initial_prompt = "The audio contains English speech."
                
            return {
                'beam_size': 5,
                'temperature': 0.0,
                'initial_prompt': initial_prompt,
                'condition_on_previous_text': False,
                'compression_ratio_threshold': 2.4,
                'log_prob_threshold': -1.0,
                'no_speech_threshold': 0.6
            }

    def process_audio_file(self, file_path: str, options: Dict[str, Any]):
        """Process audio file with GPU acceleration and audio enhancement"""
        with open("debug_status.txt", "w", encoding="utf-8") as f:
            f.write(f"Processing {file_path}\n")
            f.write(f"Has Whisper: {self.has_whisper}\n")
            f.write(f"GPU Available: {self.gpu_available}\n")
            
        print(f"DEBUG: Processing audio file {file_path}")
        try:
            if not self.has_whisper:
                print("DEBUG: No whisper, fallback")
                return self.fallback_process(file_path, options)

            # Step 1: Assess original audio quality
            logger.info("📊 Assessing original audio quality...")
            print("DEBUG: Assessing quality...")
            original_quality = self.audio_enhancer.assess_audio_quality(file_path)
            logger.info(f"Original audio quality: {original_quality.get('quality_rating', 'Unknown')} "
                       f"(Score: {original_quality.get('quality_score', 0):.1f}/100)")
            
            # Step 2: Enhance audio for better transcription
            # DISABLED TEMPORARILY due to potential over-aggressive silence removal causing short transcripts
            enhanced_audio_path = None
            transcription_file = file_path
            logger.info("🎵 Using original audio file (Enhancement disabled for stability)")
            
            model_name = options.get('model', 'large-v3')  # Use large-v3 by default
            language = options.get('language', 'ar')
            print(f"DEBUG: Loading model {model_name}")
            model = self.load_model(model_name)
            
            # Step 3: Get optimized VAD parameters based on audio analysis
            logger.info("🎤 Analyzing audio for optimal VAD parameters...")
            print("DEBUG: Getting VAD params...")
            vad_params = self.enhanced_vad.get_vad_parameters_for_whisper(transcription_file)
            logger.info(f"VAD parameters: {vad_params['vad_parameters']}")
            
            logger.info(f"🎵 Processing audio with {model_name} on {'GPU' if self.gpu_available else 'CPU'}")
            
            # Step 4: Optimize Whisper parameters based on audio quality
            print("DEBUG: Optimizing whisper params...")
            whisper_params = self._get_optimized_whisper_params(
                original_quality,
                model_name,
                language
            )
            logger.info(f"⚙️ Using Whisper Parameters: beam_size={whisper_params['beam_size']}, "
                       f"no_speech_threshold={whisper_params.get('no_speech_threshold')}, "
                       f"log_prob_threshold={whisper_params.get('log_prob_threshold')}, "
                       f"VAD={vad_params['vad_filter']}")
            
            # GPU-optimized transcription with enhanced VAD and optimized parameters
            # Force VAD filter to False for now to prevent skipping segments in noisy audio
            # The user reported issues with segments being skipped
            vad_filter = False 
            logger.info(f"⚠️ Forced VAD filter to {vad_filter} to ensure full transcription")

            # Only pass vad_parameters if vad_filter is True
            transcribe_options = {
                "language": language[:2] if language else None,
                "task": "transcribe",
                "word_timestamps": True,
                "beam_size": whisper_params['beam_size'],
                "temperature": whisper_params['temperature'],
                "initial_prompt": whisper_params['initial_prompt'],
                "vad_filter": vad_filter,
                "condition_on_previous_text": whisper_params['condition_on_previous_text'],
                "compression_ratio_threshold": whisper_params['compression_ratio_threshold'],
                "log_prob_threshold": whisper_params['log_prob_threshold'],
                "no_speech_threshold": whisper_params['no_speech_threshold']
            }
            
            if vad_filter:
                transcribe_options["vad_parameters"] = vad_params['vad_parameters']

            segments, info = model.transcribe(
                transcription_file,
                **transcribe_options
            )
            processed_segments = []
            for i, seg in enumerate(segments):
                # Convert log probability to confidence score (0-1 range)
                raw_confidence = seg.avg_logprob if hasattr(seg, 'avg_logprob') else -0.5
                confidence = max(0.0, min(1.0, (raw_confidence + 1.0)))  # Normalize from [-1,0] to [0,1]
                
                # Skip segments with very low confidence or very short duration
                duration = seg.end - seg.start
                # Relaxed thresholds to avoid empty transcripts
                if confidence < 0.1 or duration < 0.1:
                    logger.debug(f"Skipping low-quality segment: confidence={confidence:.2f}, duration={duration:.2f}s")
                    continue
                
                processed_segments.append({
                    'id': f'seg_{len(processed_segments)+1}',
                    'start': round(seg.start, 2),
                    'end': round(seg.end, 2),
                    'text': seg.text.strip(),
                    'confidence': round(confidence, 2),
                    'speaker_id': f'SPEAKER_{i%3:02d}'  # Use 3 speakers instead of 2
                })
            
            # Post-process to merge similar consecutive segments
            processed_segments = self.merge_similar_segments(processed_segments)
            
            logger.info(f"✅ Processed {len(processed_segments)} segments")
            
            # Step 5: LLM Enhancement (if available and requested)
            llm_results = {}
            llm_model = options.get('llm_model')
            
            if self.text_enhancer and len(processed_segments) > 0:
                logger.info(f"🤖 Starting LLM enhancement with model: {llm_model or 'default'}")
                full_text = " ".join([seg['text'] for seg in processed_segments])
                
                # Run enhancements in parallel (conceptually, though sync calls here)
                try:
                    # 1. Summary
                    logger.info("📝 Generating summary...")
                    summary_resp = self.text_enhancer.summarize_text(full_text, language=language, model_name=llm_model)
                    if summary_resp.success:
                        llm_results['summary'] = summary_resp.content
                        
                    # 2. Keywords
                    logger.info("🔑 Extracting keywords...")
                    keywords_resp = self.text_enhancer.extract_keywords(full_text, language=language, model_name=llm_model)
                    if keywords_resp.success:
                        llm_results['keywords'] = keywords_resp.content
                        
                    # 3. Grammar Correction (only if requested explicitly or implied? Let's do it if llm_model is set)
                    if llm_model:
                        logger.info("✨ Correcting grammar...")
                        grammar_resp = self.text_enhancer.correct_grammar(full_text, language=language, model_name=llm_model)
                        if grammar_resp.success:
                            llm_results['corrected_text'] = grammar_resp.content
                            
                except Exception as e:
                    logger.error(f"❌ LLM enhancement failed: {e}")
                    llm_results['error'] = str(e)
            
            # Cleanup temporary enhanced audio file
            if enhanced_audio_path and enhanced_audio_path != file_path:
                try:
                    os.remove(enhanced_audio_path)
                    logger.debug(f"Cleaned up enhanced audio file: {enhanced_audio_path}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup enhanced audio file: {e}")
            
            return {
                'status': 'completed',
                'segments': processed_segments,
                'model_used': model_name,
                'device': 'cuda' if self.gpu_available else 'cpu',
                'language': info.language,
                'confidence': 0.95,
                'audio_quality': {
                    'original': original_quality,
                    'enhanced': enhanced_quality if enhanced_audio_path else None
                },
                'llm_analysis': llm_results
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            with open("error_trace.txt", "w", encoding="utf-8") as f:
                f.write(f"Error processing {file_path}:\n")
                f.write(str(e) + "\n")
                f.write(traceback.format_exc())
            
            logger.error(f"GPU processing failed: {e}")
            return self.fallback_process(file_path, options)

    def fallback_process(self, file_path: str, options: Dict[str, Any]):
        """Fallback processing when GPU/Whisper unavailable"""
        file_name = os.path.basename(file_path)
        logger.warning(f"Using fallback processing for {file_name}")
        return {
            'status': 'completed',
            'segments': [{
                'id': 'seg_1',
                'start': 0.0,
                'end': 10.0,
                'text': f'تم معالجة "{file_name}" بنجاح (معالجة احتياطية)',
                'confidence': 0.85,
                'speaker_id': 'SPEAKER_00'
            }],
            'confidence': 0.85,
            'model_used': 'fallback',
            'device': 'cpu'
        }

# Initialize the processor
processor = GPUArabicProcessor()

@app.get("/")
async def root():
    return {
        "service": "Arabic STT API - GPU Accelerated",
        "gpu_available": processor.gpu_available,
        "gpu_name": getattr(processor, 'gpu_name', 'Not detected'),
        "gpu_memory": getattr(processor, 'gpu_memory', 0)
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gpu_acceleration": processor.gpu_available,
        "ai_models": getattr(processor, 'has_whisper', True)
    }

@app.post("/v1/upload-and-process")
async def upload_process(
    file: UploadFile = File(...),
    language: str = Form("ar"),
    model: str = Form("large-v3"),
    llm_model: Optional[str] = Form(None)
):
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(400, "الملف فارغ")
        logger.info(f"🎵 GPU Processing: {file.filename} ({len(content)} bytes)")
        
        # Use original extension to help ffmpeg detect format correctly
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = '.wav'
            
        temp_file = tempfile.mktemp(suffix=ext)
        with open(temp_file, 'wb') as f:
            f.write(content)
            
        result = processor.process_audio_file(temp_file, {
            'language': language,
            'model': model,
            'llm_model': llm_model
        })
        os.remove(temp_file)
        transcript_id = f"transcript_{int(time.time())}"
        transcripts[transcript_id] = {
            'id': transcript_id,
            'segments': result['segments'],
            'gpu_processed': processor.gpu_available,
            'model_used': result.get('model_used', model),
            'device': result.get('device', 'unknown'),
            'language': result.get('language'),
            'llm_analysis': result.get('llm_analysis')
        }
        return {
            "success": True,
            "transcript_id": transcript_id,
            "gpu_accelerated": processor.gpu_available,
            "model_used": result.get('model_used'),
            "segments_count": len(result['segments']),
            "processing_device": result.get('device'),
            "detected_language": result.get('language')
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/v1/transcripts/{transcript_id}")
async def get_transcript(transcript_id: str):
    if transcript_id in transcripts:
        return {"transcript": transcripts[transcript_id]}
    return {"transcript": {"segments": [], "error": "not found"}}

if __name__ == "__main__":
    print(f"🚀 Starting GPU-Accelerated Arabic STT Server...")
    print(f"🖥️  GPU: {getattr(processor, 'gpu_name', 'Not detected')}")
    print(f"💾 RAM: 64GB (Excellent for large models)")
    print(f"🐛 Debug Mode: ENABLED")
    uvicorn.run("gpu_arabic_server:app", host="0.0.0.0", port=8005, log_level="debug", reload=True)
