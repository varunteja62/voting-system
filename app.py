import os
from flask import Flask
from flask_cors import CORS
from config import Config
from db import init_database
from routes.admin import admin_bp
from routes.voter import voter_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register Blueprints
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(voter_bp, url_prefix='/api')

@app.route('/')
def status():
    return {"status": "running", "message": "Secure Voting System API is online"}

# Initialize database on app startup
init_database()

if __name__ == '__main__':
    # Support Hugging Face port binding
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
