# Vercel Python Runtime
from web_app import Handler
import json

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler"""
    # Convert Vercel request to HTTPRequest format
    class VercelRequest:
        def __init__(self, request):
            self.path = request.get('path', '/')
            self.method = request.get('method', 'GET')
            self.headers = request.get('headers', {})
            self.wfile = None
            self.rfile = None
            
        def send_response(self, code):
            self.response_code = code
            
        def send_header(self, name, value):
            if not hasattr(self, 'response_headers'):
                self.response_headers = {}
            self.response_headers[name] = value
            
        def end_headers(self):
            pass
            
    # Create handler instance
    handler_instance = Handler()
    vercel_request = VercelRequest(request)
    
    # Handle the request
    try:
        handler_instance.do_GET(vercel_request)
    except AttributeError:
        # Handle other methods
        pass
    
    # Return response in Vercel format
    return {
        'statusCode': getattr(vercel_request, 'response_code', 200),
        'headers': getattr(vercel_request, 'response_headers', {}),
        'body': ''
    }

# Export for Vercel
app = handler
