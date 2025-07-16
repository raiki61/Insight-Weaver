import sys
import os

print("--- Python Search Paths (sys.path) ---")
for path in sys.path:
    print(path)
print("------------------------------------")

print(f"PYTHONPATH Environment Variable: {os.getenv('PYTHONPATH')}")
print("------------------------------------")

try:
    print("Attempting to import 'common_types'...")
    import common_types
    print(">>> SUCCESS: 'common_types' imported successfully!")
except ImportError as e:
    print(f">>> FAILED: {e}")
