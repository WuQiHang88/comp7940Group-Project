import requests
import configparser
import pymongo

class ChatGPT:
    def __init__(self, config):
        
        client = pymongo.MongoClient(config['MONGODB']['URI'])
        db = client[config['MONGODB']['DB_NAME']]
        coll = db['bot_config']

        bot_config = coll.find_one()
        self.system_message = bot_config['system_prompt']

     
        api_key = config['CHATGPT']['API_KEY']
        base_url = config['CHATGPT']['BASE_URL']
        model = config['CHATGPT']['MODEL']
        api_ver = config['CHATGPT']['API_VER']

        self.url = f'{base_url}/deployments/{model}/chat/completions?api-version={api_ver}'
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key,
        }

    def submit(self, user_message: str):
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message},
        ]

        payload = {
            "messages": messages,
            "temperature": 1,
            "max_tokens": 300,
            "top_p": 1,
            "stream": False
        }

        response = requests.post(self.url, json=payload, headers=self.headers)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "Error: " + response.text