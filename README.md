# Voice based Email System
This project focuses on the development of a user-friendly application tailored specifically for visually impaired individuals. The application leverages voice commands to enable users to send emails, check email status, search through messages, and read inbox content, all without the need for visual interaction. 
This project uses Whisper model for speech to text conversion and GTTS library to vocalize text response, thus facilitating a voice based interaction with users.

## Technology used
1. Whisper Model
2. gTTs library
3. Python
4. Flask
5. HTML/ CSS/ JS

## Workflow
![image](https://github.com/user-attachments/assets/ee683467-2cee-4838-acd8-f220a77603a1)

1. User Registration
   Enable 2-step verification in gmail and generate app password then use your email id and generated app password along with username and password of your choice for registration.
2. Login with voice
   Users can login by speaking their id and password which is matched with hashed password for authentication.
3. Voice based response
   gTTs python library is used to convert text to speech in order to provide voice based response.
4. Audio Recording
   * The app uses PyAudio to record audio in WAV format which continues till user press space bar.
   * Audio parameters: 16-bit PCM, mono channel, 44.1 kHz sample rate.
5. Speech to Text Conversion
   The app uses the Whisper tiny.en model for English transcription (ie. converting voice to text)
6. Email functionalities
   * __Compose and Send Email:__ Users can dictate emails, which are confirmed and sent securely using Gmail's SMTP server.
   * __Mailbox Status:__ The app retrieves the status of email folders via IMAP, announcing the number of messages in each.
   * __Search Email:__ Users can search emails by criteria like sender or subject, with results read aloud or skipped as desired.
   * __Retrieve Latest Emails:__ Users can fetch and summarize the latest emails from selected folders. Summaries are created using NLTK python library.

## Acknowledgements
[Ronik22](https://github.com/Ronik22)
