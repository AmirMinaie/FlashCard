import sys
import os
from pathlib import Path

def resource_path(*relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, *relative_path)
    return os.path.join(Base_dir(), *relative_path)

def Base_dir():
    return str(Path(__file__).resolve().parents[2])