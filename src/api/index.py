# Imports
from hashlib import sha256
from pywebpush import webpush
import os, json, uuid, bleach, requests
from flask import Flask, request, jsonify, render_template
from firebase_admin import initialize_app, firestore, credentials

# DEV MODE
dev = 'dev' in os.environ

# Initialization stuff
app = Flask(__name__)
cred = credentials.Certificate(json.loads(os.environ['FB_AUTH']))
vapid_private_key = os.environ['VAPID_PRIVATE_KEY']
firebase = initialize_app(cred)
db = firestore.client()

# Course class because why not
# TODO! Use the html sanitizer!
class Course:
    def __init__(self, url: str, id: str) -> None:
        self.url = url
        self.details = json.loads(requests.get(self.url).text)
        self.quizzes = json.loads(requests.get(self.details["quizzes"]).text)
        self.achievements = json.loads(requests.get(self.details["achievements"]).text)
                
        # This is just for search!
        db.collection('course-soup').document(str(sha256(url.encode()).hexdigest())).set({
            "soup": str(self.details['title'] + ' ' + self.details['description'] + ' ' + ' '.join(self.details['tags'])).lower(),
            "url": url,
            "id": id
        })

    def render(self, page: str = 'home') -> list:
        page = self.details['pages'][page]
        source = requests.get(page['html']).text
        ret = bleach.linkify(source)
        
        return page, ret
    
    def get_quiz(self, id) -> dict:
        ret = self.quizzes[id]
        
        for i in range(len(ret['questions'])):
            ret['questions'][i]['answers'] = 'no cheating!!'
        
        return ret
        
    def verify_answer(self, qid, idx, ans) -> bool:
        return self.quizzes[qid]['questions'][int(idx)]['answer'] == ans
    def is_last_question(self, qid, idx) -> bool:
        return int(idx) >= len(self.quizzes[qid]['questions'])
    
    def coins(self, qid, idx) -> int:
        return int(self.quizzes[qid]['questions'][int(idx)]['coins'])
    def gems(self, qid) -> int:
        return int(self.quizzes[qid]['gems'])
        
# Functions
def user_exists(username):
    return db.collection('users').document(username).get().exists

def new_token(username, password):
    token = str(uuid.uuid4())
    db.collection('creds').document(username).set({
        "token": token,
        "password-hash": password
    })
    return token

def validate_password(username, password):
    return db.collection('creds').document(username).get().to_dict()['password-hash'] == password

def get_token(username):
    return db.collection('creds').document(username).get().to_dict()['token']

def validate_token(username, token):
    return db.collection('creds').document(username).get().to_dict()['token'] == token

def course_exists(course_id):
    return db.collection('courses').document(course_id).get().exists

def search(ref, query):
    ret = []
    inp = query.lower().split(' ')
    for i in inp:
        # TODO! Implement relevance score thingy / add another layer of fuzzy searching!
        ret.extend([x for x in ref.where("soup", ">=", i).where("soup", "<=", i + '\uf8ff').stream()])
        
    return [{"url": x.to_dict()['url'], "id": x.to_dict()['id']}for x in ret]

# Routing
# TODO! Reduce the amount of duplicate firestore queries you make for speed and price reduction
@app.route('/api/new-user/', methods=['POST'])
def new_user():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        }), 400
    if 'password' not in options:
        return jsonify({
            "response": "ERROR: Password hash not provided!",
            "success": False
        }), 400
    
    # Validate username, check if it exists already
    if user_exists(options['username']):
        return jsonify({
            "response": "ERROR: Username already taken.",
            "success": False
        }), 400
        
    # Create a new auth token and add it to the creds database
    token = new_token(options['username'], options['password'])
    
    # Create user document
    db.collection('users').document(options['username']).set({
        "coins": 100,
        "gems": 10,
        "level": 1,
        "achievements": [],
        "patches": [],
        "profilepic": '',
        "bio": '',
        'courses': [],
        "interests": []
    })
    
    return jsonify({
        "success": True,
        "token": token
    }), 200
    
@app.route('/api/signin-upass/', methods=['POST'])
def sign_in():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided!",
            "success": False
        }), 400
    if 'password' not in options:
        return jsonify({
            "response": "ERROR: Password hash not provided!",
            "success": False
        }), 400
        
    # Validate whether the password hash is right
    if not validate_password(options['username'], options['password']):
        return jsonify({
            "response": "ERROR: Incorrect password!",
            "success": False
        }), 400
    
    # Use existing auth token
    token = get_token(options['username'])
    
    # Return the auth token
    return jsonify({
        "success": True,
        "token": token
    }), 200

@app.route('/api/get-user/', methods=['POST'])
def get_user():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        }), 400
        
    # Validate username, error if it doesn't exist
    if not db.collection('users').document(options['username']).get().exists:
        return jsonify({
            "response": "ERROR: Username does not exist.",
            "success": False
        }), 400
    
    return jsonify({
        "response": db.collection('users').document(options['username']).get().to_dict(),
        "success": True
    }), 200
    
