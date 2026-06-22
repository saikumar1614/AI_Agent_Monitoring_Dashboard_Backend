import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import app
    print("✓ FastAPI App Initialized Successfully")
    print(f"  App Name: {app.title}")
    print(f"  App Version: {app.version}")
    print(f"  Registered Routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"    - {route.path}")
    print("\n✓ Application startup verification PASSED")
except Exception as e:
    print(f"✗ Error initializing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
