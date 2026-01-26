# Ultra minimal test - no imports, no complexity
def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'Minimal test working!'
    }

app = handler
