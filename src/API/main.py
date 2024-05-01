# Imports
import os
from flask import Flask

# Get the Firebase config from environment variables
config = {
    "apiKey": os.environ["FIREBASE_API_KEY"],
    "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
    "databaseURL": os.environ["FIREBASE_DATABASE_URL"],
    "projectId": os.environ["FIREBASE_PROJECT_ID"],
    "storageBucket": os.environ["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": os.environ["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": os.environ["FIREBASE_APP_ID"],
    "measurementId": os.environ["FIREBASE_MEASUREMENT_ID"]
}

# App stuff
app = Flask(__name__)

# Routing
@app.route("/")
def index():
    return "Everskill API is up!"

# Driver
if __name__ == "__main__":
    app.run()
