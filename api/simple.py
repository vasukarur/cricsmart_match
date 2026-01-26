def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'Hello from CricSmart!'
    }

# Vercel expects the function to be named 'handler' or exported as 'app'
app = handler
