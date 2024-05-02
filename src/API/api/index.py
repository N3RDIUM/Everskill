# Imports
import os
from flask import Flask, request, jsonify
from firebase_admin import initialize_app, firestore, credentials

# DEV MODE
dev = False

# Initialization stuff
app = Flask(__name__)
creds = "everskill-pk.json"
contents = os.environ['FB_AUTH']
with open(creds, 'w') as f:
    f.write(contents)
cred = credentials.Certificate(creds)
os.remove(creds)
firebase = initialize_app(cred)
db = firestore.client()

# Routing
@app.route("/")
def index():
    return jsonify({
        "response": "Everskill API is up!",
        "success": True
    })

@app.route('/new-user', methods=['POST'])
def new_user():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        })
    
    # Validate username, check if it exists already
    if db.collection('users').document(options['username']).get().exists:
        return jsonify({
            "response": "ERROR: Username already taken.",
            "success": False
        })
        
    # Create user document
    db.collection('users').document(options['username']).set({
        "coins": 100,
        "gems": 10,
        "level": 1,
        "achievements": [],
        "patches": [],
        "profilepic": ''
    })
    
    return jsonify({
        "success": True
    })
    
@app.route('/get-user', methods=['POST'])
def get_user():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        })
        
    # Validate username, error if it doesn't exist
    if not db.collection('users').document(options['username']).get().exists:
        return jsonify({
            "response": "ERROR: Username does not exist.",
            "success": False
        })
    
    return jsonify({
        "response": db.collection('users').document(options['username']).get().to_dict(),
        "success": True
    })

# Driver
if __name__ == "__main__":
    if dev: app.run(debug=True)
