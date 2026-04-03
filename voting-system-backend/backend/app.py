import os
from flask import Flask
from flask_cors import CORS
from config import Config
from db import init_database
from routes.admin import admin_bp
from routes.voter import voter_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})

# Register Blueprints
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(voter_bp, url_prefix='/api')

@app.route('/')
def status():
    return {"status": "running", "message": "Secure Voting System API is online"}

if __name__ == '__main__':
    init_database()
    # Port 7860 is required for Hugging Face Spaces
    port = int(os.environ.get("PORT", 7860))
    app.run(debug=True, host='0.0.0.0', port=port)
