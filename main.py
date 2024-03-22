# Chatbot assistant AI CLI
import datetime
import requests
import json
from colorama import init, Fore, Back, Style
from googletrans import Translator
import speech_recognition as sr
import pyttsx3
import models
init()

#config speech, language, translate
config = {
    "speech":False,
    "speech_language": "ru",
    "microphone": False,
    "translate": True,
    "speeker":4
}

first_message = 'Welcome DMAI, I am your Assistant. I can help you with your daily tasks. If you need help, just ask.'


def show_datetime():
    #return datetime.datetime.now()
    today = datetime.datetime.today()
    return today.strftime("%m-%d-%Y %H:%M")
    

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


def getCharacterPrompt(promptjson):
    user_name = ''
    if(promptjson['user_name']):
       user_name = promptjson['user_name']

    sysprompt = promptjson['system_prompt']+"\n"

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


def getAiResponse(prompt):
    apiUrls = [
        'https://api.openai.com/v1/chat/completions',
        'https://openrouter.ai/api/v1/chat/completions'
    ]

    api_url = apiUrls[1]
    f =  open('api_key.txt')
    api_key = f.read()

    conversation.append({"role": "user", "content": prompt})

    myobj = {
        "model": models.list[1],
        "max_tokens":200,
        "messages": conversation,
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
            conversation.append({"role": "assistant", "content": aiResponseText})  
        
        return aiResponseText            
    else:
        print("Error: "+ response.status_code + " " + response.text)



conversation = []
conversation.append({"role": "system", "content": first_message})

system_prompt = ''

charjson = open('character.json')
promptjson = json.load(charjson)

system_prompt = getCharacterPrompt(promptjson)
conversation.append({"role": "system", "content": system_prompt})

print(f'{Fore.GREEN}'+conversation[0]['content'])

def run():
    # get_voices()

    while True:
        if(config['microphone']==True):
            spokenTxt = speech_to_text()
        else:
            inputTxt = input(f'{Fore.BLUE} You: ')

        if(inputTxt):
            spoken_text = inputTxt
            
        elif(spokenTxt):
            spoken_text = spokenTxt

        if(spoken_text == 'exit'):
            break

        if(spoken_text == 'date time'):
            datetime = show_datetime()
            print(datetime)
            text_to_speech(datetime)
            continue

        # first_word = spoken_text.split(" ")[0]
        if(len(spoken_text.split()) > 2):
            spoken_text = spoken_text.split(' ', 1)[1]

        AiResponsTxt_en = getAiResponse(spoken_text)
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