@app.route('/api/subscribe-pushnotify/', methods=['POST'])
def sub_push():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        }), 400
    if 'token' not in options:
        return jsonify({
            "response": "ERROR: Auth token not provided.",
            "success": False
        }), 400
    if 'subscription' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "s, 400uccess": False
        })
        
    # Validate auth token
    if not validate_token(options['username'], options['token']):
        return jsonify({
            "response": "ERROR: Invalid auth token.",
        }), 400
        
    # Validate username, error if it doesn't exist
    if not user_exists(options['username']):
        return jsonify({
            "response": "ERROR: Username does not exist.",
            "success": False
        }), 400
        
    # Add subscription to user
    db.collection('creds').document(options['username']).update({
        "webpush": options['subscription']
    })
    
    webpush(
        json.loads(str(db.collection('creds').document(options['username']).get().to_dict()['webpush'])),
        json.dumps({
            "body": 'Welcome aboard! You have successfully subscribed to push notifications.',
            "icon": '../icons/owl.svg',
            "title": 'Everskill Notification'
        }),
        vapid_private_key=vapid_private_key,
        vapid_claims={"sub": "mailto:n3rdium@gmail.com"}
    )
    
    return jsonify({
        "success": True
    }), 200
    
@app.route('/api/subscribe-course/', methods=['POST'])
def sub_course():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        }), 400
    if 'token' not in options:
        return jsonify({
            "response": "ERROR: Auth token not provided.",
            "success": False
        }), 400
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        }), 400
        
    # Validate auth token
    if not validate_token(options['username'], options['token']):
        return jsonify({
            "response": "ERROR: Invalid auth token.",
        }), 400
        
    # Validate username, error if it doesn't exist
    if not user_exists(options['username']):
        return jsonify({
            "response": "ERROR: Username does not exist.",
            "success": False
        }), 400
        
    # Validate course id, error if it doesn't exist
    if not course_exists(options['course_id']):
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        }), 400
        
    # Add the course ID to the user's list of courses
    courses = db.collection('users').document(options['username']).get().to_dict()['courses']
    db.collection('users').document(options['username']).update({
        "courses": courses + [options['course_id']]
    })
    
    # Send a notification if the user has subscribed to notifications
    if 'webpush' in db.collection('creds').document(options['username']).get().to_dict():
        course_title = db.collection('courses').document(options['course_id']).get().to_dict()['title']
        webpush(
            json.loads(str(db.collection('creds').document(options['username']).get().to_dict()['webpush'])),
            json.dumps({
                "body": f"Welcome aboard! You have successfully subscribed to the course: {course_title}",
                "icon": '../icons/owl.svg',
                "title": 'Everskill Notification'
            }),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": "https://everskill.vercel.app/"}
        )
    
    return jsonify({
        "success": True
    }), 200

@app.route('/api/unsubscribe-course/', methods=['POST'])
def unsub_course():
    options = request.get_json()
    
    # Check request
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        }), 400
    if 'token' not in options:
        return jsonify({
            "response": "ERROR: Auth token not provided.",
            "success": False
        }), 400
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        }), 400
        
    # Validate auth token
    if not validate_token(options['username'], options['token']):
        return jsonify({
            "response": "ERROR: Invalid auth token.",
        }), 400
        
    # Validate username, error if it doesn't exist
    if not user_exists(options['username']):
        return jsonify({
            "response": "ERROR: Username does not exist.",
            "success": False
        }), 400
        
    # Validate course id, error if it doesn't exist
    if not course_exists(options['course_id']):
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        }), 400
        
    # Validate that the user has subscribed to this course
    courses = db.collection('users').document(options['username']).get().to_dict()['courses']
    if options['course_id'] not in courses:
        return jsonify({
            "response": "ERROR: The user is not subscribed to this course.",
            "success": False
        }), 400
        
    # Remove the course ID from the user's list of courses
    db.collection('users').document(options['username']).update({
        "courses": courses + [options['course_id']]
    })
    
    # Send a notification if the user has subscribed to notifications
    if 'webpush' in db.collection('creds').document(options['username']).get().to_dict():
        course_title = db.collection('courses').document(options['course_id']).get().to_dict()['title']
        webpush(
            json.loads(str(db.collection('creds').document(options['username']).get().to_dict()['webpush'])),
            json.dumps({
                "body": f"Sorry to see you go! You have successfully unsubscribed from the course: {course_title}",
                "icon": '../icons/owl.svg',
                "title": 'Everskill Notification'
            }),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": "https://everskill.vercel.app/"}
        )
    
    return jsonify({
        "success": True
    }), 200
    
@app.route('/api/course-render/', methods=['POST'])
def course_render():
    # Validate request
    options = request.get_json()
    
    # Check request
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        }), 400
    if 'page' not in options:
        options['page'] = 'home'
    
    # Validate course existence
    if not course_exists(options["course_id"]):
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        }), 400
    
    # Fetch course metadata
    course_meta = db.collection('courses').document(options["course_id"]).get().to_dict()['metadata']
    course = Course(course_meta, options["course_id"])
    details = course.details
    
    # Return it
    return jsonify({
        "success": True,
        "details": details,
        "render": course.render(options["page"])
    })
    
