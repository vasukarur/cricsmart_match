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
try:
    from app import handler as app_handler
    print("✅ App handler imported successfully")
except ImportError as e:
    print(f"❌ App handler import failed: {e}")
    sys.exit(1)

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler"""
    try:
        print(f"🎯 Request received: {request}")
        result = app_handler(request)
        print(f"✅ Handler executed successfully")
        return result
    except Exception as e:
        print(f"❌ Handler execution failed: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Handler execution failed: {str(e)}"}}'
        }

# Export for Vercel
app = handler
