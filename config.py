import json

class Config:
    token: str = ""
    application_id: int = 0
    driver_path: str
    admin: int
class Gemini:
    api_key: str = ""
class NCKU_Web:
    phpsessid: str
    course_web: str


jsonConfig = open('./config.json')
jsonFile = jsonConfig.read()
jsonFile = json.loads(jsonFile)
config = Config()
gemini = Gemini()
ncku = NCKU_Web()

config.token = jsonFile["discord_config"]['bot_token']
config.application_id = jsonFile["discord_config"]["application_id"]
config.driver_path = jsonFile["discord_config"]["driver_path"]
config.admin = jsonFile["discord_config"]['admin']
gemini.api_key = jsonFile["gemini"]["api_key"]
ncku.course_web = jsonFile["ncku_cookie"]["PHPSESSID"]
ncku.phpsessid = jsonFile["ncku_cookie"]["COURSE_WEB"]

ADMIN = config.admin
TOKEN = config.token
APPLICATION_ID = config.application_id
GENAI_APIKEY = gemini.api_key
DRIVER_PATH = config.driver_path
PHPSESSID = ncku.phpsessid
COURSE_WEB = ncku.course_web