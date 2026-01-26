# Vercel Python Entry Point
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 API handler starting...")

# Test imports to verify dependencies
try:
    import reportlab
    print("✅ ReportLab imported successfully")
except ImportError as e:
    print(f"❌ ReportLab import failed: {e}")
    sys.exit(1)

print("📦 Testing app import...")

# Import your app
try:
    from app import handler as app_handler
    print("✅ App handler imported successfully")
except ImportError as e:
    print(f"❌ App handler import failed: {e}")
    import traceback
    traceback.print_exc()
    # Don't exit, continue with simple handler
    app_handler = None

# Simple test handler
def test_handler(request):
    """Simple test handler"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>🏏 CricSmart Test Working!</h1><p>Simple handler executed successfully!</p>'
    }

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler"""
    try:
        print(f"🎯 Request received: {type(request)} - {request}")
        
        # Always return test for now to debug
        return test_handler(request)
        
        # Try app handler only if it exists
        if app_handler:
            print("🔄 Calling app handler...")
            result = app_handler(request)
            print(f"✅ Handler executed successfully")
            return result
        else:
            print("⚠️ App handler not available, returning test")
            return test_handler(request)
            
    except Exception as e:
        print(f"❌ Handler execution failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Handler execution failed: {str(e)}"}}'
        }

# Export for Vercel
app = handler
print("✅ API handler loaded successfully")
