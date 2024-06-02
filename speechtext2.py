import os
import sys
from playsound import playsound
import whisper
import pyaudio
import wave
from gtts import gTTS
import os
from playsound import playsound
import smtplib
import email
import imaplib
from email.header import decode_header

import keyboard
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
# from CONSTANTS import EMAIL_ID, PASSWORD, LANGUAGE
# from CONSTANTS_dev import EMAIL_ID, PASSWORD, LANGUAGE
EMAIL_ID = sys.argv[1]
PASSWORD = sys.argv[2]
LANGUAGE = sys.argv[3]

def SpeakText(command, langinp=LANGUAGE):
    if langinp == "": langinp = "en"
    tts = gTTS(text=command, lang=langinp)
    tts.save("~tempfile01.mp3")
    print(command)
    playsound("~tempfile01.mp3")
    os.remove("~tempfile01.mp3")

def speech_to_text():
    output_wav_file = "com.wav"
    audio=record_audio(output_wav_file)
    text=predict_output(audio)
    os.remove(output_wav_file)
    return text

def edit(choice):
    symbols = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        # Remove symbols from the word
    text= ''.join(char for char in choice if char not in symbols)
        # print(choice)
        # print(type(choice))
    choice = text.lower().strip()  # Convert choice to lowercase for case-insensitive comparison
    print("Recognized choice:", choice) 
    return choice

def record_audio(output_file, sample_rate=44100, channels=1, chunk=1024):
    audio = pyaudio.PyAudio()

    # Open stream
    stream = audio.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk)

    print("Recording... (Press 'Space' to stop)")

    frames = []
    try:
        # Record audio until 'space' is pressed
        while True:
            data = stream.read(chunk)
            frames.append(data)
            if keyboard.is_pressed('space'):  # Check if 'Space' is pressed
                break
    except KeyboardInterrupt:  # Handle keyboard interrupt (Ctrl+C)
        pass

    print("Recording finished.")

    # Stop stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save audio to file
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Audio saved as", output_file)
    return output_file

def predict_output(audio):
    model = whisper.load_model("tiny.en")
    result = model.transcribe(audio)
    # result = model.translate("hindi.wav")
    # print(result["text"])
    return result["text"]

def sendMail(sendTo, msg):
    mail = smtplib.SMTP('smtp.gmail.com', 587)  # host and port
    # Hostname to send for this command defaults to the FQDN of the local host.
    mail.ehlo()
    mail.starttls()  # security connection
    mail.login(EMAIL_ID, PASSWORD)  # login part
    for person in sendTo:
        mail.sendmail(EMAIL_ID, person, msg)  # send part
        print("Mail sent successfully to " + person)
    mail.close()

def composeMail():
    while True:  # Keep looping until email IDs are confirmed or user cancels
        SpeakText("Mention the Gmail IDs of the persons to whom you want to send an email. Email IDs should be separated with the word 'AND'.")
        SpeakText("Speak Now")
        # receivers = speech_to_text(duration=10)
        receivers = speech_to_text()
        receivers = receivers.replace("at the rate", "@")
        receivers = receivers.lower().strip()
        print("Recognized choice:", receivers)
        emails = receivers.split(" and ")

        index = 0
        for email in emails:
            emails[index] = email.replace(" ", "")
            index += 1

        SpeakText("The email will be sent to " + (' and '.join([str(elem) for elem in emails])) + ". Confirm by saying YES or NO.")
        SpeakText("Speak Now")
        # c = speech_to_text(duration=2)
        c = speech_to_text()
        confirmMailList = edit(c)

        if confirmMailList == "no" or confirmMailList == "noo":
            SpeakText("Do you want to re-enter the email IDs? Say YES or NO.")
            SpeakText("Speak Now")
            # retry = speech_to_text(duration=2)
            retry = speech_to_text()
            retry=edit(retry)
            if retry in ["no", "noo"]:
                SpeakText("Operation cancelled by the user.")
                return None
            elif retry in ["yes", "yess"]:
                continue
            else:
                SpeakText("Failed to recognize your choice. Cancelling operation.")
                return None

        if confirmMailList == "yes" or confirmMailList == "yess":
            break  # Break the loop if email IDs are confirmed

    SpeakText("Say your message")
    # msg = speech_to_text(duration=10)
    msg = speech_to_text()

    SpeakText("You said, " + msg + ". Confirm by saying YES or NO.")
    # confirmMailBody = speech_to_text(duration=2)
    confirmMailBody = speech_to_text()
    confirmMailBody = edit(confirmMailBody)
    if confirmMailBody == "yes" or confirmMailBody == "yess":
        SpeakText("Message sent")
        sendMail(emails, msg)
    else:
        SpeakText("Operation cancelled by the user")
        return None

