# Vercel Python Entry Point
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your app
from app import app

# Vercel serverless handler
def handler(request):
    return app(request)

# Export for Vercel
app = handler
