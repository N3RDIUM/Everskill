# Imports
import os, json, uuid
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

# TODO! Make functions for repetitive tasks!!
@app.route('/new-user', methods=['POST'])
def new_user():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        })
    if 'password-hash' not in options:
        return jsonify({
            "response": "ERROR: Password hash not provided!",
            "success": False
        })
    
    # Validate username, check if it exists already
    if db.collection('users').document(options['username']).get().exists:
        return jsonify({
            "response": "ERROR: Username already taken.",
            "success": False
        })
        
    # Create a new auth token and add it to the creds database
    token = str(uuid.uuid4())
    db.collection('creds').document(options['username']).set({
        "token": token,
        "password-hash": options['password-hash']
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
        "success": True,
        "token": token
    })
    
@app.route('/signin-upass', methods=['POST'])
def sign_in():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided!",
            "success": False
        })
    if 'password-hash' not in options:
        return jsonify({
            "response": "ERROR: Password hash not provided!",
            "success": False
        })
        
    # Validate whether the password hash is right
    actual = db.collection('creds').document(options['username']).get().to_dict()['password-hash']
    if actual != options['password-hash']:
        return jsonify({
            "response": "ERROR: Incorrect password!",
            "success": False
        })
    
    # Create an auth token for this user
    token = str(uuid.uuid4())
    db.collection('creds').document(options['username']).update({
        "token": token
    })
    
    # Return the auth token
    return jsonify({
        "success": True,
        "token": token
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
    if 'token' not in options:
        return jsonify({
            "response": "ERROR: Auth token not provided.",
            "success": False
        })
    if 'subscription' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        })
        
    # Validate auth token
    token = db.collection('users').document(options['username']).get()['token']
    if token != options['auth']:
        return jsonify({
            "response": "ERROR: Invalid auth token.",
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
    
    webpush(
        json.loads(str(db.collection('users').document(options['username']).get().to_dict()['webpush'])),
        json.dumps({
            "body": 'Welcome aboard! You have successfully subscribed to push notifications.',
            "title": 'Everskill Notification'
        }),
        vapid_private_key=vapid_private_key,
        vapid_claims={"sub": "mailto:n3rdium@gmail.com"}
    )
    
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
    if 'token' not in options:
        return jsonify({
            "response": "ERROR: Auth token not provided.",
            "success": False
        })
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        })
        
    # Validate auth token
    token = db.collection('users').document(options['username']).get()['token']
    if token != options['token']:
        return jsonify({
            "response": "ERROR: Invalid auth token.",
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
            json.loads(str(db.collection('users').document(options['username']).get().to_dict()['webpush'])),
            json.dumps({
                "body": f"Welcome aboard! You have successfully subscribed to the course: {course_title}",
                "title": 'Everskill Notification'
            }),
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
    if 'token' not in options:
        return jsonify({
            "response": "ERROR: Auth token not provided.",
            "success": False
        })
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        })
        
    # Validate auth token
    token = db.collection('users').document(options['username']).get()['token']
    if token != options['token']:
        return jsonify({
            "response": "ERROR: Invalid auth token.",
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
            json.loads(str(db.collection('users').document(options['username']).get().to_dict()['webpush'])),
            json.dumps({
                "body": f"Sorry to see you go! You have successfully unsubscribed from the course: {course_title}",
                "title": 'Everskill Notification'
            }),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": "https://everskill.vercel.app/"}
        )
    
    return jsonify({
        "success": True
    })

# Driver
if __name__ == "__main__":
    if dev: app.run(debug=True)
