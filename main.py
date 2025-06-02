import speech_recognition as sr
import pyttsx3
import webbrowser
import pywhatkit
import requests
import time
import openai
import urllib.parse 

recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170) 

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_openrouter_response(prompt):
    headers = {
        "Authorization": "Bearer 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",  
        "Content-Type": "application/json"
    }

    data = {
    "model": "mistralai/mistral-7b-instruct",  
    "messages": [
        {"role": "system", "content": "You are Jarvis, an intelligent, respectful, and helpful assistant, give short replies and be specific."},
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 200  
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content']
            return reply
        else:
            print("Error:", response.text)
            return "Sorry, I couldn't get a response right now."
    except Exception as e:
        print("Exception:", e)
        return "Something went wrong while contacting OpenRouter."

def processCommand(command):
    print("Command received:", command)
    speak(f"You said: {command}")
    command = command.lower()

    if command.startswith("play "):
        song_name = command.replace("play", "").strip()
        if song_name:
            speak(f"Playing {song_name} on YouTube")
            pywhatkit.playonyt(song_name)  
        else:
            speak("Please say the name of the song after 'play'")

    elif "news" in command or "headlines" in command:
        r = requests.get("https://newsapi.org/v2/top-headlines?country=us&apiKey=5fa4071e035a4242bc0000ff604fc899")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])[:5]
            speak("Here are the top 5 news headlines.")
            for article in articles:
                speak(article['title'])

    elif "youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "instagram" in command:
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com")
    elif "whatsapp" in command:
        speak("Opening WhatsApp")
        webbrowser.open("https://web.whatsapp.com/")
    else:
        response = get_openrouter_response(command)
        print("Jarvis:", response)
        speak(response)

if __name__ == "__main__":
    speak("Initializing Jarvis ...")
    
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word 'Jarvis'...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                word = recognizer.recognize_google(audio)

                if word.lower() == "jarvis":
                    speak("Hola, I am jarvis. What can I do for you?")
                    print("jarvis activated. Listening for command...")
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        command_audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                        command = recognizer.recognize_google(command_audio)
                        processCommand(command)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"API error: {e}")
        except Exception as e:
            print(f"Error: {e}")