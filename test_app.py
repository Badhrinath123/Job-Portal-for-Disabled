from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Flask Test - Success!</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 15px;
                max-width: 600px;
                margin: 0 auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Flask is Working!</h1>
            <p>Your Flask application is running successfully!</p>
            <p>The issue was with MySQL database connection, not Flask itself.</p>
            <h3>Next Steps:</h3>
            <ul style="text-align: left;">
                <li>Install MySQL database</li>
                <li>Configure database connection</li>
                <li>Run your full application</li>
            </ul>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Flask test app starting...")
    print("📱 Local access: http://127.0.0.1:5000")
    print("🌐 Network access: http://0.0.0.0:5000")
    print("💡 Other devices can access using your computer's IP address")
    app.run(debug=True, host='0.0.0.0', port=5000)