def getMailBoxStatus():
    # host and port (ssl security)
    M = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    M.login(EMAIL_ID, PASSWORD)  # login

    for i in M.list()[1]:
        l = i.decode().split(' "/" ')
        if l[1] == '"[Gmail]"':
            continue

        stat, total = M.select(f'{l[1]}')
        l[1] = l[1][1:-1]
        messages = int(total[0])
        if l[1] == 'INBOX':
            SpeakText(l[1] + " has " + str(messages) + " messages.")
        else:
            SpeakText(l[1].split("/")[-1] + " has " + str(messages) + " messages.")

    M.close()
    M.logout()

def clean(text):
    """
    clean text for creating a folder
    """
    return "".join(c if c.isalnum() else "_" for c in text)

def getLatestMails():
    """
    Get latest mails from folders in mailbox (Defaults to 3 Inbox mails)
    """
    mailBoxTarget = "INBOX"
    SpeakText("Choose the folder name to get the latest mails. Say 1 for Inbox. Say 2 for Sent Mailbox. Say 3 for Drafts. Say 4 for important mails. Say 5 for Spam. Say 6 for Starred Mails. Say 7 for Bin.")
    SpeakText("Speak Now")
    # cmb = speech_to_text(duration=2)
    cmb = speech_to_text()
    cmb=edit(cmb)
    if cmb == "1" or cmb == "one" or cmb == "oneh" or cmb == "fun" or cmb == "o n e":
        mailBoxTarget = "INBOX"
        SpeakText("Inbox selected.")
    elif cmb == "2" or cmb == "two" or cmb == "tu" or cmb == "do" or cmb == "twoh" or cmb == "tuh" or cmb == "to" or cmb == "t w o" or cmb == "too":
        mailBoxTarget = '"[Gmail]/Sent Mail"'
        SpeakText("Sent Mailbox selected.")
    elif cmb == "3" or cmb == "three" or cmb == "tree" or cmb=="t h r e e":
        mailBoxTarget = '"[Gmail]/Drafts"'
        SpeakText("Drafts selected.")
    elif cmb == "4" or cmb == "four" or cmb == "fore" or cmb == "for" or cmb=="f o u r":
        mailBoxTarget = '"[Gmail]/Important"'
        SpeakText("Important Mails selected.")
    elif cmb == "5" or cmb == "five" or cmb == "f i v e" or cmb == "phi" or cmb == "fi":
        mailBoxTarget = '"[Gmail]/Spam"'
        SpeakText("Spam selected.")
    elif cmb == "6" or cmb == "six" or cmb == "s i x":
        mailBoxTarget = '"[Gmail]/Starred"'
        SpeakText("Starred Mails selected.")
    elif cmb == "7" or cmb == "seven" or cmb == "s e v e n":
        # mailBoxTarget = '"[Gmail]/Bin"'       
        mailBoxTarget = '"[Gmail]/Trash"'
        SpeakText("Bin selected.")
    else:
        SpeakText("Wrong choice. Hence, default option Inbox wil be selected.")

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL_ID, PASSWORD)

    status, messages = imap.select(mailBoxTarget)
    
    messages = int(messages[0])

    if messages == 0:
        SpeakText("Selected MailBox is empty.")
        return None
    elif messages == 1:
        N = 1   # number of top emails to fetch
    elif messages == 2:
        N = 2   # number of top emails to fetch
    else:
        N = 3   # number of top emails to fetch

    msgCount = 1
    for i in range(messages, messages-N, -1):
        SpeakText(f"Message {msgCount}:")
        res, msg = imap.fetch(str(i), "(RFC822)")   # fetch the email message by ID
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])     # parse a bytes email into a message object

                subject, encoding = decode_header(msg["Subject"])[0]   
                if isinstance(subject, bytes): 
                    subject = subject.decode(encoding)      # if it's a bytes, decode to str
                
                From, encoding = decode_header(msg.get("From"))[0]   
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                SpeakText("Subject: " + subject)
                FromArr = From.split()
                FromName = " ".join(namechar for namechar in FromArr[0:-1])
                SpeakText("From: " + FromName)
                SpeakText("Sender mail: " + FromArr[-1])
                
                # MULTIPART
                if msg.is_multipart(): 
                    for part in msg.walk(): 
                        content_type = part.get_content_type()      
                        content_disposition = str(
                            part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()   # get the email body
                        except:
                            pass

                        # PLAIN TEXT MAIL
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            SpeakText("Do you want to listen to the text content of the mail ? Please say YES or NO.")
                            SpeakText("Speak Now")
                            # talkMSG1 = speech_to_text(duration=2)
                            talkMSG1 = speech_to_text()
                            talkMSG1=edit(talkMSG1)
                            if  talkMSG1=='yes':
                                SpeakText("The mail body contains the following:")
                                SpeakText(body)
                            else:
                                SpeakText("You chose NO")

                            #for summarisation
                            SpeakText("Do you want me to summarise the text content of the mail ? Please say YES or NO.")
                            SpeakText("Speak Now")
                            # sumMSG = speech_to_text(duration=2)
                            sumMSG = speech_to_text()
                            sumMSG=edit(sumMSG)
                            if  sumMSG=='yes':
                                SpeakText("Here is the email summary:")
                                stopWords = set(stopwords.words("english"))
                                words = word_tokenize(body)
                                # Creating a frequency table
                                freqTable = dict()
                                for word in words:
                                    word = word.lower()
                                    if word in stopWords:
                                        continue
                                    if word in freqTable:
                                        freqTable[word] += 1
                                    else:
                                        freqTable[word] = 1
                                # Creating a dictionary to keep the score
                                sentences = sent_tokenize(body)
                                sentenceValue = dict()

                                for sentence in sentences:
                                    for word, freq in freqTable.items():
                                        if word in sentence.lower():
                                            if sentence in sentenceValue:
                                                sentenceValue[sentence] += freq
                                            else:
                                                sentenceValue[sentence] = freq

                                sumValues = 0
                                for sentence in sentenceValue:
                                    sumValues += sentenceValue[sentence]
                                # Average value of a sentence from the original text
                                average = int(sumValues / len(sentenceValue))
                                # Storing sentences into our summary.
                                summary = ''
                                for sentence in sentences:
                                    if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
                                        summary += " " + sentence
                                print(summary)
                                SpeakText(summary)
                                #=======================


                        # MAIL WITH ATTACHMENT
                        elif "attachment" in content_disposition:
                            SpeakText("The mail contains attachment, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail")
                            filename = part.get_filename()  # download attachment
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    os.mkdir(folder_name)   # make a folder for this email (named after the subject)
                                filepath = os.path.join(folder_name, filename)
                                open(filepath, "wb").write(part.get_payload(decode=True))   # download attachment and save it
                
                # NOT MULTIPART
                else:
                    content_type = msg.get_content_type()    # extract content type of email
                    body = msg.get_payload(decode=True).decode()    # get the email body
                    if content_type == "text/plain":
                        SpeakText("Do you want to listen to the text content of the mail ? Please say YES or NO.")
                        SpeakText("Speak Now")
                        # talkMSG2 = speech_to_text(duration=2)
                        talkMSG2 = speech_to_text()
                        talkMSG2=edit(talkMSG2)
                        if talkMSG2 == 'yes' or talkMSG2=='yess' or talkMSG2=='y e s':
                            SpeakText("The mail body contains the following:")
                            SpeakText(body)
                        else:
                            SpeakText("You chose NO")


                # HTML CONTENTS
                if content_type == "text/html":
                    SpeakText("The mail contains an HTML part, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail. You can view the html files in any browser, simply by clicking on them.")
                    # if it's HTML, create a new HTML file
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):  
                        os.mkdir(folder_name)   # make a folder for this email (named after the subject)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)
                    
                    # webbrowser.open(filepath)     # open in the default browser

                SpeakText(f"\nEnd of message {msgCount}:")
                msgCount += 1
                print("="*100)
    imap.close()
    imap.logout()


