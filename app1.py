#===============================================================================================================
# streamlit based frontend ui with authentication (same as app.py only used streamlit for ui instead of flask)
#===============================================================================================================

import json
import hashlib
import streamlit as st
import subprocess
import os
from playsound import playsound
import speech_recognition as sr
from gtts import gTTS
LANGUAGE = "en"

def SpeakText(command, langinp=LANGUAGE):
    """
    Text to Speech using GTTS

    Args:
        command (str): Text to speak
        langinp (str, optional): Output language. Defaults to "en".
    """
    if langinp == "": langinp = "en"
    tts = gTTS(text=command, lang=langinp)
    tts.save("~tempfile01.mp3")
    playsound("~tempfile01.mp3")
    print(command)
    os.remove("~tempfile01.mp3")

def speech_to_text():
    """
    Speech to text

    Returns:
        str: Returns transcripted text
    """
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

# Main function for the Streamlit web app
def main():
    # Define session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    st.title("Voice-based Email System")

    # Display registration form if not authenticated
    if not st.session_state.authenticated:
        st.sidebar.title("User Registration")
        new_username = st.sidebar.text_input("Enter New Username:")
        new_password = st.sidebar.text_input("Enter New Password:", type="password")
        new_email = st.sidebar.text_input("Enter Email Address:")
        new_email_password = st.sidebar.text_input("Enter Email Password:", type="password")
        if st.sidebar.button("Register"):
            register_user(new_username, new_password, new_email, new_email_password)
            st.sidebar.success("Registration Successful!")
            SpeakText("Registration is successful. Please use our voice based login by clicking on the login button below to use the application")

    if not st.session_state.authenticated:
        st.header("Login")

        # Text input for username and password
        username = st.text_input("Enter Username:", key="uname")
        password = st.text_input("Enter Password:", type="password", key="auth_pword")
        if st.button("Login", key="login"):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login Successful!")

        # Voice login option
        st.header("Voice based login")
        if st.button("Login with Voice"):
            SpeakText("Please say your username")
            username_voice = speech_to_text()
            if username_voice:
                username_voice = username_voice.lower().strip().replace(" ", "")
                st.write("You entered: "+username_voice)
                SpeakText("You entered: "+username_voice)
                SpeakText("Please say your password")
                st.write("Authenticating user Please wait")
                SpeakText("Authenticating user Please wait")
                password_voice = speech_to_text()
                if password_voice:
                    password_voice = password_voice.lower().strip().replace(" ", "")
                    if authenticate_user(username_voice, password_voice):
                        st.session_state.authenticated = True
                        st.session_state.username = username_voice
                        st.success("Login Successful!")
                        SpeakText("Login is successful")
                        SpeakText("Welcome "+ st.session_state.username)
                        SpeakText("Click on start model button to use the email services")
                    else:
                        st.error("Login failed. Please try again with your registered id.")
                        SpeakText("Login failed. Please try again with your registered id.")
                else:
                    st.error("Password not recognized. Please try again.")
                    SpeakText("Password not recognized. Please try again.")
            else:
                st.error("Username not recognized. Please try again.")
                SpeakText("Username not recognized. Please try again.")


    # Display welcome message and other content if authenticated
    if st.session_state.authenticated:
        st.write(f"Welcome {st.session_state.username}!")    
        if st.button("Start ML Model", key="start_model"):
            # Pass email and email_password to speechtext2.py
            email = None
            email_password = None
            with open('users.json', 'r') as file:
                users = json.load(file)
                for user in users:
                    if user["username"] == st.session_state.username:
                        email = user["email"]
                        email_password = user["email_password"]
                        break
            if email and email_password:
                subprocess.run(["python", "speechtext2.py", email, email_password,"en"])
                st.write("ML Model is starting...")
                SpeakText("Model is starting please wait")
            else:
                st.error("User's email or email password not found.")
                SpeakText("User's email or email password not found.")
        if st.button("Logout", key="logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.success("Logout Successful!")
            SpeakText("You have successfully loged out")

if __name__ == "__main__":
    main()
