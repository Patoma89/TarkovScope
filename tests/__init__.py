"""
TarkovScope Test Suite
"""
import sys
import os

# Asegurar que TarkovScope está primero en el PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
