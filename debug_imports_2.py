import sys
import importlib
import traceback
import os

print("Current working directory:", os.getcwd())
print("\nPython version:", sys.version)
print("\nPython path:")
for path in sys.path:
    print(f"  {path}")

print("\nDirectory contents:")
for root, dirs, files in os.walk('.'):
    print(f"\nDirectory: {root}")
    for file in files:
        print(f"  {file}")

print("\nTrying to import cleaner module...")
try:
    # First try to import the module
    cleaner_module = importlib.import_module('src.cleaner')
    print("Successfully imported src.cleaner module")
    
    # Then try to get the clean_data function
    clean_data = getattr(cleaner_module, 'clean_data')
    print("Successfully got clean_data function")
    
except Exception as e:
    print(f"\nError occurred: {type(e).__name__}: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc() 