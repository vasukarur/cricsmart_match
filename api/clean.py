def handler(request):
    """Clean Vercel serverless handler"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': '''
<!DOCTYPE html>
<html>
<head>
    <title>CricSmart - Cricket Scoring</title>
</head>
<body>
    <h1>🏏 CricSmart is Working!</h1>
    <p>Serverless function deployed successfully!</p>
    <p>Time to integrate the full cricket scoring app...</p>
</body>
</html>
        '''
    }

# Export for Vercel
app = handler
