
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URI")
MONGO_DB_PWD = os.getenv("MONGO_DB_PWD")
MONGO_DB_USR = os.getenv("MONGO_DB_USR")

uri = f"mongodb+srv://{MONGO_DB_USR}:{MONGO_DB_PWD}@{MONGO_DB_URI}"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Get the Reddit database
reddit_db = client.Reddit

# Get the persona_configs Reddit collection
reddit_personas_collection = reddit_db.persona_configs

# Get the subreddit_configs Reddit collection
reddit_subreddit_configs_collection = reddit_db.subreddit_configs

def add_new_persona_config(persona_name, persona_template_id):
    new_persona_config = {
        "persona_name": persona_name,
        "persona_template_id": persona_template_id
    }
    try:
        reddit_personas_collection.insert_one(new_persona_config)
        return True
    except Exception as e:
        print(e)
        return False

def get_all_persona_configs():
    persona_configs = []
    try:
        # dont return the _id field
        persona_configs = list(reddit_personas_collection.find({}, {"_id": 0}))
        personas = {}
        for persona_config in persona_configs:
            personas[persona_config['persona_name']] = persona_config['persona_template_id']
        return personas
    except Exception as e:
        print(e)
        return persona_configs
    

def add_new_subreddit_config(subreddit_name, description, summary):
    new_subreddit_config = {
        "subreddit_name": subreddit_name,
        "description": description,
        "summary": summary
    }
    try:
        reddit_subreddit_configs_collection.insert_one(new_subreddit_config)
        return True
    except Exception as e:
        print(e)
        return False
    
def get_all_subreddit_configs():
    subreddit_configs = []
    try:
        # dont return the _id field
        subreddit_configs = list(reddit_subreddit_configs_collection.find({}, {"_id": 0}))
        configs = {}
        for subreddit_config in subreddit_configs:
            configs[subreddit_config['subreddit_name']] = {
                "subreddit_desc": subreddit_config['description'],
                "subreddit_summary": subreddit_config['summary']
            }

        return configs
    except Exception as e:
        print(e)
        return subreddit_configs
    
