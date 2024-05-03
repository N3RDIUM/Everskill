# Imports
import os, json
from pywebpush import webpush
from flask import Flask, request, jsonify, render_template
from firebase_admin import initialize_app, firestore, credentials

# DEV MODE
dev = False

# Initialization stuff
app = Flask(__name__)
cred = credentials.Certificate(json.loads(os.environ['FB_AUTH']))
vapid_private_key = os.environ['VAPID_PRIVATE_KEY']
firebase = initialize_app(cred)
db = firestore.client()

# Routing
@app.route("/")
def index():
    return jsonify({
        "response": "Everskill API is up!",
        "success": True
    })
    
@app.route('/subscribe-push')
def subscribe_push():
    return render_template('subscribe.html')

# TODO! Check for an auth token in POST routes
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
        "profilepic": '',
        'courses': []
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
    
@app.route('/subscribe-pushnotify', methods=['POST'])
def sub_push():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        })
        
    if 'subscription' not in options:
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
        
    # Add subscription to user
    db.collection('users').document(options['username']).update({
        "webpush": options['subscription']
    })
    
    return jsonify({
        "success": True
    })
    
@app.route('/subscribe-course', methods=['POST'])
def sub_course():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        })
        
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        })
        
    # Validate username, error if it doesn't exist
    if not db.collection('users').document(options['username']).get().exists:
        return jsonify({
            "response": "ERROR: Username does not exist.",
            "success": False
        })
        
    # Validate course id, error if it doesn't exist
    if not db.collection('courses').document(options['course_id']).get().exists:
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        })
        
    # Add the course ID to the user's list of courses
    courses = db.collection('users').document(options['username']).get().to_dict()['courses']
    db.collection('users').document(options['username']).update({
        "courses": courses + [options['course_id']]
    })
    
    
    # Send a notification if the user has subscribed to notifications
    if 'webpush' in db.collection('users').document(options['username']).get().to_dict():
        course_title = db.collection('courses').document(options['course_id']).get().to_dict()['title']
        webpush(
            db.collection('users').document(options['username']).get().to_dict()['webpush'],
            f"Welcome aboard! You have successfully subscribed to the course: {course_title}",
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": "https://everskill.vercel.app/"}
        )
    
    return jsonify({
        "success": True
    })

@app.route('/unsubscribe-course', methods=['POST'])
def unsub_course():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        })
        
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        })
        
    # Validate username, error if it doesn't exist
    if not db.collection('users').document(options['username']).get().exists:
        return jsonify({
            "response": "ERROR: Username does not exist.",
            "success": False
        })
        
    # Validate course id, error if it doesn't exist
    if not db.collection('courses').document(options['course_id']).get().exists:
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        })
        
    # Validate that the user has subscribed to this course
    courses = db.collection('users').document(options['username']).get().to_dict()['courses']
    if options['course_id'] not in courses:
        return jsonify({
            "response": "ERROR: The user is not subscribed to this course.",
            "success": False
        })
        
    # Remove the course ID from the user's list of courses
    db.collection('users').document(options['username']).update({
        "courses": courses + [options['course_id']]
    })
    
    # Send a notification if the user has subscribed to notifications
    if 'webpush' in db.collection('users').document(options['username']).get().to_dict():
        course_title = db.collection('courses').document(options['course_id']).get().to_dict()['title']
        webpush(
            db.collection('users').document(options['username']).get().to_dict()['webpush'],
            f"Sorry to see you go! You have successfully unsubscribed from the course: {course_title}",
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": "https://everskill.vercel.app/"}
        )
    
    return jsonify({
        "success": True
    })

# Driver
if __name__ == "__main__":
    if dev: app.run(debug=True)
