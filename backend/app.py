import os
from flask import Flask
from flask_cors import CORS
from config import Config
from db import init_database
from routes.admin import admin_bp
from routes.voter import voter_bp

import numpy as np
import json

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

app = Flask(__name__)
app.config.from_object(Config)
app.json.cls = NpEncoder
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
