#!/usr/bin/env python3
"""
Arabic STT Installation Verification Script
==========================================
Comprehensive verification of all system components, dependencies, and models.
This script performs integrity checks and validates the complete installation.
"""

import os
import sys
import json
import hashlib
import subprocess
import importlib
from pathlib import Path
from datetime import datetime
import platform

class InstallationVerifier:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'dependencies': {},
            'models': {},
            'integrity_checks': {},
            'performance_tests': {},
            'overall_status': 'UNKNOWN'
        }
        
    def log(self, message, level='INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
    def check_system_info(self):
        """Check system information and requirements"""
        self.log("Checking system information...")
        
        try:
            self.results['system_info'] = {
                'platform': platform.platform(),
                'python_version': sys.version,
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'machine': platform.machine(),
                'node': platform.node()
            }
            
            # Check available memory
            try:
                import psutil
                memory = psutil.virtual_memory()
                self.results['system_info']['total_memory_gb'] = round(memory.total / (1024**3), 2)
                self.results['system_info']['available_memory_gb'] = round(memory.available / (1024**3), 2)
            except ImportError:
                self.results['system_info']['memory_info'] = 'psutil not available'
                
            # Check disk space
            import shutil
            total, used, free = shutil.disk_usage('.')
            self.results['system_info']['disk_space_gb'] = {
                'total': round(total / (1024**3), 2),
                'used': round(used / (1024**3), 2),
                'free': round(free / (1024**3), 2)
            }
            
            self.log("✓ System information collected")
            return True
            
        except Exception as e:
            self.log(f"✗ System info check failed: {e}", 'ERROR')
            return False
    
    def check_python_dependencies(self):
        """Verify all Python dependencies are installed and working"""
        self.log("Checking Python dependencies...")
        
        required_packages = [
            'torch', 'torchvision', 'torchaudio',
            'transformers', 'datasets', 'accelerate',
            'whisper', 'faster_whisper',
            'numpy', 'pandas', 'scikit-learn',
            'librosa', 'soundfile', 'pydub',
            'fastapi', 'uvicorn',
            'pyannote.audio'
        ]
        
        dependency_status = {}
        
        for package in required_packages:
            try:
                # Handle special cases
                if package == 'pyannote.audio':
                    import pyannote.audio
                    version = pyannote.audio.__version__
                elif package == 'faster_whisper':
                    import faster_whisper
                    version = faster_whisper.__version__
                else:
                    module = importlib.import_module(package)
                    version = getattr(module, '__version__', 'unknown')
                
                dependency_status[package] = {
                    'status': 'installed',
                    'version': version
                }
                self.log(f"✓ {package} v{version}")
                
            except ImportError as e:
                dependency_status[package] = {
                    'status': 'missing',
                    'error': str(e)
                }
                self.log(f"✗ {package} - MISSING", 'ERROR')
            except Exception as e:
                dependency_status[package] = {
                    'status': 'error',
                    'error': str(e)
                }
                self.log(f"⚠ {package} - ERROR: {e}", 'WARNING')
        
        self.results['dependencies']['python'] = dependency_status
        
        # Check CUDA availability
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                cuda_info = {
                    'available': True,
                    'device_count': torch.cuda.device_count(),
                    'current_device': torch.cuda.current_device(),
                    'device_name': torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else 'Unknown'
                }
                self.log(f"✓ CUDA available: {cuda_info['device_name']}")
            else:
                cuda_info = {'available': False}
                self.log("⚠ CUDA not available, using CPU", 'WARNING')
                
            self.results['dependencies']['cuda'] = cuda_info
            
        except Exception as e:
            self.log(f"✗ CUDA check failed: {e}", 'ERROR')
            self.results['dependencies']['cuda'] = {'error': str(e)}
        
        missing_packages = [pkg for pkg, info in dependency_status.items() if info['status'] == 'missing']
        if missing_packages:
            self.log(f"Missing packages: {', '.join(missing_packages)}", 'ERROR')
            return False
        
        return True
    
    def check_nodejs_dependencies(self):
        """Check Node.js and npm dependencies"""
        self.log("Checking Node.js dependencies...")
        
        try:
            # Check Node.js version
            node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if node_result.returncode == 0:
                node_version = node_result.stdout.strip()
                self.log(f"✓ Node.js {node_version}")
                
                # Check npm version
                npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
                if npm_result.returncode == 0:
                    npm_version = npm_result.stdout.strip()
                    self.log(f"✓ npm {npm_version}")
                    
                    # Check if package.json exists and dependencies are installed
                    if Path('package.json').exists():
                        if Path('node_modules').exists():
                            self.log("✓ Node.js dependencies installed")
                            self.results['dependencies']['nodejs'] = {
                                'node_version': node_version,
                                'npm_version': npm_version,
                                'dependencies_installed': True
                            }
                        else:
                            self.log("⚠ Node.js dependencies not installed", 'WARNING')
                            self.results['dependencies']['nodejs'] = {
                                'node_version': node_version,
                                'npm_version': npm_version,
                                'dependencies_installed': False
                            }
                    else:
                        self.log("⚠ package.json not found", 'WARNING')
                        self.results['dependencies']['nodejs'] = {
                            'node_version': node_version,
                            'npm_version': npm_version,
                            'package_json_exists': False
                        }
                else:
                    self.log("✗ npm not available", 'ERROR')
                    return False
            else:
                self.log("✗ Node.js not available", 'ERROR')
                return False
                
            return True
            
        except Exception as e:
            self.log(f"✗ Node.js check failed: {e}", 'ERROR')
            self.results['dependencies']['nodejs'] = {'error': str(e)}
            return False
    
    def check_models(self):
        """Verify LLM models are downloaded and accessible"""
        self.log("Checking LLM models...")
        
        model_status = {}
        
        # Check Whisper models
        try:
            import whisper
            whisper_models = ['base', 'small']
            for model_name in whisper_models:
                try:
                    model = whisper.load_model(model_name)
                    model_status[f'whisper_{model_name}'] = {
                        'status': 'loaded',
                        'type': 'whisper'
                    }
                    self.log(f"✓ Whisper {model_name} model loaded")
                except Exception as e:
                    model_status[f'whisper_{model_name}'] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    self.log(f"✗ Whisper {model_name} model failed: {e}", 'ERROR')
        except Exception as e:
            self.log(f"✗ Whisper models check failed: {e}", 'ERROR')
        
        # Check Transformers models
        try:
            from transformers import AutoTokenizer, AutoModel, pipeline
            
            # Arabic BERT model
            try:
                tokenizer = AutoTokenizer.from_pretrained('aubmindlab/bert-base-arabertv2')
                model = AutoModel.from_pretrained('aubmindlab/bert-base-arabertv2')
                model_status['arabic_bert'] = {
                    'status': 'loaded',
                    'type': 'transformer',
                    'model_name': 'aubmindlab/bert-base-arabertv2'
                }
                self.log("✓ Arabic BERT model loaded")
            except Exception as e:
                model_status['arabic_bert'] = {
                    'status': 'error',
                    'error': str(e)
                }
                self.log(f"✗ Arabic BERT model failed: {e}", 'ERROR')
            
            # Sentiment analysis model
            try:
                sentiment_pipeline = pipeline('sentiment-analysis', 
                                            model='cardiffnlp/twitter-xlm-roberta-base-sentiment')
                model_status['sentiment_analysis'] = {
                    'status': 'loaded',
                    'type': 'pipeline',
                    'model_name': 'cardiffnlp/twitter-xlm-roberta-base-sentiment'
                }
                self.log("✓ Sentiment analysis model loaded")
            except Exception as e:
                model_status['sentiment_analysis'] = {
                    'status': 'error',
                    'error': str(e)
                }
                self.log(f"✗ Sentiment analysis model failed: {e}", 'ERROR')
                
        except Exception as e:
            self.log(f"✗ Transformers models check failed: {e}", 'ERROR')
        
        # Check Ollama models
        try:
            import subprocess
            
            # Check if Ollama is installed
            try:
                result = subprocess.run(['ollama', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    model_status['ollama_service'] = {
                        'status': 'installed',
                        'version': result.stdout.strip(),
                        'type': 'ollama'
                    }
                    self.log("✓ Ollama service is installed")
                    
                    # Check available Ollama models
                    try:
                        result = subprocess.run(['ollama', 'list'], 
                                              capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            ollama_models = []
                            lines = result.stdout.strip().split('\n')[1:]  # Skip header
                            for line in lines:
                                if line.strip():
                                    model_name = line.split()[0]
                                    ollama_models.append(model_name)
                            
                            model_status['ollama_models'] = {
                                'status': 'available',
                                'models': ollama_models,
                                'count': len(ollama_models),
                                'type': 'ollama'
                            }
                            
                            # Check for recommended models
                            recommended_models = ['llama3.1:8b', 'mistral:7b', 'qwen2.5:7b', 'phi3:mini']
                            available_recommended = [model for model in recommended_models 
                                                   if any(model in available for available in ollama_models)]
                            
                            if available_recommended:
                                self.log(f"✓ Ollama models available: {', '.join(available_recommended)}")
                            else:
                                self.log("⚠ No recommended Ollama models found", 'WARNING')
                                
                        else:
                            model_status['ollama_models'] = {
                                'status': 'error',
                                'error': 'Failed to list Ollama models'
                            }
                            self.log("✗ Failed to list Ollama models", 'ERROR')
                    except subprocess.TimeoutExpired:
                        model_status['ollama_models'] = {
                            'status': 'timeout',
                            'error': 'Ollama list command timed out'
                        }
                        self.log("✗ Ollama list command timed out", 'ERROR')
                        
                else:
                    model_status['ollama_service'] = {
                        'status': 'error',
                        'error': 'Ollama command failed'
                    }
                    self.log("✗ Ollama service check failed", 'ERROR')
                    
            except FileNotFoundError:
                model_status['ollama_service'] = {
                    'status': 'not_installed',
                    'error': 'Ollama not found in PATH'
                }
                self.log("⚠ Ollama not installed", 'WARNING')
            except subprocess.TimeoutExpired:
                model_status['ollama_service'] = {
                    'status': 'timeout',
                    'error': 'Ollama version check timed out'
                }
                self.log("✗ Ollama version check timed out", 'ERROR')
                
        except Exception as e:
            self.log(f"✗ Ollama check failed: {e}", 'ERROR')
            model_status['ollama_service'] = {
                'status': 'error',
                'error': str(e)
            }
        
        self.results['models'] = model_status
        
        # Check if critical models are available
        critical_models = ['whisper_base', 'arabic_bert']
        missing_critical = [model for model in critical_models 
                          if model not in model_status or model_status[model]['status'] != 'loaded']
        
        if missing_critical:
            self.log(f"Missing critical models: {', '.join(missing_critical)}", 'ERROR')
            return False
        
        return True
    
    def perform_integrity_checks(self):
        """Perform integrity checks on key files and configurations"""
        self.log("Performing integrity checks...")
        
        integrity_results = {}
        
        # Check key files exist
        key_files = [
            'multimodal_analysis_system.py',
            'enhanced_truth_detector.py',
            'advanced_sentiment_analyzer.py',
            'gpu_arabic_server.py',
            'training_api.py',
            'package.json',
            'requirements-training.txt'
        ]
        
        for file_path in key_files:
            if Path(file_path).exists():
                # Calculate file hash for integrity
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                integrity_results[file_path] = {
                    'exists': True,
                    'size': Path(file_path).stat().st_size,
                    'hash': file_hash
                }
                self.log(f"✓ {file_path} - OK")
            else:
                integrity_results[file_path] = {'exists': False}
                self.log(f"✗ {file_path} - MISSING", 'ERROR')
        
        # Check directory structure
        required_dirs = ['src', 'public', 'models', 'data']
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                integrity_results[f'dir_{dir_path}'] = {'exists': True}
                self.log(f"✓ Directory {dir_path} - OK")
            else:
                integrity_results[f'dir_{dir_path}'] = {'exists': False}
                self.log(f"⚠ Directory {dir_path} - MISSING", 'WARNING')
        
        self.results['integrity_checks'] = integrity_results
        
        # Check if critical files are missing
        missing_critical = [f for f in key_files[:5] if not integrity_results.get(f, {}).get('exists', False)]
        if missing_critical:
            self.log(f"Missing critical files: {', '.join(missing_critical)}", 'ERROR')
            return False
        
        return True
    
    def run_performance_tests(self):
        """Run basic performance tests"""
        self.log("Running performance tests...")
        
        performance_results = {}
        
        try:
            # Test audio processing
            import numpy as np
            import time
            
            # Generate test audio data
            sample_rate = 16000
            duration = 5  # seconds
            test_audio = np.random.randn(sample_rate * duration).astype(np.float32)
            
            # Test Whisper transcription speed
            try:
                import whisper
                model = whisper.load_model("base")
                
                start_time = time.time()
                result = model.transcribe(test_audio)
                transcription_time = time.time() - start_time
                
                performance_results['whisper_transcription'] = {
                    'duration_seconds': duration,
                    'processing_time': transcription_time,
                    'real_time_factor': transcription_time / duration,
                    'status': 'success'
                }
                self.log(f"✓ Whisper transcription: {transcription_time:.2f}s for {duration}s audio")
                
            except Exception as e:
                performance_results['whisper_transcription'] = {
                    'status': 'error',
                    'error': str(e)
                }
                self.log(f"✗ Whisper performance test failed: {e}", 'ERROR')
            
            # Test PyTorch operations
            try:
                import torch
                
                start_time = time.time()
                x = torch.randn(1000, 1000)
                y = torch.randn(1000, 1000)
                z = torch.matmul(x, y)
                torch_time = time.time() - start_time
                
                performance_results['torch_operations'] = {
                    'matrix_multiply_time': torch_time,
                    'device': str(z.device),
                    'status': 'success'
                }
                self.log(f"✓ PyTorch operations: {torch_time:.4f}s")
                
            except Exception as e:
                performance_results['torch_operations'] = {
                    'status': 'error',
                    'error': str(e)
                }
                self.log(f"✗ PyTorch performance test failed: {e}", 'ERROR')
        
        except Exception as e:
            self.log(f"✗ Performance tests failed: {e}", 'ERROR')
            performance_results['error'] = str(e)
        
        self.results['performance_tests'] = performance_results
        return True
    
    def determine_overall_status(self):
        """Determine overall installation status"""
        
        # Count successful checks
        checks = {
            'system_info': bool(self.results.get('system_info')),
            'python_deps': all(dep.get('status') == 'installed' 
                             for dep in self.results.get('dependencies', {}).get('python', {}).values()),
            'nodejs_deps': self.results.get('dependencies', {}).get('nodejs', {}).get('dependencies_installed', False),
            'models': any(model.get('status') == 'loaded' 
                         for model in self.results.get('models', {}).values()),
            'integrity': all(file_info.get('exists', False) 
                           for file_info in self.results.get('integrity_checks', {}).values() 
                           if 'exists' in file_info),
            'performance': bool(self.results.get('performance_tests'))
        }
        
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        
        if passed_checks == total_checks:
            self.results['overall_status'] = 'EXCELLENT'
        elif passed_checks >= total_checks * 0.8:
            self.results['overall_status'] = 'GOOD'
        elif passed_checks >= total_checks * 0.6:
            self.results['overall_status'] = 'FAIR'
        else:
            self.results['overall_status'] = 'POOR'
        
        self.results['check_summary'] = {
            'passed': passed_checks,
            'total': total_checks,
            'percentage': round((passed_checks / total_checks) * 100, 1)
        }
    
    def save_results(self):
        """Save verification results to file"""
        results_file = 'installation_verification_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        self.log(f"Results saved to {results_file}")
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("INSTALLATION VERIFICATION SUMMARY")
        print("="*70)
        
        status = self.results['overall_status']
        status_colors = {
            'EXCELLENT': '✓',
            'GOOD': '✓',
            'FAIR': '⚠',
            'POOR': '✗'
        }
        
        print(f"Overall Status: {status_colors.get(status, '?')} {status}")
        
        summary = self.results.get('check_summary', {})
        print(f"Checks Passed: {summary.get('passed', 0)}/{summary.get('total', 0)} ({summary.get('percentage', 0)}%)")
        
        print("\nComponent Status:")
        print(f"  System Info: {'✓' if self.results.get('system_info') else '✗'}")
        
        python_deps = self.results.get('dependencies', {}).get('python', {})
        python_ok = all(dep.get('status') == 'installed' for dep in python_deps.values())
        print(f"  Python Dependencies: {'✓' if python_ok else '✗'}")
        
        nodejs_ok = self.results.get('dependencies', {}).get('nodejs', {}).get('dependencies_installed', False)
        print(f"  Node.js Dependencies: {'✓' if nodejs_ok else '✗'}")
        
        models_ok = any(model.get('status') == 'loaded' for model in self.results.get('models', {}).values())
        print(f"  LLM Models: {'✓' if models_ok else '✗'}")
        
        cuda_info = self.results.get('dependencies', {}).get('cuda', {})
        cuda_available = cuda_info.get('available', False)
        print(f"  CUDA Support: {'✓' if cuda_available else '⚠ (CPU only)'}")
        
        print("\nRecommendations:")
        if status == 'EXCELLENT':
            print("  🎉 Installation is complete and fully functional!")
            print("  🚀 You can start using the Arabic STT system.")
        elif status == 'GOOD':
            print("  ✅ Installation is mostly complete with minor issues.")
            print("  🔧 Check the detailed results for optimization opportunities.")
        elif status == 'FAIR':
            print("  ⚠️  Installation has some issues that should be addressed.")
            print("  🛠️  Review missing components and reinstall if necessary.")
        else:
            print("  ❌ Installation has significant issues.")
            print("  🔄 Consider running the installation script again.")
        
        print("="*70)
    
    def run_full_verification(self):
        """Run complete verification process"""
        self.log("Starting comprehensive installation verification...")
        
        try:
            # Run all verification steps
            self.check_system_info()
            self.check_python_dependencies()
            self.check_nodejs_dependencies()
            self.check_models()
            self.perform_integrity_checks()
            self.run_performance_tests()
            
            # Determine overall status
            self.determine_overall_status()
            
            # Save and display results
            self.save_results()
            self.print_summary()
            
            return self.results['overall_status'] in ['EXCELLENT', 'GOOD']
            
        except Exception as e:
            self.log(f"Verification failed with error: {e}", 'ERROR')
            self.results['overall_status'] = 'ERROR'
            self.results['error'] = str(e)
            return False

def main():
    """Main verification function"""
    verifier = InstallationVerifier()
    success = verifier.run_full_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()