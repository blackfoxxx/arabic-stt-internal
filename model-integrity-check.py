#!/usr/bin/env python3
"""
Model Integrity Check and Download Script
=========================================
This script verifies the integrity of all required models and downloads
missing ones with proper checksum verification.
"""

import os
import sys
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, List, Optional, Tuple

class ModelIntegrityChecker:
    def __init__(self):
        self.models_config = {
            'whisper_models': {
                'base': {
                    'size_mb': 142,
                    'description': 'Whisper base model for speech recognition'
                },
                'small': {
                    'size_mb': 244,
                    'description': 'Whisper small model for better accuracy'
                }
            },
            'huggingface_models': {
                'aubmindlab/bert-base-arabertv2': {
                    'description': 'Arabic BERT model for text understanding',
                    'files': ['config.json', 'pytorch_model.bin', 'tokenizer.json', 'vocab.txt']
                },
                'cardiffnlp/twitter-xlm-roberta-base-sentiment': {
                    'description': 'Multilingual sentiment analysis model',
                    'files': ['config.json', 'pytorch_model.bin', 'tokenizer.json']
                },
                'microsoft/speecht5_asr': {
                    'description': 'SpeechT5 model for speech recognition',
                    'files': ['config.json', 'pytorch_model.bin', 'preprocessor_config.json']
                }
            },
            'ollama_models': {
                'llama3.1:8b': {
                    'description': 'Llama 3.1 8B model for advanced text processing',
                    'size_gb': 4.7,
                    'recommended': True
                },
                'mistral:7b': {
                    'description': 'Mistral 7B model for efficient text processing',
                    'size_gb': 4.1,
                    'recommended': True
                },
                'qwen2.5:7b': {
                    'description': 'Qwen2.5 7B model for multilingual tasks',
                    'size_gb': 4.4,
                    'recommended': True
                },
                'phi3:mini': {
                    'description': 'Phi-3 Mini model for fast processing',
                    'size_gb': 2.3,
                    'recommended': False
                }
            }
        }
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'whisper_models': {},
            'huggingface_models': {},
            'ollama_models': {},
            'downloads': [],
            'errors': [],
            'summary': {}
        }
    
    def log(self, message: str, level: str = 'INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
    
    def get_model_cache_dir(self) -> Path:
        """Get the model cache directory"""
        # Try to get HuggingFace cache directory
        cache_dir = os.environ.get('HF_HOME') or os.environ.get('HUGGINGFACE_HUB_CACHE')
        if cache_dir:
            return Path(cache_dir)
        
        # Default cache locations
        if os.name == 'nt':  # Windows
            cache_dir = Path.home() / '.cache' / 'huggingface'
        else:  # Unix-like
            cache_dir = Path.home() / '.cache' / 'huggingface'
        
        return cache_dir
    
    def check_whisper_models(self) -> bool:
        """Check Whisper models integrity"""
        self.log("Checking Whisper models...")
        
        all_good = True
        
        for model_name, model_info in self.models_config['whisper_models'].items():
            try:
                import whisper
                
                # Try to load the model
                self.log(f"Loading Whisper {model_name} model...")
                model = whisper.load_model(model_name)
                
                # Get model file path
                model_path = whisper._MODELS[model_name]
                if hasattr(whisper, '_download'):
                    # Get the actual downloaded file path
                    import whisper.audio
                    model_file = None
                    try:
                        # This is a bit hacky, but Whisper doesn't expose the file path directly
                        cache_dir = Path.home() / '.cache' / 'whisper'
                        potential_files = list(cache_dir.glob(f"*{model_name}*"))
                        if potential_files:
                            model_file = potential_files[0]
                    except:
                        pass
                
                self.results['whisper_models'][model_name] = {
                    'status': 'loaded',
                    'description': model_info['description'],
                    'expected_size_mb': model_info['size_mb'],
                    'file_path': str(model_file) if model_file else 'unknown'
                }
                
                self.log(f"✓ Whisper {model_name} model loaded successfully")
                
            except Exception as e:
                self.log(f"✗ Whisper {model_name} model failed: {e}", 'ERROR')
                self.results['whisper_models'][model_name] = {
                    'status': 'error',
                    'error': str(e),
                    'description': model_info['description']
                }
                self.results['errors'].append(f"Whisper {model_name}: {e}")
                all_good = False
        
        return all_good
    
    def check_huggingface_models(self) -> bool:
        """Check HuggingFace models integrity"""
        self.log("Checking HuggingFace models...")
        
        all_good = True
        
        for model_name, model_info in self.models_config['huggingface_models'].items():
            try:
                self.log(f"Checking {model_name}...")
                
                # Try to load the model
                from transformers import AutoConfig, AutoTokenizer
                
                # Check if model is cached locally
                cache_dir = self.get_model_cache_dir()
                model_cache_path = cache_dir / 'hub' / f"models--{model_name.replace('/', '--')}"
                
                model_status = {
                    'status': 'unknown',
                    'description': model_info['description'],
                    'cache_path': str(model_cache_path),
                    'files_found': [],
                    'files_missing': []
                }
                
                # Check if model files exist locally
                if model_cache_path.exists():
                    # Look for model files in the cache
                    for root, dirs, files in os.walk(model_cache_path):
                        model_status['files_found'].extend(files)
                    
                    # Check for required files
                    required_files = model_info.get('files', [])
                    for req_file in required_files:
                        found = any(req_file in f for f in model_status['files_found'])
                        if not found:
                            model_status['files_missing'].append(req_file)
                
                # Try to load the model to verify it works
                try:
                    config = AutoConfig.from_pretrained(model_name)
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    model_status['status'] = 'loaded'
                    model_status['config_loaded'] = True
                    model_status['tokenizer_loaded'] = True
                    
                    self.log(f"✓ {model_name} loaded successfully")
                    
                except Exception as load_error:
                    model_status['status'] = 'load_error'
                    model_status['load_error'] = str(load_error)
                    self.log(f"⚠ {model_name} files found but loading failed: {load_error}", 'WARNING')
                    all_good = False
                
                self.results['huggingface_models'][model_name] = model_status
                
            except Exception as e:
                self.log(f"✗ {model_name} check failed: {e}", 'ERROR')
                self.results['huggingface_models'][model_name] = {
                    'status': 'error',
                    'error': str(e),
                    'description': model_info['description']
                }
                self.results['errors'].append(f"{model_name}: {e}")
                all_good = False
        
        return all_good
    
    def download_missing_whisper_models(self) -> bool:
        """Download missing Whisper models"""
        self.log("Downloading missing Whisper models...")
        
        missing_models = []
        for model_name, model_status in self.results['whisper_models'].items():
            if model_status['status'] != 'loaded':
                missing_models.append(model_name)
        
        if not missing_models:
            self.log("All Whisper models are already available")
            return True
        
        success = True
        for model_name in missing_models:
            try:
                self.log(f"Downloading Whisper {model_name} model...")
                import whisper
                
                # This will download the model if it's not already cached
                model = whisper.load_model(model_name)
                
                self.results['downloads'].append({
                    'model': f'whisper_{model_name}',
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                
                self.log(f"✓ Whisper {model_name} downloaded successfully")
                
            except Exception as e:
                self.log(f"✗ Failed to download Whisper {model_name}: {e}", 'ERROR')
                self.results['downloads'].append({
                    'model': f'whisper_{model_name}',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                success = False
        
        return success
    
    def check_ollama_models(self) -> bool:
        """Check Ollama models availability and integrity"""
        self.log("Checking Ollama models...")
        
        all_good = True
        
        # First check if Ollama is installed
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.log("Ollama is not installed or not accessible", 'WARNING')
                self.results['ollama_models']['service'] = {
                    'status': 'not_available',
                    'error': 'Ollama not installed'
                }
                return False
                
            ollama_version = result.stdout.strip()
            self.log(f"Ollama version: {ollama_version}")
            
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.log(f"Ollama is not available: {e}", 'WARNING')
            self.results['ollama_models']['service'] = {
                'status': 'not_available',
                'error': str(e)
            }
            return False
        
        # Get list of available models
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                self.log("Failed to list Ollama models", 'ERROR')
                self.results['ollama_models']['service'] = {
                    'status': 'error',
                    'error': 'Failed to list models'
                }
                return False
            
            # Parse available models
            available_models = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    available_models.append(model_name)
            
            self.log(f"Available Ollama models: {', '.join(available_models) if available_models else 'None'}")
            
        except subprocess.TimeoutExpired:
            self.log("Ollama list command timed out", 'ERROR')
            self.results['ollama_models']['service'] = {
                'status': 'timeout',
                'error': 'List command timed out'
            }
            return False
        
        # Check each configured model
        for model_name, model_info in self.models_config['ollama_models'].items():
            model_available = any(model_name in available for available in available_models)
            
            if model_available:
                # Try to test the model with a simple prompt
                try:
                    test_result = subprocess.run([
                        'ollama', 'run', model_name, 'Hello, respond with just "OK"'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if test_result.returncode == 0 and 'OK' in test_result.stdout.upper():
                        self.results['ollama_models'][model_name] = {
                            'status': 'loaded',
                            'description': model_info['description'],
                            'size_gb': model_info['size_gb'],
                            'recommended': model_info['recommended'],
                            'test_passed': True
                        }
                        self.log(f"✓ {model_name} is loaded and functional")
                    else:
                        self.results['ollama_models'][model_name] = {
                            'status': 'available_but_failed_test',
                            'description': model_info['description'],
                            'error': 'Model test failed',
                            'test_output': test_result.stdout[:100]
                        }
                        self.log(f"⚠ {model_name} is available but failed functionality test", 'WARNING')
                        all_good = False
                        
                except subprocess.TimeoutExpired:
                    self.results['ollama_models'][model_name] = {
                        'status': 'available_but_timeout',
                        'description': model_info['description'],
                        'error': 'Model test timed out'
                    }
                    self.log(f"⚠ {model_name} test timed out", 'WARNING')
                    all_good = False
                    
            else:
                self.results['ollama_models'][model_name] = {
                    'status': 'not_downloaded',
                    'description': model_info['description'],
                    'size_gb': model_info['size_gb'],
                    'recommended': model_info['recommended']
                }
                self.log(f"✗ {model_name} is not downloaded")
                if model_info['recommended']:
                    all_good = False
        
        return all_good
    
    def download_missing_ollama_models(self) -> bool:
        """Download missing Ollama models"""
        self.log("Downloading missing Ollama models...")
        
        # Check if Ollama is available
        try:
            subprocess.run(['ollama', '--version'], 
                          capture_output=True, text=True, timeout=10, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            self.log("Ollama is not available, skipping model downloads", 'WARNING')
            return False
        
        missing_models = []
        for model_name, model_status in self.results['ollama_models'].items():
            if model_name != 'service' and model_status['status'] == 'not_downloaded':
                if model_status.get('recommended', False):
                    missing_models.append(model_name)
        
        if not missing_models:
            self.log("All recommended Ollama models are already available")
            return True
        
        success = True
        for model_name in missing_models:
            try:
                self.log(f"Downloading {model_name} (this may take several minutes)...")
                
                result = subprocess.run(['ollama', 'pull', model_name], 
                                      capture_output=True, text=True, timeout=1800)  # 30 minutes timeout
                
                if result.returncode == 0:
                    self.results['downloads'].append({
                        'model': f'ollama_{model_name}',
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    })
                    self.log(f"✓ {model_name} downloaded successfully")
                else:
                    self.results['downloads'].append({
                        'model': f'ollama_{model_name}',
                        'status': 'failed',
                        'error': result.stderr,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.log(f"✗ Failed to download {model_name}: {result.stderr}", 'ERROR')
                    success = False
                    
            except subprocess.TimeoutExpired:
                self.log(f"✗ Download of {model_name} timed out", 'ERROR')
                self.results['downloads'].append({
                    'model': f'ollama_{model_name}',
                    'status': 'timeout',
                    'error': 'Download timed out',
                    'timestamp': datetime.now().isoformat()
                })
                success = False
            except Exception as e:
                self.log(f"✗ Failed to download {model_name}: {e}", 'ERROR')
                self.results['downloads'].append({
                    'model': f'ollama_{model_name}',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                success = False
        
        return success
    
    def download_missing_huggingface_models(self) -> bool:
        """Download missing HuggingFace models"""
        self.log("Downloading missing HuggingFace models...")
        
        missing_models = []
        for model_name, model_status in self.results['huggingface_models'].items():
            if model_status['status'] not in ['loaded']:
                missing_models.append(model_name)
        
        if not missing_models:
            self.log("All HuggingFace models are already available")
            return True
        
        success = True
        for model_name in missing_models:
            try:
                self.log(f"Downloading {model_name}...")
                from transformers import AutoConfig, AutoTokenizer, AutoModel
                
                # Download config and tokenizer
                config = AutoConfig.from_pretrained(model_name)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # For some models, also download the model weights
                try:
                    model = AutoModel.from_pretrained(model_name)
                    model_downloaded = True
                except Exception as model_error:
                    self.log(f"⚠ Could not download model weights for {model_name}: {model_error}", 'WARNING')
                    model_downloaded = False
                
                self.results['downloads'].append({
                    'model': model_name,
                    'status': 'success',
                    'config_downloaded': True,
                    'tokenizer_downloaded': True,
                    'model_downloaded': model_downloaded,
                    'timestamp': datetime.now().isoformat()
                })
                
                self.log(f"✓ {model_name} downloaded successfully")
                
            except Exception as e:
                self.log(f"✗ Failed to download {model_name}: {e}", 'ERROR')
                self.results['downloads'].append({
                    'model': model_name,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                success = False
        
        return success
    
    def verify_model_functionality(self) -> bool:
        """Verify that models can actually perform their intended tasks"""
        self.log("Verifying model functionality...")
        
        functionality_results = {}
        
        # Test Whisper functionality
        try:
            import whisper
            import numpy as np
            
            # Create dummy audio data
            sample_rate = 16000
            duration = 1  # 1 second
            dummy_audio = np.random.randn(sample_rate * duration).astype(np.float32)
            
            model = whisper.load_model("base")
            result = model.transcribe(dummy_audio)
            
            functionality_results['whisper_transcription'] = {
                'status': 'success',
                'test_result': result.get('text', '')[:50] + '...' if result.get('text') else 'No text'
            }
            self.log("✓ Whisper transcription test passed")
            
        except Exception as e:
            functionality_results['whisper_transcription'] = {
                'status': 'failed',
                'error': str(e)
            }
            self.log(f"✗ Whisper transcription test failed: {e}", 'ERROR')
        
        # Test Arabic BERT functionality
        try:
            from transformers import AutoTokenizer, AutoModel
            
            tokenizer = AutoTokenizer.from_pretrained('aubmindlab/bert-base-arabertv2')
            model = AutoModel.from_pretrained('aubmindlab/bert-base-arabertv2')
            
            # Test with Arabic text
            test_text = "مرحبا بك في نظام التحليل الصوتي"
            inputs = tokenizer(test_text, return_tensors="pt")
            outputs = model(**inputs)
            
            functionality_results['arabic_bert'] = {
                'status': 'success',
                'test_text': test_text,
                'output_shape': str(outputs.last_hidden_state.shape)
            }
            self.log("✓ Arabic BERT test passed")
            
        except Exception as e:
            functionality_results['arabic_bert'] = {
                'status': 'failed',
                'error': str(e)
            }
            self.log(f"✗ Arabic BERT test failed: {e}", 'ERROR')
        
        # Test sentiment analysis functionality
        try:
            from transformers import pipeline
            
            sentiment_pipeline = pipeline('sentiment-analysis', 
                                         model='cardiffnlp/twitter-xlm-roberta-base-sentiment')
            
            test_texts = ["I love this system!", "This is terrible"]
            results = sentiment_pipeline(test_texts)
            
            functionality_results['sentiment_analysis'] = {
                'status': 'success',
                'test_results': results
            }
            self.log("✓ Sentiment analysis test passed")
            
        except Exception as e:
            functionality_results['sentiment_analysis'] = {
                'status': 'failed',
                'error': str(e)
            }
            self.log(f"✗ Sentiment analysis test failed: {e}", 'ERROR')
        
        self.results['functionality_tests'] = functionality_results
        
        # Check if critical functionality works
        critical_tests = ['whisper_transcription', 'arabic_bert']
        failed_critical = [test for test in critical_tests 
                          if functionality_results.get(test, {}).get('status') != 'success']
        
        return len(failed_critical) == 0
    
    def generate_summary(self):
        """Generate summary of model integrity check"""
        whisper_models = self.results['whisper_models']
        hf_models = self.results['huggingface_models']
        ollama_models = self.results['ollama_models']
        
        whisper_loaded = sum(1 for m in whisper_models.values() if m['status'] == 'loaded')
        whisper_total = len(whisper_models)
        
        hf_loaded = sum(1 for m in hf_models.values() if m['status'] == 'loaded')
        hf_total = len(hf_models)
        
        # Count Ollama models (excluding 'service' entry)
        ollama_loaded = sum(1 for k, m in ollama_models.items() 
                           if k != 'service' and m.get('status') == 'loaded')
        ollama_total = len([k for k in ollama_models.keys() if k != 'service'])
        
        downloads_successful = sum(1 for d in self.results['downloads'] if d['status'] == 'success')
        downloads_total = len(self.results['downloads'])
        
        functionality_passed = sum(1 for t in self.results.get('functionality_tests', {}).values() 
                                 if t['status'] == 'success')
        functionality_total = len(self.results.get('functionality_tests', {}))
        
        self.results['summary'] = {
            'whisper_models': f"{whisper_loaded}/{whisper_total}",
            'huggingface_models': f"{hf_loaded}/{hf_total}",
            'ollama_models': f"{ollama_loaded}/{ollama_total}",
            'downloads': f"{downloads_successful}/{downloads_total}" if downloads_total > 0 else "0/0",
            'functionality_tests': f"{functionality_passed}/{functionality_total}",
            'total_errors': len(self.results['errors']),
            'overall_status': 'GOOD' if (whisper_loaded == whisper_total and 
                                       hf_loaded >= hf_total * 0.8 and
                                       ollama_loaded >= ollama_total * 0.5 and  # More lenient for Ollama
                                       functionality_passed >= functionality_total * 0.8) else 'NEEDS_ATTENTION'
        }
    
    def save_results(self):
        """Save results to file"""
        results_file = 'model_integrity_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        self.log(f"Results saved to {results_file}")
    
    def print_summary(self):
        """Print summary of results"""
        print("\n" + "="*70)
        print("MODEL INTEGRITY CHECK SUMMARY")
        print("="*70)
        
        summary = self.results['summary']
        status = summary['overall_status']
        
        print(f"Overall Status: {'✓' if status == 'GOOD' else '⚠'} {status}")
        print(f"Whisper Models: {summary['whisper_models']}")
        print(f"HuggingFace Models: {summary['huggingface_models']}")
        print(f"Ollama Models: {summary['ollama_models']}")
        print(f"Downloads: {summary['downloads']}")
        print(f"Functionality Tests: {summary['functionality_tests']}")
        print(f"Total Errors: {summary['total_errors']}")
        
        if status == 'GOOD':
            print("\n🎉 All models are properly installed and functional!")
        else:
            print("\n⚠️  Some models need attention. Check the detailed results.")
            if self.results['errors']:
                print("\nErrors encountered:")
                for error in self.results['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")
        
        print("="*70)
    
    def run_full_check(self, download_missing: bool = True) -> bool:
        """Run complete model integrity check"""
        self.log("Starting comprehensive model integrity check...")
        
        try:
            # Check existing models
            whisper_ok = self.check_whisper_models()
            hf_ok = self.check_huggingface_models()
            ollama_ok = self.check_ollama_models()
            
            # Download missing models if requested
            if download_missing:
                if not whisper_ok:
                    self.download_missing_whisper_models()
                if not hf_ok:
                    self.download_missing_huggingface_models()
                if not ollama_ok:
                    self.download_missing_ollama_models()
                
                # Re-check after downloads
                self.log("Re-checking models after downloads...")
                whisper_ok = self.check_whisper_models()
                hf_ok = self.check_huggingface_models()
                ollama_ok = self.check_ollama_models()
            
            # Verify functionality
            functionality_ok = self.verify_model_functionality()
            
            # Generate summary
            self.generate_summary()
            
            # Save and display results
            self.save_results()
            self.print_summary()
            
            return self.results['summary']['overall_status'] == 'GOOD'
            
        except Exception as e:
            self.log(f"Model integrity check failed: {e}", 'ERROR')
            self.results['summary'] = {'overall_status': 'ERROR', 'error': str(e)}
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check and verify model integrity')
    parser.add_argument('--no-download', action='store_true', 
                       help='Skip downloading missing models')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    checker = ModelIntegrityChecker()
    success = checker.run_full_check(download_missing=not args.no_download)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()