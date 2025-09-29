#!/usr/bin/env python3
"""
Audio Enhancement Module for Arabic STT
Improves audio quality before transcription to increase accuracy
"""

import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from scipy import signal
from scipy.signal import butter, filtfilt, wiener
import tempfile
import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class AudioEnhancer:
    """Advanced audio enhancement for better transcription accuracy"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.target_db = -20.0  # Target RMS level in dB
        
    def enhance_audio(self, audio_path: str, output_path: Optional[str] = None) -> str:
        """
        Complete audio enhancement pipeline
        
        Args:
            audio_path: Path to input audio file
            output_path: Path for enhanced audio (optional)
            
        Returns:
            Path to enhanced audio file
        """
        try:
            logger.info(f"🎵 Enhancing audio: {audio_path}")
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            logger.info(f"📊 Original audio: {len(audio)} samples, {sr} Hz")
            
            # Step 1: Noise reduction
            audio = self._reduce_noise(audio, sr)
            logger.info("✅ Noise reduction applied")
            
            # Step 2: Normalize audio levels
            audio = self._normalize_audio(audio)
            logger.info("✅ Audio normalization applied")
            
            # Step 3: Apply bandpass filter for speech
            audio = self._apply_speech_filter(audio, sr)
            logger.info("✅ Speech filter applied")
            
            # Step 4: Dynamic range compression
            audio = self._compress_dynamic_range(audio)
            logger.info("✅ Dynamic range compression applied")
            
            # Step 5: Remove silence and enhance speech
            audio = self._enhance_speech_segments(audio, sr)
            logger.info("✅ Speech enhancement applied")
            
            # Save enhanced audio
            if output_path is None:
                output_path = tempfile.mktemp(suffix='_enhanced.wav')
            
            sf.write(output_path, audio, sr, subtype='PCM_16')
            logger.info(f"✅ Enhanced audio saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Audio enhancement failed: {e}")
            return audio_path  # Return original if enhancement fails
    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Advanced noise reduction using spectral subtraction"""
        try:
            # Use noisereduce library for spectral subtraction
            # Estimate noise from first 0.5 seconds
            noise_sample_length = min(int(0.5 * sr), len(audio) // 4)
            
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(
                y=audio, 
                sr=sr,
                stationary=False,  # Non-stationary noise reduction
                prop_decrease=0.8,  # Reduce noise by 80%
                n_fft=2048,
                win_length=2048,
                hop_length=512
            )
            
            return reduced_noise
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}, using original audio")
            return audio
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to target RMS level"""
        try:
            # Calculate current RMS
            rms = np.sqrt(np.mean(audio**2))
            
            if rms > 0:
                # Target RMS level (-20 dB)
                target_rms = 10**(self.target_db / 20)
                
                # Apply normalization
                normalized = audio * (target_rms / rms)
                
                # Prevent clipping
                max_val = np.max(np.abs(normalized))
                if max_val > 0.95:
                    normalized = normalized * (0.95 / max_val)
                
                return normalized
            
            return audio
            
        except Exception as e:
            logger.warning(f"Normalization failed: {e}")
            return audio
    
    def _apply_speech_filter(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply bandpass filter optimized for Arabic speech"""
        try:
            # Arabic speech frequency range: 80 Hz - 8000 Hz
            low_freq = 80
            high_freq = min(8000, sr // 2 - 100)  # Avoid Nyquist frequency
            
            # Design Butterworth bandpass filter
            nyquist = sr / 2
            low = low_freq / nyquist
            high = high_freq / nyquist
            
            b, a = butter(4, [low, high], btype='band')
            
            # Apply filter
            filtered = filtfilt(b, a, audio)
            
            return filtered
            
        except Exception as e:
            logger.warning(f"Speech filter failed: {e}")
            return audio
    
    def _compress_dynamic_range(self, audio: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression to even out volume levels"""
        try:
            # Simple compressor using tanh function
            threshold = 0.3
            ratio = 4.0
            
            # Apply compression
            compressed = np.where(
                np.abs(audio) > threshold,
                np.sign(audio) * (threshold + (np.abs(audio) - threshold) / ratio),
                audio
            )
            
            # Smooth the result
            compressed = np.tanh(compressed * 0.8) * 0.9
            
            return compressed
            
        except Exception as e:
            logger.warning(f"Dynamic range compression failed: {e}")
            return audio
    
    def _enhance_speech_segments(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Enhance speech segments and reduce silence"""
        try:
            # Voice Activity Detection
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)    # 10ms hop
            
            # Calculate energy-based VAD
            frames = librosa.util.frame(audio, frame_length=frame_length, 
                                      hop_length=hop_length, axis=0)
            energy = np.sum(frames**2, axis=0)
            
            # Adaptive threshold
            energy_threshold = np.percentile(energy, 30)  # 30th percentile
            
            # Identify speech segments
            speech_mask = energy > energy_threshold
            
            # Expand speech regions slightly
            kernel_size = 5
            speech_mask = signal.medfilt(speech_mask.astype(float), kernel_size) > 0.5
            
            # Apply enhancement only to speech segments
            enhanced = audio.copy()
            
            for i, is_speech in enumerate(speech_mask):
                start_sample = i * hop_length
                end_sample = min(start_sample + hop_length, len(audio))
                
                if is_speech and start_sample < len(audio):
                    # Enhance speech segments
                    segment = audio[start_sample:end_sample]
                    
                    # Apply mild amplification to speech
                    enhanced[start_sample:end_sample] = segment * 1.2
                else:
                    # Reduce non-speech segments
                    enhanced[start_sample:end_sample] *= 0.3
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Speech enhancement failed: {e}")
            return audio
    
    def assess_audio_quality(self, audio_path: str) -> dict:
        """Assess audio quality metrics"""
        try:
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # Calculate quality metrics
            rms = np.sqrt(np.mean(audio**2))
            peak = np.max(np.abs(audio))
            
            # Signal-to-noise ratio estimation
            # Use spectral subtraction approach
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            
            # Estimate noise floor (bottom 10% of magnitudes)
            noise_floor = np.percentile(magnitude, 10)
            signal_power = np.mean(magnitude)
            
            snr_estimate = 20 * np.log10(signal_power / (noise_floor + 1e-10))
            
            # Dynamic range
            dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
            
            # Spectral centroid (brightness)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
            
            quality_metrics = {
                'rms_level': float(rms),
                'peak_level': float(peak),
                'rms_db': float(20 * np.log10(rms + 1e-10)),
                'peak_db': float(20 * np.log10(peak + 1e-10)),
                'estimated_snr': float(snr_estimate),
                'dynamic_range': float(dynamic_range),
                'spectral_centroid': float(spectral_centroid),
                'duration': float(len(audio) / sr),
                'sample_rate': int(sr)
            }
            
            # Quality assessment
            quality_score = self._calculate_quality_score(quality_metrics)
            quality_metrics['quality_score'] = quality_score
            quality_metrics['quality_rating'] = self._get_quality_rating(quality_score)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {'error': str(e)}
    
    def _calculate_quality_score(self, metrics: dict) -> float:
        """Calculate overall quality score (0-100)"""
        score = 50  # Base score
        
        # SNR contribution (0-30 points)
        snr = metrics.get('estimated_snr', 0)
        if snr > 20:
            score += 30
        elif snr > 10:
            score += 20
        elif snr > 5:
            score += 10
        
        # RMS level contribution (0-20 points)
        rms_db = metrics.get('rms_db', -60)
        if -25 <= rms_db <= -15:  # Optimal range
            score += 20
        elif -35 <= rms_db <= -10:  # Good range
            score += 15
        elif -45 <= rms_db <= -5:   # Acceptable range
            score += 10
        
        return min(100, max(0, score))
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert quality score to rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 35:
            return "Poor"
        else:
            return "Very Poor"

# Example usage
if __name__ == "__main__":
    enhancer = AudioEnhancer()
    
    # Test with an audio file
    test_file = "test_audio.wav"
    if os.path.exists(test_file):
        # Assess original quality
        original_quality = enhancer.assess_audio_quality(test_file)
        print(f"Original quality: {original_quality}")
        
        # Enhance audio
        enhanced_file = enhancer.enhance_audio(test_file)
        
        # Assess enhanced quality
        enhanced_quality = enhancer.assess_audio_quality(enhanced_file)
        print(f"Enhanced quality: {enhanced_quality}")
    else:
        print("No test audio file found")