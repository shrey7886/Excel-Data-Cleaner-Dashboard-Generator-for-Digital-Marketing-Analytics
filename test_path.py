import sys
print("Python path:", sys.path)
print("\nTrying to import cleaner...")
try:
    from src.cleaner import clean_data
    print("Successfully imported cleaner")
except ImportError as e:
    print(f"Import error: {e}")

# The error message indicates that Django is not installed in your current Python environment.
# The following code block is added to check for Django's presence.

try:
    import django
    print("Successfully imported Django")
except ImportError as e:
    print(f"Import error: {e}") 