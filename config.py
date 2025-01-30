from pydantic import BaseModel
import orjson
class DiscordConfig(BaseModel):
    bot_token: str
    application_id: int
    driver_path: str
    admin: int

class GeminiConfig(BaseModel):
    api_key: str

class NCKUCookieConfig(BaseModel):
    phpsessid: str
    course_web: str

class MongoDBConfig(BaseModel):
    db_url: str

class Config(BaseModel):
    discord_config: DiscordConfig
    gemini: GeminiConfig
    ncku_cookie: NCKUCookieConfig
    mongodb: MongoDBConfig

try:
    with open("./config.json", "rb") as file:
        config = Config(**orjson.loads(file.read()))
except:
    config = Config(
        discord_config=DiscordConfig(bot_token="", application_id=0, driver_path="", admin=0),
        gemini=GeminiConfig(api_key=""),
        ncku_cookie=NCKUCookieConfig(phpsessid="", course_web=""),
        mongodb=MongoDBConfig(db_url="")
    )
    with open("config.json", "wb") as file:
        file.write(orjson.dumps(config.model_dump(), option=orjson.OPT_INDENT_2))
    input("please edit config.json")
    exit(0)

TOKEN = config.discord_config.bot_token
APPLICATION_ID = config.discord_config.application_id
DRIVER_PATH = config.discord_config.driver_path
ADMIN_ID = config.discord_config.admin

GEMINI_API_KEY = config.gemini.api_key

PHPSESSID = config.ncku_cookie.phpsessid
COURSE_WEB = config.ncku_cookie.course_web

MONGO_DB_URL = config.mongodb.db_url
