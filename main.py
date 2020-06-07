import requests
import json
import pyttsx3
import speech_recognition as sr
import re 

API_KEY = "twMGzTfGhKb3"
PROJECT_TOKEN = "t3n1bQCxLaz4"
RUN_TOKEN = "t-aTLBATY6mD"


class Data:
    def __init__(self,api_key,project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key" : self.api_key
        }
        self.get_data()
    
    def get_data (self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params = {"api_key": self.api_key})
        self.data = json.loads(response.text)

    def get_total_cases(self):
        data = self.data['total']   
        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']
        return "0"
    
    def get_total_deaths(self):
        data = self.data['total']   
        for content in data:
            if content['name'] == "Deaths:":
                return content['value']  
        return "0"

    def get_total_recovered(self):
        data = self.data['total']   
        for content in data:
            if content['name'] == "Recovered:":
                return content['value']
        return "0"
    
    def get_country_data(self,country):
        data = self.data['country']   
        for content in data:
            if content['name'].lower() == country.lower():
                return content  
        return "0"     

    def get_list_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower()) 

        return countries      



def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source :
        audio = r.listen(source)
        said = ""
        try :
            said = r.recognize_google(audio)
        except Exception as e:
            print ("Exception:", str(e))
        
    return said.lower()

def main():
    print("Started Program..")
    END_PHRASE = "stop"
    data = Data(API_KEY,PROJECT_TOKEN)
    country_list = set(data.get_list_countries())
    TOTAL_PATTERNS = {
                re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
                re.compile("[\w\s]+ total cases"):data.get_total_cases,
                re.compile("[\w\s]+ total [\w\s]+ deaths"):data.get_total_deaths,
                re.compile("[\w\s]+ total deaths"):data.get_total_deaths,
                re.compile("[\w\s]+ total [\w\s]+ recovered"):data.get_total_recovered,
                re.compile("[\w\s]+ total recovered"):data.get_total_recovered
    }

    COUNTRY_PATTERNS = {
                re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
                re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
                re.compile("[\w\s]+ new cases [\w\s]+"): lambda country: data.get_country_data(country)['new_cases'],
                re.compile("[\w\s]+ cases [\w\s]+ today"): lambda country: data.get_country_data(country)['new_cases'],
                re.compile("[\w\s]+ new deaths [\w\s]+"): lambda country: data.get_country_data(country)['new_deaths'],
                re.compile("[\w\s]+ deaths [\w\s]+ today"): lambda country: data.get_country_data(country)['new_deaths'],
                re.compile("[\w\s]+ recovered [\w\s]+"): lambda country: data.get_country_data(country)['total_recovered'],
                re.compile("[\w\s]+ active cases [\w\s]+"): lambda country: data.get_country_data(country)['active_cases'],
                re.compile("[\w\s]+ tests [\w\s]"): lambda country: data.get_country_data(country)['total_tests'],
                re.compile("[\w\s]+ critical [\w\s]"): lambda country: data.get_country_data(country)['serious_cases'],
                re.compile("[\w\s]+ serious [\w\s]"): lambda country: data.get_country_data(country)['serious_cases'],
                re.compile("[\w\s]+ population [\w\s]"): lambda country: data.get_country_data(country)['population']
    }
    while True:
        print("Listening..")
        text = get_audio()
        result = None

        for pattern,func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result =func(country)
                        break 
                    

        for pattern,func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break

        if result :
            speak(result)

        if text.find(END_PHRASE) != -1: #Stop loop
            break

main()