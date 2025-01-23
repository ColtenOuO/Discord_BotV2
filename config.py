import json

class Config:
    token: str = ""
    application_id: int = 0

jsonConfig = open('./config.json')
jsonFile = jsonConfig.read()
jsonFile = json.loads(jsonFile)
config = Config()

config.token = jsonFile["discord_config"]['bot_token']
config.application_id = jsonFile["discord_config"]["application_id"]

TOKEN = config.token
APPLICATION_ID = config.application_id