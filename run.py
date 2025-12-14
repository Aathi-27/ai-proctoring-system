#!/usr/bin/env python3
"""
Main entry point for YOLOv8 Mobile Detection System.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from main import main
    main()