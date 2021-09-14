import pyttsx3

import speech_recognition as sr

import smtplib

dict = {'dad':'dad@gmail.com','college':'college@gmail.com','person':'person@gmail.com'}
engine = pyttsx3.init('sapi5')

voices = engine.getProperty('voices') # getting different voices

engine.setProperty('voice',voices[0].id) # first voice chosen

def speak(audio):

    engine.say(audio)

    engine.runAndWait()
def listen():

    #it takes microphone input from the user and returns string output

    r = sr.Recognizer()

    with sr.Microphone() as source:

        print("Iam listening.....")

        r.pause_threshold=1

        audio = r.listen(source)

    try:

        print("Recognizing.....")

        query = r.recognize_google(audio, language = 'en-in') # setting language

        print(f"User said:{query}\n")



    except Exception as e:

       speak("Say that again please...")

       return "None"

    return(query) # user's speech returned as string
def sendEmail(to,content):

    server = smtplib.SMTP('smtp.gmail.com',587) # create a SMTP object for connection with server

    server.ehlo()

    server.starttls() #TLS connection required by gmail

    server.login('sender@gmail.com','password')

    server.sendmail('sender@gmail.com',to,content) # from, to, content

if __name__ == "__main__":

    while(True):  # run infinite loop

        query = listen().lower()

        if 'email to' in query:

            try:

                name = list(query.split()) # extract receiver's name

                name = name[name.index('to')+1]

                speak("what should i say")

                content = listen()

                to = dict[name]

                sendEmail(to,content)

                speak("email has been sent")

            except Exception as e:

                print(e)

                speak("sorry unable to send the email at the moment.Try again")
