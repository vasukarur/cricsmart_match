# Debug version to identify the 500 error
import json

def handler(request):
    """Debug handler to identify the issue"""
    try:
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        
        print(f"🔍 Debug Request: {method} {path}")
        print(f"🔍 Full request: {request}")
        
        # Test basic response first
        if path == '/' or path == '/index.html':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': '''
<!DOCTYPE html>
<html>
<head>
    <title>CricSmart Debug</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { color: #01147C; margin-bottom: 30px; }
        .status { background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .button { background: #01147C; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .result { background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏏 CricSmart Debug Mode</h1>
            <h2>Testing Serverless Function</h2>
        </div>
        <div class="status">
            <h3>✅ Basic Serverless Working!</h3>
            <p>If you can see this page, the serverless function is working.</p>
            <p>Now testing cricket modules...</p>
        </div>
        <div class="actions">
            <button class="button" onclick="testModules()">Test Cricket Modules</button>
            <button class="button" onclick="testAPI()">Test API Response</button>
        </div>
        <div id="result" class="result"></div>
    </div>
    <script>
        async function testModules() {
            try {
                const response = await fetch('/api/test-modules');
                const data = await response.json();
                document.getElementById('result').innerHTML = '<h4>Module Test Result:</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
        
        async function testAPI() {
            try {
                const response = await fetch('/api/test');
                const data = await response.json();
                document.getElementById('result').innerHTML = '<h4>API Test Result:</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
                '''
            }
        
        elif path.startswith('/api/test-modules'):
            # Test importing cricket modules
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                from models import MatchState, Team, Player
                from pdf_generator import generate_scoreboard_pdf
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': True,
                        'modules': '✅ All cricket modules imported successfully',
                        'models_available': True,
                        'pdf_generator_available': True
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': False,
                        'error': str(e),
                        'modules': '❌ Module import failed'
                    })
                }
        
        elif path.startswith('/api/test'):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'API is working!',
                    'method': method,
                    'path': path,
                    'timestamp': '2026-01-26'
                })
            }
        
        # Default response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Debug handler working',
                'method': method,
                'path': path
            })
        }
        
    except Exception as e:
        print(f"❌ Debug Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e),
                'message': 'Debug handler failed'
            })
        }

# Export for Vercel
app = handler
