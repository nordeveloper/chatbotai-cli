import datetime
import requests
import json
import colorama
from colorama import Fore
from googletrans import Translator
import speech_recognition as sr
import pyttsx3
import os

colorama.init(autoreset=True)

class ChatBotAssistant:
    def __init__(self, config_path='config.json', api_key_path='api_key.txt', character_path='character.json'):
        self.config = self.load_config(config_path)
        self.api_key = self.load_api_key(api_key_path)
        self.chat_history = []
        self.translator = Translator()
        self.promptjson = self.load_character_prompt(character_path)
        self.system_prompt = self.get_character_prompt(self.promptjson)
        self.chat_history.append({"role": "system", "content": self.system_prompt})
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        print(f'{Fore.GREEN} Hi, I am helpful ChatBot Assistant AI. How can I help you?')

    @staticmethod
    def load_config(config_path):
        with open(config_path) as config_file:
            return json.load(config_file)

    @staticmethod
    def load_api_key(api_key_path):
        if not os.path.exists(api_key_path):
            print('[NOTE] Please create a file named api_key.txt and put your OpenRouter AI API key inside')
            exit()
        else:
            with open(api_key_path) as api_file:
                return api_file.read().strip()

    @staticmethod
    def load_character_prompt(character_path):
        with open(character_path) as character_file:
            return json.load(character_file)

    @staticmethod
    def show_datetime():
        return datetime.datetime.today().strftime("%m-%d-%Y %H:%M")

    def get_voices(self):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            print("Name: " + voice.name)

    def text_to_speech(self, text):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('rate', 130)
        self.engine.setProperty('voice', voices[self.config['speaker']].id)
        self.engine.say(text)
        self.engine.runAndWait()

    def speech_to_text(self):
        try:
            with sr.Microphone() as source:
                print("Waiting for speech...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)

            if audio:
                print("Recognizing...")
                text = self.recognizer.recognize_google(audio)
            return text

        except sr.UnknownValueError:
            print("Sorry, I could not understand what you said.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition: {e}")
            return None

    def google_translate(self, text, dest="ru"):
        result = self.translator.translate(text, src="en", dest=dest)
        return result.text

    def get_character_prompt(self, promptjson):
        user_name = ''
        sysprompt = promptjson['system_prompt'] + "\n"
        if promptjson['user_name']:
            user_name = promptjson['user_name']
        if promptjson['persona']:
            sysprompt += "Persona: " + promptjson['persona'] + "\n"
        if promptjson['scenario']:
            sysprompt += "Scenario: " + promptjson['scenario'] + "\n"
        if promptjson['first_mes']:
            sysprompt += "First message: " + promptjson['first_mes']
        if promptjson['name']:
            sysprompt = sysprompt.replace('{{char}}', promptjson['name'])
            sysprompt = sysprompt.replace('{{user}}', user_name)
        return sysprompt

    def get_ai_response(self, prompt):
        api_urls = [
            'https://api.openai.com/v1/chat/completions',
            'https://openrouter.ai/api/v1/chat/completions'
        ]

        api_url = api_urls[1]

        self.chat_history.append({"role": "user", "content": prompt})

        myobj = {
            "model": "gpt-4",
            "max_tokens": self.config['max_tokens'],
            "messages": self.chat_history,
            'temperature': 0.8,
            'top_p': 1,
            'frequency_penalty': 0.9,
            'presence_penalty': 0.9
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://localhost"
        }
        response = requests.post(api_url, json=myobj, headers=headers)

        ai_response_text = 'Error, try again'

        if response.status_code == 200:
            data = response.json()
            if data['choices'][0]['message']['content']:
                ai_response_text = data['choices'][0]['message']['content']
                self.chat_history.append({"role": "assistant", "content": ai_response_text})

        return ai_response_text

    def run(self):
        while True:
            if self.config['microphone']:
                input_txt = self.speech_to_text()
            else:
                input_txt = input(f'{Fore.BLUE} You: ')

            if input_txt == 'exit':
                break

            if input_txt == 'date time':
                current_datetime = self.show_datetime()
                print(f'{Fore.YELLOW}' + current_datetime)
                self.text_to_speech(current_datetime)
                continue

            ai_response_txt_en = self.get_ai_response(input_txt)
            print(f'{Fore.GREEN}' + ai_response_txt_en)

            if self.config['translate']:
                ai_response_txt_ru = self.google_translate(ai_response_txt_en)
                print(f'{Fore.YELLOW}' + ai_response_txt_ru)

            if self.config['speech'] and self.config['speech_language'] == 'en':
                self.text_to_speech(ai_response_txt_en)

            if self.config['speech'] and self.config['speech_language'] == 'ru':
                self.text_to_speech(ai_response_txt_ru)


if __name__ == "__main__":
    bot = ChatBotAssistant()
    bot.run()
