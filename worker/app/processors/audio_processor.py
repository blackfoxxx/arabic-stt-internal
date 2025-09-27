"""
Audio processing utilities using FFmpeg and audio enhancement
"""

import os
import subprocess
import tempfile
import json
from typing import Dict, Any, Optional, Tuple
import librosa
import soundfile as sf
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


class AudioProcessor:
    """Audio processing and enhancement for Arabic STT"""
    
    def __init__(self):
        self.supported_formats = {
            "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
            "video": ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
        }
        
        # Check FFmpeg availability
        self.ffmpeg_available = self._check_ffmpeg()
        if not self.ffmpeg_available:
            logger.warning("FFmpeg not available - audio processing will be limited")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                timeout=5
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def extract_audio(self, input_path: str, output_path: str) -> bool:
        """Extract audio from video or convert audio format"""
        
        if not self.ffmpeg_available:
            logger.error("FFmpeg not available for audio extraction")
            return False
        
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-ar", "16000",  # 16kHz sample rate
                "-ac", "1",  # Mono channel
                "-f", "wav",  # WAV format
                "-y", output_path  # Overwrite output
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,  # 5 minute timeout
                text=True
            )
            
            if result.returncode != 0:
                logger.error("FFmpeg audio extraction failed", 
                           error=result.stderr, cmd=" ".join(cmd))
                return False
            
            # Verify output file exists and has content
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                logger.error("Audio extraction produced empty file")
                return False
            
            logger.info("Audio extracted successfully", 
                       input=input_path, output=output_path,
                       size=os.path.getsize(output_path))
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Audio extraction timed out")
            return False
        except Exception as e:
            logger.error("Audio extraction failed", error=str(e))
            return False
    
    def enhance_audio(
        self, 
        input_path: str, 
        output_path: str, 
        enhancement_level: str = "medium"
    ) -> bool:
        """Enhance audio quality for better ASR results"""
        
        try:
            # Step 1: Basic cleanup with FFmpeg
            temp_cleaned = tempfile.mktemp(suffix='.wav')
            if not self._basic_audio_cleanup(input_path, temp_cleaned):
                return False
            
            # Step 2: Advanced enhancement based on level
            if enhancement_level == "high":
                enhanced = self._advanced_enhancement(temp_cleaned, output_path)
            elif enhancement_level == "medium":
                enhanced = self._medium_enhancement(temp_cleaned, output_path)
            else:  # light or none
                enhanced = self._light_enhancement(temp_cleaned, output_path)
            
            # Cleanup temp file
            if os.path.exists(temp_cleaned):
                os.remove(temp_cleaned)
            
            return enhanced
            
        except Exception as e:
            logger.error("Audio enhancement failed", error=str(e))
            return False
    
    def _basic_audio_cleanup(self, input_path: str, output_path: str) -> bool:
        """Basic audio cleanup with FFmpeg"""
        
        if not self.ffmpeg_available:
            # Fallback: just copy file
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-vn",  # No video
                "-ac", "1",  # Mono
                "-ar", "16000",  # 16kHz
                "-af", "highpass=f=80,lowpass=f=8000",  # Basic filtering
                "-c:a", "pcm_s16le",  # 16-bit PCM
                "-y", output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
            
        except Exception as e:
            logger.error("Basic audio cleanup failed", error=str(e))
            return False
    
    def _light_enhancement(self, input_path: str, output_path: str) -> bool:
        """Light audio enhancement"""
        
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-af", "dynaudnorm=g=7:s=50,highpass=f=60,lowpass=f=7500",
                "-ar", "16000", "-ac", "1",
                "-y", output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
            
        except Exception as e:
            logger.error("Light enhancement failed", error=str(e))
            # Fallback: copy original
            import shutil
            shutil.copy2(input_path, output_path)
            return True
    
    def _medium_enhancement(self, input_path: str, output_path: str) -> bool:
        """Medium audio enhancement with noise reduction"""
        
        try:
            # Use FFmpeg's arnndn filter for noise reduction
            cmd = [
                "ffmpeg", "-i", input_path,
                "-af", "afftdn=nf=15:tn=1,dynaudnorm=g=5:s=30,highpass=f=60,lowpass=f=7500",
                "-ar", "16000", "-ac", "1",
                "-y", output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            
            if result.returncode == 0:
                return True
            else:
                # Fallback to light enhancement
                logger.warning("Medium enhancement failed, falling back to light")
                return self._light_enhancement(input_path, output_path)
                
        except Exception as e:
            logger.error("Medium enhancement failed", error=str(e))
            return self._light_enhancement(input_path, output_path)
    
    def _advanced_enhancement(self, input_path: str, output_path: str) -> bool:
        """Advanced audio enhancement with multiple techniques"""
        
        try:
            # Multi-stage enhancement
            temp_stage1 = tempfile.mktemp(suffix='.wav')
            temp_stage2 = tempfile.mktemp(suffix='.wav')
            
            # Stage 1: Aggressive noise reduction
            cmd1 = [
                "ffmpeg", "-i", input_path,
                "-af", "afftdn=nf=25:tn=1",
                "-y", temp_stage1
            ]
            
            if subprocess.run(cmd1, capture_output=True, timeout=300).returncode != 0:
                return self._medium_enhancement(input_path, output_path)
            
            # Stage 2: Dynamic normalization and compression
            cmd2 = [
                "ffmpeg", "-i", temp_stage1,
                "-af", "dynaudnorm=g=3:s=20,compand=0.1,0.2:-90,-90,-40,-25,-20,-15,0,-5:6:0.1:0.1",
                "-y", temp_stage2
            ]
            
            if subprocess.run(cmd2, capture_output=True, timeout=300).returncode != 0:
                return self._medium_enhancement(input_path, output_path)
            
            # Stage 3: Final filtering and normalization
            cmd3 = [
                "ffmpeg", "-i", temp_stage2,
                "-af", "highpass=f=60,lowpass=f=7500,dynaudnorm=g=5",
                "-ar", "16000", "-ac", "1",
                "-y", output_path
            ]
            
            success = subprocess.run(cmd3, capture_output=True, timeout=300).returncode == 0
            
            # Cleanup temp files
            for temp_file in [temp_stage1, temp_stage2]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            if success:
                return True
            else:
                return self._medium_enhancement(input_path, output_path)
                
        except Exception as e:
            logger.error("Advanced enhancement failed", error=str(e))
            return self._medium_enhancement(input_path, output_path)
    
    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract audio/video metadata"""
        
        try:
            # Use FFprobe for metadata extraction
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30, text=True)
            
            if result.returncode != 0:
                logger.error("FFprobe failed", error=result.stderr)
                return None
            
            metadata = json.loads(result.stdout)
            
            # Extract relevant information
            format_info = metadata.get("format", {})
            audio_stream = None
            
            # Find audio stream
            for stream in metadata.get("streams", []):
                if stream.get("codec_type") == "audio":
                    audio_stream = stream
                    break
            
            if not audio_stream:
                logger.error("No audio stream found in file")
                return None
            
            extracted_metadata = {
                "duration": float(format_info.get("duration", 0)),
                "file_size": int(format_info.get("size", 0)),
                "sample_rate": int(audio_stream.get("sample_rate", 0)),
                "channels": int(audio_stream.get("channels", 1)),
                "codec": audio_stream.get("codec_name", "unknown"),
                "bitrate": int(audio_stream.get("bit_rate", 0)) if audio_stream.get("bit_rate") else None,
                "format_name": format_info.get("format_name", "unknown")
            }
            
            return extracted_metadata
            
        except Exception as e:
            logger.error("Metadata extraction failed", error=str(e))
            return None
    
    def validate_audio_quality(self, file_path: str) -> Dict[str, Any]:
        """Validate audio quality for STT processing"""
        
        try:
            # Load audio with librosa
            audio, sr = librosa.load(file_path, sr=None)
            
            # Calculate quality metrics
            quality_metrics = {
                "sample_rate": sr,
                "duration": len(audio) / sr,
                "rms_energy": float(np.sqrt(np.mean(audio**2))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(audio))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(audio, sr=sr))),
                "snr_estimate": self._estimate_snr(audio),
                "quality_score": 0.0
            }
            
            # Calculate quality score (0-1)
            score = 0.0
            
            # Sample rate score (16kHz is optimal)
            if sr >= 16000:
                score += 0.3
            elif sr >= 8000:
                score += 0.2
            
            # Duration score
            duration = quality_metrics["duration"]
            if duration > 5:  # At least 5 seconds
                score += 0.2
            
            # Signal energy score
            rms = quality_metrics["rms_energy"]
            if rms > 0.01:  # Reasonable signal level
                score += 0.2
            
            # SNR score
            snr = quality_metrics["snr_estimate"]
            if snr > 10:  # Good SNR
                score += 0.3
            elif snr > 5:  # Acceptable SNR
                score += 0.2
            
            quality_metrics["quality_score"] = min(1.0, score)
            
            # Quality assessment
            if quality_metrics["quality_score"] >= 0.8:
                quality_metrics["assessment"] = "excellent"
            elif quality_metrics["quality_score"] >= 0.6:
                quality_metrics["assessment"] = "good"
            elif quality_metrics["quality_score"] >= 0.4:
                quality_metrics["assessment"] = "fair"
            else:
                quality_metrics["assessment"] = "poor"
            
            return quality_metrics
            
        except Exception as e:
            logger.error("Audio quality validation failed", error=str(e))
            return {
                "quality_score": 0.0,
                "assessment": "unknown",
                "error": str(e)
            }
    
    def _estimate_snr(self, audio: np.ndarray, frame_len: int = 2048) -> float:
        """Estimate Signal-to-Noise Ratio"""
        try:
            # Simple SNR estimation using energy-based approach
            # Split audio into frames
            frames = librosa.util.frame(audio, frame_length=frame_len, hop_length=frame_len//2)
            
            # Calculate frame energies
            frame_energies = np.sum(frames**2, axis=0)
            
            # Estimate noise floor (bottom 10% of frame energies)
            noise_threshold = np.percentile(frame_energies, 10)
            signal_threshold = np.percentile(frame_energies, 90)
            
            # Calculate SNR in dB
            if noise_threshold > 0:
                snr_db = 10 * np.log10(signal_threshold / noise_threshold)
                return float(snr_db)
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def convert_to_mono_16k(self, input_path: str, output_path: str) -> bool:
        """Convert audio to mono 16kHz WAV format optimized for ASR"""
        
        try:
            # Load audio
            audio, sr = librosa.load(input_path, sr=16000, mono=True)
            
            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.9
            
            # Save as WAV
            sf.write(output_path, audio, 16000, subtype='PCM_16')
            
            logger.info("Audio converted to mono 16kHz", 
                       input=input_path, output=output_path,
                       duration=len(audio)/16000)
            
            return True
            
        except Exception as e:
            logger.error("Audio conversion failed", error=str(e))
            return False
    
    def apply_noise_reduction(self, input_path: str, output_path: str, method: str = "spectral") -> bool:
        """Apply noise reduction using different methods"""
        
        try:
            if method == "spectral":
                return self._spectral_noise_reduction(input_path, output_path)
            elif method == "rnnoise":
                return self._rnnoise_reduction(input_path, output_path)
            else:
                # Fallback to FFmpeg filtering
                return self._ffmpeg_noise_reduction(input_path, output_path)
                
        except Exception as e:
            logger.error("Noise reduction failed", method=method, error=str(e))
            return False
    
    def _spectral_noise_reduction(self, input_path: str, output_path: str) -> bool:
        """Spectral noise reduction using librosa"""
        
        try:
            import noisereduce as nr
            
            # Load audio
            audio, sr = librosa.load(input_path, sr=16000)
            
            # Apply noise reduction
            reduced_audio = nr.reduce_noise(
                y=audio, 
                sr=sr,
                stationary=False,  # Non-stationary noise reduction
                prop_decrease=0.8   # Reduce noise by 80%
            )
            
            # Save enhanced audio
            sf.write(output_path, reduced_audio, sr, subtype='PCM_16')
            
            logger.info("Spectral noise reduction applied successfully")
            return True
            
        except Exception as e:
            logger.error("Spectral noise reduction failed", error=str(e))
            return False
    
    def _rnnoise_reduction(self, input_path: str, output_path: str) -> bool:
        """RNNoise-based noise reduction"""
        
        try:
            # Check if RNNoise is available
            result = subprocess.run(["which", "rnnoise_demo"], capture_output=True)
            if result.returncode != 0:
                logger.warning("RNNoise not available, falling back to spectral")
                return self._spectral_noise_reduction(input_path, output_path)
            
            # RNNoise expects 48kHz mono PCM
            temp_48k = tempfile.mktemp(suffix='.raw')
            temp_denoised = tempfile.mktemp(suffix='.raw')
            
            # Convert to 48kHz raw PCM
            cmd_to_raw = [
                "ffmpeg", "-i", input_path,
                "-f", "s16le", "-acodec", "pcm_s16le",
                "-ac", "1", "-ar", "48000",
                "-y", temp_48k
            ]
            
            if subprocess.run(cmd_to_raw, capture_output=True).returncode != 0:
                return self._spectral_noise_reduction(input_path, output_path)
            
            # Apply RNNoise
            cmd_denoise = ["rnnoise_demo", temp_48k, temp_denoised]
            if subprocess.run(cmd_denoise, capture_output=True).returncode != 0:
                return self._spectral_noise_reduction(input_path, output_path)
            
            # Convert back to 16kHz WAV
            cmd_to_wav = [
                "ffmpeg", "-f", "s16le", "-ar", "48000", "-ac", "1",
                "-i", temp_denoised,
                "-ar", "16000",
                "-y", output_path
            ]
            
            success = subprocess.run(cmd_to_wav, capture_output=True).returncode == 0
            
            # Cleanup
            for temp_file in [temp_48k, temp_denoised]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            if success:
                logger.info("RNNoise reduction applied successfully")
                return True
            else:
                return self._spectral_noise_reduction(input_path, output_path)
                
        except Exception as e:
            logger.error("RNNoise reduction failed", error=str(e))
            return self._spectral_noise_reduction(input_path, output_path)
    
    def _ffmpeg_noise_reduction(self, input_path: str, output_path: str) -> bool:
        """FFmpeg-based noise reduction"""
        
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-af", "afftdn=nf=20:tn=1,dynaudnorm,highpass=f=60,lowpass=f=7500",
                "-ar", "16000", "-ac", "1",
                "-y", output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
            
        except Exception as e:
            logger.error("FFmpeg noise reduction failed", error=str(e))
            return False
    
    def _medium_enhancement(self, input_path: str, output_path: str) -> bool:
        """Medium enhancement using librosa and spectral processing"""
        
        try:
            # Load audio
            audio, sr = librosa.load(input_path, sr=16000)
            
            # Apply spectral noise reduction
            import noisereduce as nr
            reduced_audio = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.6)
            
            # Apply dynamic range compression
            # Simple compression using numpy
            threshold = 0.7
            ratio = 4.0
            compressed = np.where(
                np.abs(reduced_audio) > threshold,
                np.sign(reduced_audio) * (threshold + (np.abs(reduced_audio) - threshold) / ratio),
                reduced_audio
            )
            
            # Normalize
            if np.max(np.abs(compressed)) > 0:
                compressed = compressed / np.max(np.abs(compressed)) * 0.9
            
            # Save result
            sf.write(output_path, compressed, sr, subtype='PCM_16')
            
            logger.info("Medium enhancement completed successfully")
            return True
            
        except Exception as e:
            logger.error("Medium enhancement failed", error=str(e))
            return self._light_enhancement(input_path, output_path)
    
    def split_audio_by_silence(
        self, 
        input_path: str, 
        min_silence_len: int = 500,
        silence_thresh: int = -40
    ) -> List[Tuple[float, float]]:
        """Split audio by silence detection"""
        
        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence
            
            # Load audio
            audio = AudioSegment.from_wav(input_path)
            
            # Split on silence
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=100  # Keep 100ms of silence
            )
            
            # Convert to time ranges
            segments = []
            current_time = 0.0
            
            for chunk in chunks:
                duration = len(chunk) / 1000.0  # Convert to seconds
                segments.append((current_time, current_time + duration))
                current_time += duration
            
            logger.info("Audio split by silence", segments_count=len(segments))
            return segments
            
        except Exception as e:
            logger.error("Audio splitting failed", error=str(e))
            return []
    
    def get_audio_fingerprint(self, file_path: str) -> Optional[str]:
        """Generate audio fingerprint for duplicate detection"""
        
        try:
            # Load audio and compute chromagram
            audio, sr = librosa.load(file_path, sr=22050, duration=30)  # First 30 seconds
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            
            # Create simple fingerprint from chroma features
            fingerprint = np.mean(chroma, axis=1)
            
            # Convert to hex string
            fingerprint_bytes = (fingerprint * 255).astype(np.uint8).tobytes()
            fingerprint_hex = fingerprint_bytes.hex()
            
            return fingerprint_hex
            
        except Exception as e:
            logger.error("Audio fingerprinting failed", error=str(e))
            return None