def searchMail():
    """
    Search mails by subject / author mail ID

    Returns:
        None: None
    """
    M = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    M.login(EMAIL_ID, PASSWORD)

    mailBoxTarget = "INBOX"
    SpeakText("Where do you want to search ? Say 1 for Inbox. Say 2 for Sent Mailbox. Say 3 for Drafts. Say 4 for important mails. Say 5 for Spam. Say 6 for Starred Mails. Say 7 for Bin.")
    SpeakText("Speak Now")
    # cmb = speech_to_text(duration=2)
    cmb = speech_to_text()
    cmb=edit(cmb)
    if cmb == "1" or cmb == "one" or cmb == "o n e" or cmb=="fun" or cmb == "oneh":
        mailBoxTarget = "INBOX"
        SpeakText("Inbox selected.")
    elif cmb == "2" or cmb == "two" or cmb == "tu" or cmb == "t w o" or cmb == "too" or cmb == "to":
        mailBoxTarget = '"[Gmail]/Sent Mail"'
        SpeakText("Sent Mailbox selected.")
    elif cmb == "3" or cmb == "three" or cmb =="tree" or cmb == "t h r e e":
        mailBoxTarget = '"[Gmail]/Drafts"'
        SpeakText("Drafts selected.")
    elif cmb == "4" or cmb == "four" or cmb == "fore" or cmb == "for" or cmb == "f o u r":
        mailBoxTarget = '"[Gmail]/Important"'
        SpeakText("Important Mails selected.")
    elif cmb == "5" or cmb == "five" or cmb == "f i v e":
        mailBoxTarget = '"[Gmail]/Spam"'
        SpeakText("Spam selected.")
    elif cmb == "6" or cmb == "six" or cmb == "s i x":
        mailBoxTarget = '"[Gmail]/Starred"'
        SpeakText("Starred Mails selected.")
    elif cmb == "7" or cmb== "seven" or cmb == "s e v e n":
        mailBoxTarget = '"[Gmail]/Bin"'
        SpeakText("Bin selected.")
    else:
        SpeakText("Wrong choice. Hence, default option Inbox wil be selected.")


    M.select(mailBoxTarget)

    SpeakText("Say 1 to search mails from a specific sender. Say 2 to search mail with respect to the subject of the mail.")
    SpeakText("Speak Now")
    # mailSearchChoice = speech_to_text(duration=2)
    mailSearchChoice = speech_to_text()
    mailSearchChoice=edit(mailSearchChoice)
    if mailSearchChoice == "1" or mailSearchChoice== "one" or mailSearchChoice== "o n e":
        SpeakText("Please mention the sender email ID you want to search.")
        SpeakText("Speak Now")
        # searchSub = speech_to_text(duration=15)
        searchSub = speech_to_text()
        searchSub = searchSub.replace("at the rate", "@")
        searchSub = searchSub.replace(" ", "")
        status, messages = M.search(None, f'FROM "{searchSub}"')
    elif mailSearchChoice == "2" or mailSearchChoice == "two" or mailSearchChoice == "tu" or mailSearchChoice == "too" or mailSearchChoice == "to" or mailSearchChoice == "t w o":
        SpeakText("Please mention the subject of the mail you want to search.")
        SpeakText("Speak Now")
        # searchSub = speech_to_text(duration=10)
        searchSub = speech_to_text()
        status, messages = M.search(None, f'SUBJECT "{searchSub}"')
    else:
        SpeakText("Wrong choice. Performing default operation. Please mention the subject of the mail you want to search.")
        SpeakText("Speak Now")
        # searchSub = speech_to_text(duration=10)
        searchSub = speech_to_text()
        status, messages = M.search(None, f'SUBJECT "{searchSub}"')
    
    
    if str(messages[0]) == "b''":
        SpeakText(f"Mail not found in {mailBoxTarget}.")
        return None

    msgCount = 1
    for i in messages:
        SpeakText(f"Message {msgCount}:")
        res, msg = M.fetch(i, "(RFC822)")   # fetch the email message by ID
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])     # parse a bytes email into a message object

                subject, encoding = decode_header(msg["Subject"])[0]    # decode the email subject
                if isinstance(subject, bytes): 
                    subject = subject.decode(encoding)      # if it's a bytes, decode to str
                
                From, encoding = decode_header(msg.get("From"))[0]      # decode email sender
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                SpeakText("Subject: " + subject)
                FromArr = From.split()
                FromName = " ".join(namechar for namechar in FromArr[0:-1])
                SpeakText("From: " + FromName)
                SpeakText("Sender mail: " + FromArr[-1])

                # MULTIPART
                if msg.is_multipart(): 
                    for part in msg.walk(): # iterate over email parts
                        content_type = part.get_content_type()      # extract content type of email
                        content_disposition = str(
                            part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()   # get the email body
                        except:
                            pass

                        # PLAIN TEXT MAIL
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            SpeakText("Do you want to listen to the text content of the mail ? Please say YES or NO.")
                            SpeakText("Speak Now")
                            # talkMSG1 = speech_to_text(duration=2)
                            talkMSG1 = speech_to_text()
                            talkMSG1=edit(talkMSG1)
                            if talkMSG1 == 'yes':
                                SpeakText("The mail body contains the following:")
                                SpeakText(body)
                            else:
                                SpeakText("You chose NO")

                        # MAIL WITH ATTACHMENT
                        elif "attachment" in content_disposition:
                            SpeakText("The mail contains attachment, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail")
                            filename = part.get_filename()  # download attachment
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    os.mkdir(folder_name)   # make a folder for this email (named after the subject)
                                filepath = os.path.join(folder_name, filename)
                                open(filepath, "wb").write(part.get_payload(decode=True))   # download attachment and save it
                
                # NOT MULTIPART
                else:
                    content_type = msg.get_content_type()    # extract content type of email
                    body = msg.get_payload(decode=True).decode()    # get the email body
                    if content_type == "text/plain":
                        SpeakText("Do you want to listen to the text content of the mail ? Please say YES or NO.")
                        SpeakText("Speak Now")
                        # talkMSG2 = speech_to_text(duration=2)
                        talkMSG2 = speech_to_text()
                        talkMSG2=edit(talkMSG2)
                        if talkMSG2 == 'yes':
                            SpeakText("The mail body contains the following:")
                            SpeakText(body)
                        else:
                            SpeakText("You chose NO")


                # HTML CONTENTS
                if content_type == "text/html":
                    SpeakText("The mail contains an HTML part, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail. You can view the html files in any browser, simply by clicking on them.")
                    # if it's HTML, create a new HTML file
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):  
                        os.mkdir(folder_name)   # make a folder for this email (named after the subject)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)
                    
                    # webbrowser.open(filepath)     # open in the default browser

                SpeakText(f"\nEnd of message {msgCount}:")
                msgCount += 1
                print("="*100)

    M.close()
    M.logout()

