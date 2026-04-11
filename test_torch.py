import sys
import os

print(f"Python version: {sys.version}")
print(f"Executable: {sys.executable}")

try:
    import torch
    print(f"Torch version: {torch.__version__}")
    print(f"Torch file: {torch.__file__}")
except Exception as e:
    print(f"Failed to import torch: {e}")

try:
    import torch._C
    print("torch._C ok")
except Exception as e:
    print(f"Failed to import torch._C: {e}")
    import traceback
    traceback.print_exc()

try:
    import torchvision
    print(f"Torchvision version: {torchvision.__version__}")
except Exception as e:
    print(f"Failed to import torchvision: {e}")
    import traceback
    traceback.print_exc()
