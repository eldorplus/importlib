import os.path
import sys

TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_ROOT)

sys.path.insert(0, PROJECT_ROOT)  # Force the right importlib2.
import importlib2

# Swap in importlib2 and test.
sys.modules['importlib'] = importlib2
sys.modules['test'] = sys.modules[__name__]