@app.route('/api/quiz-get/', methods=['POST'])
def get_quiz():
    # Validate request
    options = request.get_json()
    
    # Check request
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        }), 400
    if 'quiz_id' not in options:
        return jsonify({
            "response": "ERROR: Quiz ID not provided.",
            "success": False
        }), 400
        
    # Validate course existence
    if not course_exists(options["course_id"]):
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        }), 400
        
    # Fetch course metadata
    course_meta = db.collection('courses').document(options["course_id"]).get().to_dict()['metadata']
    course = Course(course_meta, options["course_id"])
    quiz = course.get_quiz(options["quiz_id"])
    
    # Return it
    return jsonify({
        "success": True,
        "quiz": quiz
    })
    
@app.route('/api/quiz-check/', methods=['POST'])
def check_answer():
    # Validate request
    options = request.get_json()
    
    # Check request
    if 'course_id' not in options:
        return jsonify({
            "response": "ERROR: Course ID not provided.",
            "success": False
        }), 400
    if 'quiz_id' not in options:
        return jsonify({
            "response": "ERROR: Quiz ID not provided.",
            "success": False
        }), 400
    if 'question_index' not in options:
        return jsonify({
            "response": "ERROR: Question index not provided.",
            "success": False
        }), 400
    if 'answer_index' not in options:
        return jsonify({
            "response": "ERROR: Answer index not provided.",
            "success": False
        }), 400
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Username not provided.",
            "success": False
        }), 400
    if 'token' not in options:
        return jsonify({
            "response": "ERROR: Auth token not provided.",
            "success": False
        }), 400
    
    # Validate course existence
    if not course_exists(options["course_id"]):
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        }), 400
        
    # Validate auth token
    token = db.collection('creds').document(options['username']).get().to_dict()['token']
    if token != options['token']:
        return jsonify({
            "response": "ERROR: Invalid auth token.",
            "success": False
        }), 400
        
    # Fetch course metadata
    course_meta = db.collection('courses').document(options["course_id"]).get().to_dict()['metadata']
    course = Course(course_meta, options["course_id"])
    coins = course.coins(options['quiz_id'], options['question_index'])
    gems = course.gems(options['quiz_id'])
    correct = course.verify_answer(options['quiz_id'], options['question_index'], options['answer_index'])
    
    # Add coins to the user profile if the answer is correct
    if correct:
        db.collection('users').document(options['username']).update({
            "coins": int(db.collection('users').document(options['username']).get().to_dict()['coins']) + coins
        })
        if course.is_last_question(options['quiz_id'], options['answer_index']):
            # Add gems to the user profile if the answer is correct
            if correct:
                db.collection('users').document(options['username']).update({
                    "gems": int(db.collection('users').document(options['username']).get().to_dict()['gems']) + gems
                })
    
    # Return it
    return jsonify({
        "success": True,
        "check": correct
    })

@app.route('/api/course-search/', methods=['POST'])
def search_course():
    # Validate request
    options = request.get_json()
    if 'query' not in options:
        return jsonify({
            "response": "ERROR: Query not provided.",
            "success": False
        }), 400
        
    # Search for courses
    ref = db.collection("course-soup")
    res = search(ref, options['query'])
    
    # Return the results
    return jsonify({
        "results": res,
        "success": True
    })

@app.route('/api/user-profile/', methods=['POST'])
def api_profile():
    # Validate request
    options = request.get_json()
    if 'username' not in options:
        return jsonify({
            "response": "ERROR: Query not provided.",
            "success": False
        }), 400
    
    # Check if the profile exists
    if not db.collection('users').document(options['username']).get().exists:
        return jsonify({
            "response": "ERROR: User does not exist.",
            "success": False
        }), 400
        
    # Return the profile
    return jsonify({
        "profile": db.collection('users').document(options['username']).get().to_dict(),
        "success": True
    })

# Templates routing
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/signup/")
def signup():
    return render_template('signup.html')

@app.route("/signin/")
def signin():
    return render_template('signin.html')

@app.route('/subscribe/')
def subscribe():
    return render_template('subscribe.html')

@app.route('/course-view/<string:course_id>/')
def view_course(course_id):
    # Get course details
    if not db.collection('courses').document(course_id).get().exists:
        return jsonify({
            "response": "ERROR: Course ID is invalid.",
            "success": False
        }), 400
    
    return render_template(
        "course-view.html",
        course_id=course_id
    )

@app.route('/search/')
def search_ui():
    return render_template('search.html')

@app.route('/user/<string:username>/')
def profile(username):
    return render_template('profile.html', u=username)

# Driver
if __name__ == "__main__":
    if dev: app.run(debug=True, port=5050)
