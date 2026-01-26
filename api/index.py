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
    sys.exit(1)

# Simple test handler first
def test_handler(request):
    """Simple test handler"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>🏏 CricSmart is Working!</h1><p>Test handler executed successfully!</p>'
    }

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler"""
    try:
        print(f"🎯 Request received: {type(request)}")
        
        # Try simple test first
        if request.get('path', '/') == '/test':
            return test_handler(request)
        
        print("🔄 Calling app handler...")
        result = app_handler(request)
        print(f"✅ Handler executed successfully")
        return result
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
