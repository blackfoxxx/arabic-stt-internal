#!/usr/bin/env python3
"""
Advanced Acoustic Analysis Module
Integrates praat-parselmouth, pyAudioAnalysis, and openSMILE
for comprehensive voice feature extraction and analysis
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

try:
    import parselmouth
    from parselmouth.praat import call
    PRAAT_AVAILABLE = True
except ImportError:
    PRAAT_AVAILABLE = False
    print("⚠️ praat-parselmouth not available. Install with: pip install praat-parselmouth")

try:
    import pyAudioAnalysis.audioBasicIO as audioBasicIO
    import pyAudioAnalysis.ShortTermFeatures as ShortTermFeatures
    import pyAudioAnalysis.MidTermFeatures as MidTermFeatures
    PYAUDIO_AVAILABLE = True
except ImportError:
    try:
        from pyAudioAnalysis import audioBasicIO
        from pyAudioAnalysis import ShortTermFeatures
        from pyAudioAnalysis import MidTermFeatures
        PYAUDIO_AVAILABLE = True
    except ImportError:
        PYAUDIO_AVAILABLE = False
        print("⚠️ pyAudioAnalysis not available. Install with: pip install pyAudioAnalysis")

try:
    import opensmile
    OPENSMILE_AVAILABLE = True
except ImportError:
    OPENSMILE_AVAILABLE = False
    print("⚠️ openSMILE not available. Install with: pip install opensmile")

@dataclass
class ProsodyFeatures:
    """Prosodic features from Praat analysis"""
    mean_f0: float
    std_f0: float
    min_f0: float
    max_f0: float
    f0_range: float
    jitter: float
    shimmer: float
    hnr: float  # Harmonics-to-Noise Ratio
    speaking_rate: float
    pause_duration: float
    voice_breaks: int
    intensity_mean: float
    intensity_std: float
    formant_f1_mean: float
    formant_f2_mean: float
    formant_f3_mean: float

@dataclass
class SpectralFeatures:
    """Spectral features from pyAudioAnalysis"""
    mfcc_mean: List[float]
    mfcc_std: List[float]
    spectral_centroid: float
    spectral_rolloff: float
    spectral_flux: float
    zero_crossing_rate: float
    energy: float
    entropy_of_energy: float
    chroma_vector: List[float]
    chroma_deviation: float

@dataclass
class OpenSMILEFeatures:
    """Features from openSMILE toolkit"""
    egemaps_features: Dict[str, float]
    compare_features: Dict[str, float]
    emotion_features: Dict[str, float]
    voice_quality_features: Dict[str, float]

@dataclass
class VoiceStressIndicators:
    """Voice stress and emotion indicators"""
    stress_level: float  # 0-1
    emotional_arousal: float  # 0-1
    valence: float  # -1 to 1 (negative to positive)
    voice_tension: float  # 0-1
    breathing_irregularity: float  # 0-1
    micro_tremor: float  # 0-1
    vocal_effort: float  # 0-1

@dataclass
class DeceptionAcousticMarkers:
    """Acoustic markers potentially indicating deception"""
    pitch_variability_score: float
    voice_quality_degradation: float
    hesitation_markers: float
    speech_rate_changes: float
    vocal_tension_score: float
    confidence_score: float  # Overall confidence in deception detection

@dataclass
class AcousticAnalysisResult:
    """Complete acoustic analysis result"""
    prosody_features: Optional[ProsodyFeatures]
    spectral_features: Optional[SpectralFeatures]
    opensmile_features: Optional[OpenSMILEFeatures]
    stress_indicators: VoiceStressIndicators
    deception_markers: DeceptionAcousticMarkers
    overall_voice_quality: float
    emotional_state_acoustic: Dict[str, float]
    processing_time: float
    features_extracted: List[str]

class AcousticAnalyzer:
    """Advanced acoustic analysis using multiple libraries"""
    
    def __init__(self):
        self.praat_available = PRAAT_AVAILABLE
        self.pyaudio_available = PYAUDIO_AVAILABLE
        self.opensmile_available = OPENSMILE_AVAILABLE
        
        # Initialize openSMILE if available
        if self.opensmile_available:
            try:
                self.smile_egemaps = opensmile.Smile(
                    feature_set=opensmile.FeatureSet.eGeMAPSv02,
                    feature_level=opensmile.FeatureLevel.Functionals,
                )
                self.smile_compare = opensmile.Smile(
                    feature_set=opensmile.FeatureSet.ComParE_2016,
                    feature_level=opensmile.FeatureLevel.Functionals,
                )
            except Exception as e:
                print(f"⚠️ openSMILE initialization failed: {e}")
                self.opensmile_available = False
    
    def extract_praat_features(self, audio_path: str) -> Optional[ProsodyFeatures]:
        """Extract prosodic features using Praat-Parselmouth"""
        if not self.praat_available:
            return None
        
        try:
            # Load audio
            sound = parselmouth.Sound(audio_path)
            
            # Extract pitch
            pitch = sound.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500)
            
            # Extract formants
            formant = sound.to_formant_burg(time_step=0.01, max_number_of_formants=5,
                                          maximum_formant=5500, window_length=0.025)
            
            # Extract intensity
            intensity = sound.to_intensity(time_step=0.01)
            
            # Pitch statistics
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values != 0]  # Remove unvoiced frames
            
            if len(pitch_values) > 0:
                mean_f0 = np.mean(pitch_values)
                std_f0 = np.std(pitch_values)
                min_f0 = np.min(pitch_values)
                max_f0 = np.max(pitch_values)
                f0_range = max_f0 - min_f0
            else:
                mean_f0 = std_f0 = min_f0 = max_f0 = f0_range = 0.0
            
            # Voice quality measures
            try:
                jitter = call(pitch, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
                shimmer = call([sound, pitch], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
                hnr = call(sound, "Get harmonicity (cc)", 0.01, 75, 0.1, 1.0)
            except:
                jitter = shimmer = hnr = 0.0
            
            # Speaking rate and pauses
            textgrid = call(sound, "To TextGrid (silences)", 100, 0.0, -25.0, 0.1, 0.1, "silent", "sounding")
            total_duration = sound.get_total_duration()
            
            # Count voice breaks and calculate speaking rate
            voice_breaks = 0
            pause_duration = 0.0
            speaking_rate = 0.0
            
            try:
                silence_tier = call(textgrid, "Extract tier", 1)
                num_intervals = call(silence_tier, "Get number of intervals")
                
                for i in range(1, num_intervals + 1):
                    label = call(silence_tier, "Get label of interval", i)
                    if label == "silent":
                        start = call(silence_tier, "Get start time of interval", i)
                        end = call(silence_tier, "Get end time of interval", i)
                        pause_duration += (end - start)
                        voice_breaks += 1
                
                speaking_duration = total_duration - pause_duration
                if speaking_duration > 0:
                    # Estimate syllables (rough approximation)
                    speaking_rate = len(pitch_values) / speaking_duration * 0.1  # Rough syllables per second
            except:
                pass
            
            # Intensity statistics
            intensity_values = intensity.values.T
            intensity_mean = np.mean(intensity_values) if len(intensity_values) > 0 else 0.0
            intensity_std = np.std(intensity_values) if len(intensity_values) > 0 else 0.0
            
            # Formant statistics
            try:
                f1_values = []
                f2_values = []
                f3_values = []
                
                for t in np.arange(0, total_duration, 0.01):
                    f1 = call(formant, "Get value at time", 1, t, "Hertz", "Linear")
                    f2 = call(formant, "Get value at time", 2, t, "Hertz", "Linear")
                    f3 = call(formant, "Get value at time", 3, t, "Hertz", "Linear")
                    
                    if not np.isnan(f1): f1_values.append(f1)
                    if not np.isnan(f2): f2_values.append(f2)
                    if not np.isnan(f3): f3_values.append(f3)
                
                formant_f1_mean = np.mean(f1_values) if f1_values else 0.0
                formant_f2_mean = np.mean(f2_values) if f2_values else 0.0
                formant_f3_mean = np.mean(f3_values) if f3_values else 0.0
            except:
                formant_f1_mean = formant_f2_mean = formant_f3_mean = 0.0
            
            return ProsodyFeatures(
                mean_f0=mean_f0,
                std_f0=std_f0,
                min_f0=min_f0,
                max_f0=max_f0,
                f0_range=f0_range,
                jitter=jitter,
                shimmer=shimmer,
                hnr=hnr,
                speaking_rate=speaking_rate,
                pause_duration=pause_duration,
                voice_breaks=voice_breaks,
                intensity_mean=intensity_mean,
                intensity_std=intensity_std,
                formant_f1_mean=formant_f1_mean,
                formant_f2_mean=formant_f2_mean,
                formant_f3_mean=formant_f3_mean
            )
            
        except Exception as e:
            print(f"Error in Praat analysis: {e}")
            return None
    
    def extract_pyaudio_features(self, audio_path: str) -> Optional[SpectralFeatures]:
        """Extract spectral features using pyAudioAnalysis"""
        if not self.pyaudio_available:
            return None
        
        try:
            # Load audio
            sampling_rate, signal = audioBasicIO.read_audio_file(audio_path)
            
            # Convert to mono if stereo
            if signal.ndim > 1:
                signal = np.mean(signal, axis=1)
            
            # Extract short-term features
            st_features, _ = ShortTermFeatures.feature_extraction(
                signal, sampling_rate, 0.050 * sampling_rate, 0.025 * sampling_rate
            )
            
            # Calculate statistics
            mfcc_mean = np.mean(st_features[1:14], axis=1).tolist()  # MFCC coefficients
            mfcc_std = np.std(st_features[1:14], axis=1).tolist()
            
            spectral_centroid = np.mean(st_features[0])  # Zero crossing rate
            spectral_rolloff = np.mean(st_features[27])  # Spectral rolloff
            spectral_flux = np.mean(st_features[28])  # Spectral flux
            zero_crossing_rate = np.mean(st_features[0])
            energy = np.mean(st_features[1])
            entropy_of_energy = np.mean(st_features[2])
            
            # Chroma features
            chroma_vector = np.mean(st_features[14:26], axis=1).tolist()  # Chroma vector
            chroma_deviation = np.std(st_features[14:26])
            
            return SpectralFeatures(
                mfcc_mean=mfcc_mean,
                mfcc_std=mfcc_std,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                spectral_flux=spectral_flux,
                zero_crossing_rate=zero_crossing_rate,
                energy=energy,
                entropy_of_energy=entropy_of_energy,
                chroma_vector=chroma_vector,
                chroma_deviation=chroma_deviation
            )
            
        except Exception as e:
            print(f"Error in pyAudioAnalysis: {e}")
            return None
    
    def extract_opensmile_features(self, audio_path: str) -> Optional[OpenSMILEFeatures]:
        """Extract features using openSMILE"""
        if not self.opensmile_available:
            return None
        
        try:
            # Extract eGeMAPS features
            egemaps_df = self.smile_egemaps.process_file(audio_path)
            egemaps_features = egemaps_df.iloc[0].to_dict()
            
            # Extract ComParE features
            compare_df = self.smile_compare.process_file(audio_path)
            compare_features = compare_df.iloc[0].to_dict()
            
            # Extract emotion-related features
            emotion_features = {}
            voice_quality_features = {}
            
            # Map specific features to emotion and voice quality
            for key, value in egemaps_features.items():
                if any(emotion_key in key.lower() for emotion_key in ['f0', 'jitter', 'shimmer']):
                    emotion_features[key] = value
                if any(quality_key in key.lower() for quality_key in ['hnr', 'spectral', 'mfcc']):
                    voice_quality_features[key] = value
            
            return OpenSMILEFeatures(
                egemaps_features=egemaps_features,
                compare_features=compare_features,
                emotion_features=emotion_features,
                voice_quality_features=voice_quality_features
            )
            
        except Exception as e:
            print(f"Error in openSMILE analysis: {e}")
            return None
    
    def calculate_stress_indicators(self, prosody: Optional[ProsodyFeatures],
                                  spectral: Optional[SpectralFeatures],
                                  opensmile: Optional[OpenSMILEFeatures]) -> VoiceStressIndicators:
        """Calculate voice stress indicators from acoustic features"""
        
        # Initialize with default values
        stress_level = 0.0
        emotional_arousal = 0.0
        valence = 0.0
        voice_tension = 0.0
        breathing_irregularity = 0.0
        micro_tremor = 0.0
        vocal_effort = 0.0
        
        if prosody:
            # Stress indicators from prosody
            # High F0 variability can indicate stress
            if prosody.mean_f0 > 0:
                f0_cv = prosody.std_f0 / prosody.mean_f0  # Coefficient of variation
                stress_level += min(f0_cv * 2, 1.0) * 0.3
            
            # High jitter and shimmer indicate voice tension
            voice_tension += min(prosody.jitter * 100, 1.0) * 0.4
            voice_tension += min(prosody.shimmer * 50, 1.0) * 0.4
            
            # Low HNR indicates voice quality issues
            if prosody.hnr < 15:  # Normal HNR is typically > 15 dB
                voice_tension += (15 - prosody.hnr) / 15 * 0.2
            
            # Speaking rate changes
            if prosody.speaking_rate > 6 or prosody.speaking_rate < 2:  # Normal: 2-6 syllables/sec
                stress_level += 0.2
            
            # Voice breaks indicate breathing irregularity
            if prosody.voice_breaks > 2:
                breathing_irregularity += min(prosody.voice_breaks / 10, 1.0)
            
            # Emotional arousal from F0 range and intensity
            if prosody.f0_range > 100:  # Wide F0 range indicates high arousal
                emotional_arousal += min(prosody.f0_range / 200, 1.0) * 0.5
            
            if prosody.intensity_std > 5:  # High intensity variation
                emotional_arousal += min(prosody.intensity_std / 10, 1.0) * 0.3
            
            # Valence estimation (rough approximation)
            # Higher mean F0 and formants might indicate positive valence
            if prosody.mean_f0 > 150 and prosody.formant_f2_mean > 1500:
                valence += 0.3
            elif prosody.mean_f0 < 120:
                valence -= 0.3
        
        if spectral:
            # Spectral indicators of stress
            # High spectral centroid can indicate tension
            if spectral.spectral_centroid > 2000:
                voice_tension += min((spectral.spectral_centroid - 2000) / 2000, 1.0) * 0.3
            
            # Energy variations
            vocal_effort += min(spectral.energy / 0.1, 1.0) * 0.4
            
            # MFCC variations for micro-tremor detection
            mfcc_variation = np.mean(spectral.mfcc_std) if spectral.mfcc_std else 0
            micro_tremor += min(mfcc_variation * 10, 1.0)
        
        if opensmile:
            # Use openSMILE emotion features if available
            egemaps = opensmile.egemaps_features
            
            # Look for specific arousal and valence indicators
            for key, value in egemaps.items():
                if 'arousal' in key.lower():
                    emotional_arousal = max(emotional_arousal, min(abs(value), 1.0))
                elif 'valence' in key.lower():
                    valence = max(valence, min(value, 1.0)) if value > 0 else min(valence, max(value, -1.0))
        
        # Normalize values to 0-1 range (except valence which is -1 to 1)
        stress_level = min(max(stress_level, 0.0), 1.0)
        emotional_arousal = min(max(emotional_arousal, 0.0), 1.0)
        valence = min(max(valence, -1.0), 1.0)
        voice_tension = min(max(voice_tension, 0.0), 1.0)
        breathing_irregularity = min(max(breathing_irregularity, 0.0), 1.0)
        micro_tremor = min(max(micro_tremor, 0.0), 1.0)
        vocal_effort = min(max(vocal_effort, 0.0), 1.0)
        
        return VoiceStressIndicators(
            stress_level=stress_level,
            emotional_arousal=emotional_arousal,
            valence=valence,
            voice_tension=voice_tension,
            breathing_irregularity=breathing_irregularity,
            micro_tremor=micro_tremor,
            vocal_effort=vocal_effort
        )
    
    def detect_deception_markers(self, prosody: Optional[ProsodyFeatures],
                               spectral: Optional[SpectralFeatures],
                               stress: VoiceStressIndicators) -> DeceptionAcousticMarkers:
        """Detect acoustic markers potentially indicating deception"""
        
        pitch_variability_score = 0.0
        voice_quality_degradation = 0.0
        hesitation_markers = 0.0
        speech_rate_changes = 0.0
        vocal_tension_score = 0.0
        
        if prosody:
            # Pitch variability (deception often shows increased F0 variability)
            if prosody.mean_f0 > 0:
                pitch_variability_score = min(prosody.std_f0 / prosody.mean_f0 * 3, 1.0)
            
            # Voice quality degradation
            voice_quality_degradation = min(prosody.jitter * 50 + prosody.shimmer * 25, 1.0)
            if prosody.hnr < 12:  # Lower HNR threshold for deception
                voice_quality_degradation += (12 - prosody.hnr) / 12 * 0.5
            
            # Hesitation markers (pauses and voice breaks)
            if prosody.pause_duration > 0.5:  # More than 0.5s total pause time
                hesitation_markers += min(prosody.pause_duration / 2.0, 1.0) * 0.6
            
            hesitation_markers += min(prosody.voice_breaks / 5, 1.0) * 0.4
            
            # Speech rate changes (deception often shows rate variations)
            if prosody.speaking_rate < 2 or prosody.speaking_rate > 7:
                speech_rate_changes = 0.7
            elif prosody.speaking_rate < 3 or prosody.speaking_rate > 5:
                speech_rate_changes = 0.4
        
        # Vocal tension from stress indicators
        vocal_tension_score = stress.voice_tension
        
        # Overall confidence in deception detection
        # Higher scores in multiple markers increase confidence
        marker_scores = [
            pitch_variability_score,
            voice_quality_degradation,
            hesitation_markers,
            speech_rate_changes,
            vocal_tension_score
        ]
        
        # Confidence based on consistency across markers
        high_markers = sum(1 for score in marker_scores if score > 0.6)
        medium_markers = sum(1 for score in marker_scores if 0.3 < score <= 0.6)
        
        if high_markers >= 3:
            confidence_score = 0.8
        elif high_markers >= 2 or (high_markers >= 1 and medium_markers >= 2):
            confidence_score = 0.6
        elif high_markers >= 1 or medium_markers >= 3:
            confidence_score = 0.4
        else:
            confidence_score = 0.2
        
        return DeceptionAcousticMarkers(
            pitch_variability_score=pitch_variability_score,
            voice_quality_degradation=voice_quality_degradation,
            hesitation_markers=hesitation_markers,
            speech_rate_changes=speech_rate_changes,
            vocal_tension_score=vocal_tension_score,
            confidence_score=confidence_score
        )
    
    def analyze_audio(self, audio_path: str) -> AcousticAnalysisResult:
        """Perform comprehensive acoustic analysis"""
        start_time = time.time()
        
        print(f"🎵 Starting acoustic analysis of: {audio_path}")
        
        features_extracted = []
        
        # Extract Praat features
        print("🔊 Extracting prosodic features with Praat...")
        prosody_features = self.extract_praat_features(audio_path)
        if prosody_features:
            features_extracted.append("Praat-Prosody")
        
        # Extract pyAudioAnalysis features
        print("📊 Extracting spectral features with pyAudioAnalysis...")
        spectral_features = self.extract_pyaudio_features(audio_path)
        if spectral_features:
            features_extracted.append("pyAudioAnalysis-Spectral")
        
        # Extract openSMILE features
        print("🎛️ Extracting openSMILE features...")
        opensmile_features = self.extract_opensmile_features(audio_path)
        if opensmile_features:
            features_extracted.append("openSMILE")
        
        # Calculate stress indicators
        print("😰 Calculating stress indicators...")
        stress_indicators = self.calculate_stress_indicators(
            prosody_features, spectral_features, opensmile_features
        )
        
        # Detect deception markers
        print("🕵️ Detecting deception markers...")
        deception_markers = self.detect_deception_markers(
            prosody_features, spectral_features, stress_indicators
        )
        
        # Calculate overall voice quality
        voice_quality = 1.0
        if prosody_features:
            # Base quality on HNR, jitter, and shimmer
            hnr_quality = min(prosody_features.hnr / 20, 1.0) if prosody_features.hnr > 0 else 0.5
            jitter_quality = max(0, 1.0 - prosody_features.jitter * 100)
            shimmer_quality = max(0, 1.0 - prosody_features.shimmer * 50)
            voice_quality = (hnr_quality + jitter_quality + shimmer_quality) / 3
        
        # Estimate emotional state from acoustic features
        emotional_state_acoustic = {
            'arousal': stress_indicators.emotional_arousal,
            'valence': (stress_indicators.valence + 1) / 2,  # Convert to 0-1 scale
            'dominance': 1.0 - stress_indicators.stress_level,  # Inverse of stress
            'tension': stress_indicators.voice_tension,
            'effort': stress_indicators.vocal_effort
        }
        
        processing_time = time.time() - start_time
        
        return AcousticAnalysisResult(
            prosody_features=prosody_features,
            spectral_features=spectral_features,
            opensmile_features=opensmile_features,
            stress_indicators=stress_indicators,
            deception_markers=deception_markers,
            overall_voice_quality=voice_quality,
            emotional_state_acoustic=emotional_state_acoustic,
            processing_time=processing_time,
            features_extracted=features_extracted
        )

def main():
    """Test the acoustic analyzer"""
    # Check for audio file
    audio_files = [
        "test_audio_converted.wav",
        "250825-1107_OugfC4aY.mp3",
        "250825_1107.mp3",
        "test_audio.wav"
    ]
    
    audio_path = None
    for file in audio_files:
        if os.path.exists(file):
            audio_path = file
            break
    
    if not audio_path:
        print("❌ No audio file found for testing")
        print("Available files should be one of:", audio_files)
        return
    
    # Initialize analyzer
    analyzer = AcousticAnalyzer()
    
    print(f"🎵 Available libraries:")
    print(f"  - Praat-Parselmouth: {'✅' if analyzer.praat_available else '❌'}")
    print(f"  - pyAudioAnalysis: {'✅' if analyzer.pyaudio_available else '❌'}")
    print(f"  - openSMILE: {'✅' if analyzer.opensmile_available else '❌'}")
    
    if not any([analyzer.praat_available, analyzer.pyaudio_available, analyzer.opensmile_available]):
        print("❌ No acoustic analysis libraries available!")
        print("Install with:")
        print("  pip install praat-parselmouth pyAudioAnalysis opensmile")
        return
    
    # Perform analysis
    result = analyzer.analyze_audio(audio_path)
    
    # Print results
    print("\n" + "="*80)
    print("🎵 ACOUSTIC ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\n📊 Features Extracted: {', '.join(result.features_extracted)}")
    print(f"🎯 Overall Voice Quality: {result.overall_voice_quality:.3f}")
    
    print(f"\n😰 STRESS INDICATORS:")
    print(f"  Stress Level: {result.stress_indicators.stress_level:.3f}")
    print(f"  Emotional Arousal: {result.stress_indicators.emotional_arousal:.3f}")
    print(f"  Valence: {result.stress_indicators.valence:.3f}")
    print(f"  Voice Tension: {result.stress_indicators.voice_tension:.3f}")
    print(f"  Breathing Irregularity: {result.stress_indicators.breathing_irregularity:.3f}")
    
    print(f"\n🕵️ DECEPTION MARKERS:")
    print(f"  Pitch Variability: {result.deception_markers.pitch_variability_score:.3f}")
    print(f"  Voice Quality Degradation: {result.deception_markers.voice_quality_degradation:.3f}")
    print(f"  Hesitation Markers: {result.deception_markers.hesitation_markers:.3f}")
    print(f"  Speech Rate Changes: {result.deception_markers.speech_rate_changes:.3f}")
    print(f"  Confidence Score: {result.deception_markers.confidence_score:.3f}")
    
    print(f"\n💭 EMOTIONAL STATE (Acoustic):")
    for emotion, value in result.emotional_state_acoustic.items():
        print(f"  {emotion.title()}: {value:.3f}")
    
    if result.prosody_features:
        print(f"\n🔊 PROSODIC FEATURES:")
        print(f"  Mean F0: {result.prosody_features.mean_f0:.1f} Hz")
        print(f"  F0 Range: {result.prosody_features.f0_range:.1f} Hz")
        print(f"  Jitter: {result.prosody_features.jitter:.4f}")
        print(f"  Shimmer: {result.prosody_features.shimmer:.4f}")
        print(f"  HNR: {result.prosody_features.hnr:.1f} dB")
        print(f"  Speaking Rate: {result.prosody_features.speaking_rate:.1f} syll/sec")
    
    print(f"\n⏱️ Processing Time: {result.processing_time:.2f}s")
    
    # Save results
    timestamp = int(time.time())
    results_file = f"acoustic_analysis_results_{timestamp}.json"
    
    # Convert to dict for JSON serialization
    result_dict = {
        'prosody_features': asdict(result.prosody_features) if result.prosody_features else None,
        'spectral_features': asdict(result.spectral_features) if result.spectral_features else None,
        'opensmile_features': asdict(result.opensmile_features) if result.opensmile_features else None,
        'stress_indicators': asdict(result.stress_indicators),
        'deception_markers': asdict(result.deception_markers),
        'overall_voice_quality': result.overall_voice_quality,
        'emotional_state_acoustic': result.emotional_state_acoustic,
        'processing_time': result.processing_time,
        'features_extracted': result.features_extracted,
        'audio_file': audio_path
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")

if __name__ == "__main__":
    main()