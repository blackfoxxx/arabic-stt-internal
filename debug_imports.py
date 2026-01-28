import sys
import traceback

print("Testing imports...")
try:
    import torch
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device: {torch.cuda.get_device_name(0)}")
except ImportError:
    print("Failed to import torch")
    traceback.print_exc()
except Exception:
    print("Error during torch check")
    traceback.print_exc()

try:
    from faster_whisper import WhisperModel
    print("faster-whisper imported successfully")
except ImportError:
    print("Failed to import faster_whisper")
    traceback.print_exc()
except Exception:
    print("Error during faster_whisper check")
    traceback.print_exc()
