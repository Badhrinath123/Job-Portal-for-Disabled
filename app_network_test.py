from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'secret_key_here'  # Add a secret key for session

@app.route('/', methods=['POST','GET'])
def index():
    return '''
    <html>
    <head>
        <title>Flask Network Test - Success!</title>
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
            .ip-info {
                background: rgba(255,255,255,0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Flask Network Access Test</h1>
            <p>Your Flask application is accessible from other devices!</p>
            
            <div class="ip-info">
                <h3>📱 Access Instructions:</h3>
                <p><strong>Local access:</strong> http://127.0.0.1:5000</p>
                <p><strong>Network access:</strong> http://YOUR_IP_ADDRESS:5000</p>
                <p><em>Replace YOUR_IP_ADDRESS with your computer's actual IP</em></p>
            </div>
            
            <h3>✅ Network Test Successful!</h3>
            <p>If you can see this page from another device, your Flask app is properly configured for network access.</p>
            
            <div style="margin-top: 30px;">
                <h4>🔧 Next Steps:</h4>
                <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                    <li>Install and configure MySQL database</li>
                    <li>Update database connection settings</li>
                    <li>Run your full application with database features</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'Flask app is accessible from network',
        'server_info': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': True
        }
    })

if __name__ == '__main__':
    print("🚀 Flask network test app starting...")
    print("📱 Local access: http://127.0.0.1:5000")
    print("🌐 Network access: http://0.0.0.0:5000")
    print("💡 Other devices can access using your computer's IP address")
    print("🔧 Test endpoint: http://YOUR_IP:5000/test")
    app.run(debug=True, host='0.0.0.0', port=5000)