def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'CricSmart is working! 🏏'
    }

app = handler
