# Vercel serverless handler
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import handler

# Export for Vercel
def app(request):
    return handler(request)
