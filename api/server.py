# CricSmart Serverless Handler
import os
import json
import uuid
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Add current directory to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import cricket modules
try:
    from models import MatchState, Team, Player, PlayerRole, BallEvent, WicketType, BattingStats, BowlingStats
    from pdf_generator import generate_scoreboard_pdf
    CRICKET_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Cricket modules not available: {e}")
    CRICKET_MODULES_AVAILABLE = False

# Multi-match state structure
STATE = {
    "matches": {},  # Dictionary to store multiple matches by MatchID
    "current_match_id": None,  # Track current active match
}

# Session management for MatchID
SESSIONS = {}  # Store session data if needed

def get_match_id_from_request(request):
    """Extract MatchID from URL parameters or create new one"""
    path = request.get('path', '/')
    query_string = path.split('?')[-1] if '?' in path else ''
    query_params = parse_qs(query_string)
    match_id = query_params.get('match_id', [None])[0]
    
    # If no MatchID in URL, check if we have a current match
    if not match_id and STATE["current_match_id"]:
        match_id = STATE["current_match_id"]
    
    return match_id

def create_new_match(match_name=None):
    """Create a new match with unique MatchID"""
    if not CRICKET_MODULES_AVAILABLE:
        return {"error": "Cricket modules not available"}
    
    match_id = str(uuid.uuid4())
    match_data = {
        "match": MatchState(),
        "started": False,
        "created_at": datetime.now().isoformat(),
        "match_name": match_name or f"Match {len(STATE['matches']) + 1}",
        "updated_at": datetime.now().isoformat(),
    }
    STATE["matches"][match_id] = match_data
    STATE["current_match_id"] = match_id
    return match_id

def get_current_match(match_id=None):
    """Get current match state"""
    if not match_id:
        match_id = STATE["current_match_id"]
    
    if match_id and match_id in STATE["matches"]:
        return STATE["matches"][match_id]
    
    return None

def serve_main_html():
    """Serve the main CricSmart HTML interface"""
    try:
        with open('static/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>CricSmart - Cricket Scoring</title>
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
            <h1>🏏 CricSmart</h1>
            <h2>Cricket Scoring Application</h2>
        </div>
        <div class="status">
            <h3>✅ Serverless Deployment Successful!</h3>
            <p>CricSmart is running on Vercel serverless functions.</p>
            <p>Cricket modules: <span id="module-status">⏳ Checking...</span></p>
        </div>
        <div class="actions">
            <button class="button" onclick="createMatch()">Create New Match</button>
            <button class="button" onclick="viewMatches()">View Matches</button>
            <button class="button" onclick="checkStatus()">Check Status</button>
        </div>
        <div id="result" class="result"></div>
    </div>
    <script>
        // Check module status on load
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('module-status').innerHTML = data.cricket_modules ? '✅ Available' : '⚠️ Loading...';
            })
            .catch(error => {
                document.getElementById('module-status').innerHTML = '❌ Error checking modules';
            });
        
        async function createMatch() {
            try {
                const response = await fetch('/api/create-match', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({match_name: 'Test Match'})
                });
                const data = await response.json();
                document.getElementById('result').innerHTML = '<h4>New Match Created!</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
        
        async function viewMatches() {
            try {
                const response = await fetch('/api/matches');
                const data = await response.json();
                document.getElementById('result').innerHTML = '<h4>Current Matches:</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('result').innerHTML = '<h4>System Status:</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
        '''

def handler(request):
    """Main CricSmart serverless handler"""
    try:
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        
        print(f"🏏 CricSmart Request: {method} {path}")
        
        # Handle different routes
        if path == '/' or path == '/index.html':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': serve_main_html()
            }
        
        elif path.startswith('/api/status'):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'cricket_modules': CRICKET_MODULES_AVAILABLE,
                    'total_matches': len(STATE['matches']),
                    'current_match_id': STATE['current_match_id'],
                    'message': 'CricSmart serverless is running!'
                })
            }
        
        elif path.startswith('/api/create-match'):
            if method == 'POST':
                # Parse request body
                body = request.get('body', '{}')
                try:
                    data = json.loads(body) if body else {}
                except:
                    data = {}
                
                match_id = create_new_match(data.get('match_name'))
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': True,
                        'match_id': match_id,
                        'message': 'New match created successfully'
                    })
                }
        
        elif path.startswith('/api/matches'):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'matches': STATE['matches'],
                    'current_match_id': STATE['current_match_id'],
                    'total_matches': len(STATE['matches'])
                })
            }
        
        # Default response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'CricSmart API is working!',
                'method': method,
                'path': path,
                'cricket_modules': CRICKET_MODULES_AVAILABLE
            })
        }
        
    except Exception as e:
        print(f"❌ CricSmart Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e),
                'message': 'CricSmart serverless function encountered an error'
            })
        }

# Export for Vercel
app = handler
