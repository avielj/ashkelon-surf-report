def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>IT WORKS!</h1><p>Vercel Python is running</p>'
    }
