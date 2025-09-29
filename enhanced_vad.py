#!/usr/bin/env python3
"""
Enhanced Voice Activity Detection (VAD) for Arabic Speech
Provides advanced silence detection and speech segmentation
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.signal import butter, filtfilt
import logging
from typing import List, Tuple, Dict, Optional
import tempfile

logger = logging.getLogger(__name__)

class EnhancedVAD:
    """Enhanced Voice Activity Detection optimized for Arabic speech"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.frame_length = int(0.025 * sample_rate)  # 25ms frames
        self.hop_length = int(0.010 * sample_rate)    # 10ms hop
        self.min_speech_duration = 0.3  # Minimum speech segment duration (seconds)
        self.min_silence_duration = 0.2  # Minimum silence duration (seconds)
        
    def detect_speech_segments(self, audio_path: str) -> List[Dict]:
        """
        Detect speech segments in audio using advanced VAD
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of speech segments with start/end times and confidence
        """
        try:
            logger.info(f"🎤 Analyzing speech segments in: {audio_path}")
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # Multi-feature VAD
            energy_vad = self._energy_based_vad(audio)
            spectral_vad = self._spectral_based_vad(audio, sr)
            zero_crossing_vad = self._zero_crossing_vad(audio)
            
            # Combine VAD features
            combined_vad = self._combine_vad_features(energy_vad, spectral_vad, zero_crossing_vad)
            
            # Post-process to get clean segments
            speech_segments = self._post_process_vad(combined_vad, audio, sr)
            
            logger.info(f"✅ Detected {len(speech_segments)} speech segments")
            return speech_segments
            
        except Exception as e:
            logger.error(f"❌ VAD analysis failed: {e}")
            return []
    
    def _energy_based_vad(self, audio: np.ndarray) -> np.ndarray:
        """Energy-based voice activity detection"""
        try:
            # Frame the audio
            frames = librosa.util.frame(audio, frame_length=self.frame_length, 
                                      hop_length=self.hop_length, axis=0)
            
            # Calculate RMS energy for each frame
            energy = np.sqrt(np.mean(frames**2, axis=0))
            
            # Adaptive threshold using percentiles
            energy_threshold = np.percentile(energy, 25)  # 25th percentile as noise floor
            dynamic_threshold = energy_threshold + 0.3 * (np.max(energy) - energy_threshold)
            
            # Voice activity detection
            vad = energy > dynamic_threshold
            
            return vad.astype(float)
            
        except Exception as e:
            logger.warning(f"Energy VAD failed: {e}")
            return np.ones(len(audio) // self.hop_length)
    
    def _spectral_based_vad(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Spectral-based voice activity detection"""
        try:
            # Compute STFT
            stft = librosa.stft(audio, n_fft=512, hop_length=self.hop_length, 
                              win_length=self.frame_length)
            magnitude = np.abs(stft)
            
            # Spectral centroid (brightness indicator)
            spectral_centroid = librosa.feature.spectral_centroid(
                S=magnitude, sr=sr, hop_length=self.hop_length)[0]
            
            # Spectral rolloff (energy distribution)
            spectral_rolloff = librosa.feature.spectral_rolloff(
                S=magnitude, sr=sr, hop_length=self.hop_length, roll_percent=0.85)[0]
            
            # Spectral flux (change in spectrum)
            spectral_flux = np.diff(magnitude, axis=1)
            spectral_flux = np.sum(np.abs(spectral_flux), axis=0)
            spectral_flux = np.pad(spectral_flux, (1, 0), mode='constant')
            
            # Combine spectral features
            # Arabic speech typically has centroid between 1000-3000 Hz
            centroid_score = np.where(
                (spectral_centroid > 800) & (spectral_centroid < 4000), 1.0, 0.3
            )
            
            # High rolloff indicates speech
            rolloff_score = np.where(spectral_rolloff > sr * 0.1, 1.0, 0.2)
            
            # Normalize spectral flux
            flux_normalized = spectral_flux / (np.max(spectral_flux) + 1e-10)
            flux_score = np.where(flux_normalized > 0.1, 1.0, 0.3)
            
            # Combine scores
            spectral_vad = (centroid_score + rolloff_score + flux_score) / 3.0
            
            # Threshold
            spectral_vad = (spectral_vad > 0.6).astype(float)
            
            return spectral_vad
            
        except Exception as e:
            logger.warning(f"Spectral VAD failed: {e}")
            return np.ones(len(audio) // self.hop_length)
    
    def _zero_crossing_vad(self, audio: np.ndarray) -> np.ndarray:
        """Zero-crossing rate based VAD"""
        try:
            # Frame the audio
            frames = librosa.util.frame(audio, frame_length=self.frame_length, 
                                      hop_length=self.hop_length, axis=0)
            
            # Calculate zero crossing rate for each frame
            zcr = []
            for frame in frames.T:
                # Count zero crossings
                zero_crossings = np.sum(np.diff(np.sign(frame)) != 0)
                zcr.append(zero_crossings / len(frame))
            
            zcr = np.array(zcr)
            
            # Arabic speech typically has moderate ZCR (0.05-0.3)
            # Too low = silence, too high = noise
            zcr_vad = np.where((zcr > 0.02) & (zcr < 0.4), 1.0, 0.0)
            
            return zcr_vad
            
        except Exception as e:
            logger.warning(f"ZCR VAD failed: {e}")
            return np.ones(len(audio) // self.hop_length)
    
    def _combine_vad_features(self, energy_vad: np.ndarray, spectral_vad: np.ndarray, 
                            zcr_vad: np.ndarray) -> np.ndarray:
        """Combine multiple VAD features using weighted voting"""
        try:
            # Ensure all arrays have the same length
            min_length = min(len(energy_vad), len(spectral_vad), len(zcr_vad))
            energy_vad = energy_vad[:min_length]
            spectral_vad = spectral_vad[:min_length]
            zcr_vad = zcr_vad[:min_length]
            
            # Weighted combination (energy is most reliable for Arabic)
            weights = [0.5, 0.3, 0.2]  # energy, spectral, zcr
            combined = (weights[0] * energy_vad + 
                       weights[1] * spectral_vad + 
                       weights[2] * zcr_vad)
            
            # Threshold for final decision
            vad_result = (combined > 0.4).astype(float)
            
            return vad_result
            
        except Exception as e:
            logger.warning(f"VAD combination failed: {e}")
            return energy_vad  # Fallback to energy VAD
    
    def _post_process_vad(self, vad: np.ndarray, audio: np.ndarray, sr: int) -> List[Dict]:
        """Post-process VAD results to get clean speech segments"""
        try:
            # Apply median filter to smooth VAD decisions
            vad_smooth = signal.medfilt(vad, kernel_size=5)
            
            # Find speech segments
            speech_frames = np.where(vad_smooth > 0.5)[0]
            
            if len(speech_frames) == 0:
                return []
            
            # Group consecutive frames into segments
            segments = []
            segment_start = speech_frames[0]
            
            for i in range(1, len(speech_frames)):
                # If gap is too large, end current segment and start new one
                if speech_frames[i] - speech_frames[i-1] > self.min_silence_duration * sr / self.hop_length:
                    segment_end = speech_frames[i-1]
                    segments.append((segment_start, segment_end))
                    segment_start = speech_frames[i]
            
            # Add the last segment
            segments.append((segment_start, speech_frames[-1]))
            
            # Convert frame indices to time and filter by duration
            speech_segments = []
            for start_frame, end_frame in segments:
                start_time = start_frame * self.hop_length / sr
                end_time = end_frame * self.hop_length / sr
                duration = end_time - start_time
                
                # Filter out very short segments
                if duration >= self.min_speech_duration:
                    # Calculate confidence based on VAD strength in segment
                    segment_vad = vad_smooth[start_frame:end_frame+1]
                    confidence = np.mean(segment_vad)
                    
                    # Calculate additional quality metrics
                    start_sample = int(start_time * sr)
                    end_sample = int(end_time * sr)
                    segment_audio = audio[start_sample:end_sample]
                    
                    # RMS energy of segment
                    rms = np.sqrt(np.mean(segment_audio**2))
                    
                    speech_segments.append({
                        'start': round(start_time, 3),
                        'end': round(end_time, 3),
                        'duration': round(duration, 3),
                        'confidence': round(confidence, 3),
                        'rms_energy': round(float(rms), 4),
                        'quality_score': self._calculate_segment_quality(segment_audio, sr)
                    })
            
            return speech_segments
            
        except Exception as e:
            logger.warning(f"VAD post-processing failed: {e}")
            return []
    
    def _calculate_segment_quality(self, segment_audio: np.ndarray, sr: int) -> float:
        """Calculate quality score for a speech segment"""
        try:
            if len(segment_audio) == 0:
                return 0.0
            
            # RMS energy (normalized)
            rms = np.sqrt(np.mean(segment_audio**2))
            energy_score = min(1.0, rms * 10)  # Scale to 0-1
            
            # Spectral centroid (speech-like frequency distribution)
            if len(segment_audio) > 512:
                centroid = np.mean(librosa.feature.spectral_centroid(y=segment_audio, sr=sr))
                # Arabic speech centroid typically 1000-3000 Hz
                if 1000 <= centroid <= 3000:
                    centroid_score = 1.0
                elif 500 <= centroid <= 4000:
                    centroid_score = 0.7
                else:
                    centroid_score = 0.3
            else:
                centroid_score = 0.5
            
            # Dynamic range
            peak = np.max(np.abs(segment_audio))
            if peak > 0:
                dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
                range_score = min(1.0, max(0.0, (dynamic_range - 5) / 15))  # 5-20 dB range
            else:
                range_score = 0.0
            
            # Combine scores
            quality_score = (energy_score * 0.4 + centroid_score * 0.4 + range_score * 0.2)
            
            return round(quality_score, 3)
            
        except Exception as e:
            logger.warning(f"Quality calculation failed: {e}")
            return 0.5
    
    def apply_vad_to_audio(self, audio_path: str, output_path: Optional[str] = None) -> str:
        """Apply VAD to remove silence and keep only speech segments"""
        try:
            logger.info(f"🎤 Applying VAD to: {audio_path}")
            
            # Detect speech segments
            segments = self.detect_speech_segments(audio_path)
            
            if not segments:
                logger.warning("No speech segments detected")
                return audio_path
            
            # Load original audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # Extract and concatenate speech segments
            speech_audio = []
            for segment in segments:
                start_sample = int(segment['start'] * sr)
                end_sample = int(segment['end'] * sr)
                speech_audio.append(audio[start_sample:end_sample])
                
                # Add small silence between segments (100ms)
                silence_samples = int(0.1 * sr)
                speech_audio.append(np.zeros(silence_samples))
            
            # Concatenate all speech segments
            if speech_audio:
                processed_audio = np.concatenate(speech_audio)
                
                # Save processed audio
                if output_path is None:
                    output_path = tempfile.mktemp(suffix='_vad_processed.wav')
                
                sf.write(output_path, processed_audio, sr, subtype='PCM_16')
                
                original_duration = len(audio) / sr
                processed_duration = len(processed_audio) / sr
                compression_ratio = processed_duration / original_duration
                
                logger.info(f"✅ VAD processing complete:")
                logger.info(f"   Original duration: {original_duration:.2f}s")
                logger.info(f"   Processed duration: {processed_duration:.2f}s")
                logger.info(f"   Compression ratio: {compression_ratio:.2f}")
                logger.info(f"   Speech segments: {len(segments)}")
                
                return output_path
            else:
                logger.warning("No speech audio extracted")
                return audio_path
                
        except Exception as e:
            logger.error(f"❌ VAD processing failed: {e}")
            return audio_path
    
    def get_vad_parameters_for_whisper(self, audio_path: str) -> Dict:
        """Get optimized VAD parameters for Whisper based on audio analysis"""
        try:
            segments = self.detect_speech_segments(audio_path)
            
            if not segments:
                # Default parameters for poor quality audio
                return {
                    'vad_filter': True,
                    'vad_parameters': {
                        'min_silence_duration_ms': 800,
                        'speech_pad_ms': 400,
                        'max_speech_duration_s': 30
                    }
                }
            
            # Analyze segment characteristics
            durations = [seg['duration'] for seg in segments]
            confidences = [seg['confidence'] for seg in segments]
            
            avg_duration = np.mean(durations)
            avg_confidence = np.mean(confidences)
            
            # Adaptive parameters based on analysis
            if avg_confidence > 0.8 and avg_duration > 2.0:
                # High quality, longer segments
                min_silence = 300
                speech_pad = 200
            elif avg_confidence > 0.6:
                # Medium quality
                min_silence = 500
                speech_pad = 300
            else:
                # Lower quality, more aggressive filtering
                min_silence = 800
                speech_pad = 400
            
            return {
                'vad_filter': True,
                'vad_parameters': {
                    'min_silence_duration_ms': min_silence,
                    'speech_pad_ms': speech_pad,
                    'max_speech_duration_s': min(30, max(10, avg_duration * 2))
                }
            }
            
        except Exception as e:
            logger.warning(f"VAD parameter optimization failed: {e}")
            return {
                'vad_filter': True,
                'vad_parameters': {
                    'min_silence_duration_ms': 500,
                    'speech_pad_ms': 300,
                    'max_speech_duration_s': 30
                }
            }

# Example usage
if __name__ == "__main__":
    vad = EnhancedVAD()
    
    # Test with an audio file
    test_file = "test_audio.wav"
    if os.path.exists(test_file):
        # Detect speech segments
        segments = vad.detect_speech_segments(test_file)
        print(f"Detected segments: {segments}")
        
        # Apply VAD processing
        processed_file = vad.apply_vad_to_audio(test_file)
        print(f"Processed audio: {processed_file}")
        
        # Get Whisper parameters
        whisper_params = vad.get_vad_parameters_for_whisper(test_file)
        print(f"Whisper VAD parameters: {whisper_params}")
    else:
        print("No test audio file found")