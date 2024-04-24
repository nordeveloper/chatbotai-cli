# ChatBot Assistant AI CLI
import datetime
import requests
import json
from colorama import init, Fore, Back, Style
from googletrans import Translator
import speech_recognition as sr
import pyttsx3
import models

init()

config_json = open('config.json')
config = json.load(config_json)


def show_datetime():
    return datetime.datetime.today().strftime("%m-%d-%Y %H:%M")
    

def get_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print("Name: "+ voice.name)


def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 130)
    engine.setProperty('voice', voices[config['speeker']].id)
    engine.say(text)
    engine.runAndWait()


def speech_to_text():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Waiting for speech...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

        if(audio):
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
        return text
        
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition:{e}")
        return None    


def google_translate(text, dest="ru"):
    translator = Translator() 
    result = translator.translate(text, src="en", dest=dest)
    return result.text   


def get_character_prompt(promptjson):
    user_name = ''
    sysprompt = promptjson['system_prompt']+"\n"
    if(promptjson['user_name']):
       user_name = promptjson['user_name']
    if(promptjson['persona']):
        sysprompt+= "Persona: "+promptjson['persona']+"\n"
    if(promptjson['scenario']):
        sysprompt+="Scenario: "+ promptjson['scenario']+"\n"
    if(promptjson['first_mes']):
        sysprompt+="First message: "+ promptjson['first_mes']
    if(promptjson['name']):
        sysprompt = sysprompt.replace('{{char}}', promptjson['name'])
        sysprompt = sysprompt.replace('{{user}}', user_name)
        return sysprompt


def get_ai_response(prompt):
    apiUrls = [
        'https://api.openai.com/v1/chat/completions',
        'https://openrouter.ai/api/v1/chat/completions'
    ]

    api_url = apiUrls[1]
    f =  open('api_key.txt')
    api_key = f.read()

    chat_history.append({"role": "user", "content": prompt})

    myobj = {
        "model": models.list[1],
        "max_tokens":config.max_tokens,
        "messages": chat_history,
        'temperature': 0.8,
        'top_p': 1,
        'frequency_penalty': 0.9,
        'presence_penalty': 0.9
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost"
    }
    response = requests.post(api_url, json=myobj, headers=headers)

    aiResponseText = 'Error, try again'

    if response.status_code == 200:
        data = response.json()
        if(data['choices'][0]['message']['content']):
            aiResponseText = data['choices'][0]['message']['content']
            chat_history.append({"role": "assistant", "content": aiResponseText})  
        
        return aiResponseText            
    else:
        print(response)


chat_history = []
charjson = open('character.json')
promptjson = json.load(charjson)
system_prompt = get_character_prompt(promptjson)
chat_history.append({"role": "system", "content": system_prompt})

print(f'{Fore.GREEN} Hi, I am helpfull ChatBot Assistant AI. How can I help you?')

def run():

    while True:
        if(config['microphone']==True):
            inputTxt = speech_to_text()
        else:
            inputTxt = input(f'{Fore.BLUE} You: ')

        if(inputTxt == 'exit'):
            break

        if(inputTxt == 'date time'):
            datetime = show_datetime()
            print(f'{Fore.YELLOW}'+ datetime)
            text_to_speech(datetime)
            continue

        AiResponsTxt_en = get_ai_response(inputTxt)
        print(f'{Fore.GREEN}'+AiResponsTxt_en)  
            
        if(config['translate']==True):
            AiResponsTxt_ru = google_translate(AiResponsTxt_en)
            print(f'{Fore.YELLOW}'+ AiResponsTxt_ru)
            
        if(config['speech']==True and config['speech_language']=='en'):
            text_to_speech(AiResponsTxt_en)

        if(config['speech']==True and config['speech_language']=='ru'):
            text_to_speech(AiResponsTxt_ru)



if __name__ == "__main__":
    run()
