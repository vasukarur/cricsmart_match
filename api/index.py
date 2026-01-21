# Vercel Python Entry Point
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports to verify dependencies
try:
    import reportlab
    print("✅ ReportLab imported successfully")
except ImportError as e:
    print(f"❌ ReportLab import failed: {e}")
    sys.exit(1)

# Import your app
from app import handler as app_handler

# Vercel serverless handler
def handler(request):
    return app_handler(request)

# Export for Vercel
app = handler