def main():
    """
    Main function that handles primary choices
    """
    
    if EMAIL_ID != "" and PASSWORD != "":
        SpeakText("Do you want to run model?")
        SpeakText("Speak Now")
        # text = speech_to_text(duration=2)
        text = speech_to_text()
        text=edit(text)
        while text in['yes','yess','yeah','y e s']:

            SpeakText("Choose and speak out the option number for the task you want to perform. Say 1 to send a mail. Say 2 to get your mailbox status. Say 3 to search a mail. Say 4 to get the last 3 mails.")
            SpeakText("Speak Now")
            # text = speech_to_text(duration=2)
            text = speech_to_text()
            choice=edit(text)
            
            if choice in ['1', 'one','won','onee','o n e','fun','done','wuan','von','van','when']:
                composeMail()
                print("compose email")
            elif choice in ['2', 'two','too','tu','to','t w o','do','doo','boo']:
                getMailBoxStatus()
                print("getMailBoxStatus")
            elif choice in ['3', 'three','tree','t h r e e']:
                searchMail()
                print('search mail')
            elif choice in ['4', 'four','for','f o u r','fore','food','foot','flour','floor','full','foul','ford']:
                getLatestMails()
                print("latest mail")
            else:
                SpeakText("Wrong choice. Please say only the number")
            
            SpeakText("Do you want to run model?")
            SpeakText("Speak Now")
            # text = speech_to_text(duration=2)
            text = speech_to_text()
            text=edit(text)
            

if __name__ == '__main__':
    main()
