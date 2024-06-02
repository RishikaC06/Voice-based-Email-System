from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import hashlib
import subprocess
import os
from playsound import playsound
import speech_recognition as sr
from gtts import gTTS
LANGUAGE = "en"

app = Flask(__name__)

def SpeakText(command, langinp=LANGUAGE):
    if langinp == "": langinp = "en"
    tts = gTTS(text=command, lang=langinp)
    tts.save("tempfile02.mp3")
    playsound("tempfile02.mp3")
    print(command)
    os.remove("tempfile02.mp3")

def speech_to_text():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source2:
            r.adjust_for_ambient_noise(source2, duration=0.2)
            audio2 = r.listen(source2)
            MyText = r.recognize_google(audio2)
            print("You said: "+MyText)
            return MyText

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None

    except sr.UnknownValueError:
        print("unknown error occured")
        return None

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if the entered credentials match the registered user
def authenticate_user(username, password):
    with open('users.json', 'r') as file:
        users = json.load(file)
        for user in users:
            if user["username"] == username and user["hashed_password"] == hash_password(password):
                return True
    return False

# Function to register a new user
def register_user(username, password, email, email_password):
    new_user = {
        "username": username,
        "hashed_password": hash_password(password),
        "email": email,
        "email_password": email_password
    }
    with open('users.json', 'r+') as file:
        users = json.load(file)
        users.append(new_user)
        file.seek(0)
        json.dump(users, file, indent=4)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    email_password = request.form['email_password']
    register_user(username, password, email, email_password)
    SpeakText("Registration is successful. Click on start model to use the application")
    return redirect(url_for('dashboard', username=username))

@app.route('/dashboard/<username>')
def dashboard(username):
    wel_msg = "Welcome " + username
    SpeakText(wel_msg)  
    SpeakText("Click on start model to use the application")
    return render_template('dashboard.html', welcome_message=wel_msg,username=username)

@app.route('/login_with_voice', methods=['POST'])
def login_with_voice():
    if request.method == 'POST':
        SpeakText("Please say your username")
        username_voice = speech_to_text()
        if username_voice:
            username_voice = username_voice.lower().strip().replace(" ", "")
            SpeakText("Please say your password")
            password_voice = speech_to_text()
            if password_voice:
                password_voice = password_voice.lower().strip().replace(" ", "")
                if authenticate_user(username_voice, password_voice):
                    SpeakText("Authentication is successful. Click on start model to use the application")
                    # Redirect to the dashboard page with the username
                    return redirect(url_for('dashboard', username=username_voice))
                else:
                    error_message = "Login failed. Please try again with your registered id."
                    SpeakText("Login failed. Please try again with your registered id.")
                    return jsonify({"error": error_message}) 
            else:
                error_message = "Password not recognized. Please try again."
                SpeakText("Password not recognized. Please try again.")
                return jsonify({"error": error_message}) 
        else:
            error_message = "Username not recognized. Please try again."
            SpeakText("Username not recognized. Please try again.")
            return jsonify({"error": error_message}) 
    else:
        # Handle GET request if needed
        pass

@app.route('/start_model', methods=['POST'])
def start_model():
    # username = request.args.get('username')
    print("Received form data:", request.form)  # Add logging to check form data
    username = request.form.get('username')
    print("Received username:", username)
    email = None
    email_password = None
    with open('users.json', 'r') as file:
        users = json.load(file)
        for user in users:
            if user["username"] == username:
                email = user["email"]
                email_password = user["email_password"]
                break
    print(username)
    print(email)
    print(email_password)
    if email and email_password:
        subprocess.run(["python", "speechtext2.py", email, email_password, "en"])
        return "ML Model is starting..."
    else:
        return "User's email or email password not found."

@app.route('/logout', methods=['POST'])
def logout():
    # Redirect the user to the root URL (index.html)
    SpeakText("You have successfully logged out")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True,port=8000)
