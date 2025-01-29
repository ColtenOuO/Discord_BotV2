from fastapi import APIRouter
from pymongo import MongoClient
from config import DB_URL
import json
import random
router = APIRouter()
client = MongoClient(DB_URL)
db = client["Discord-Bot"]
collection = db["bank"]

def update_user_balance(discord_id, balance):
    collection.update_one(
        {"discord_id": discord_id},
        {"$set": {"balance": balance}},
        upsert=True  # if user is not exist, add it.
    )
def get_balance(discord_id) -> int:
    user_data = collection.find_one({"discord_id": discord_id})
    if user_data: return user_data['balance']
    else: return 0

@router.post("/update/balance/{discord_id}/{balance}")
def update_balance(discord_id: int, balance: int):
    update_user_balance(discord_id=discord_id, balance=balance)
    return { "discord_id": discord_id, "balance": balance }

@router.post("/update/add/{discord_id}/{balance}")
def update_balance(discord_id: int, balance: int):
    now_balance = get_balance(discord_id)
    update_user_balance(discord_id=discord_id, balance=now_balance + balance)
    return { "discord_id": discord_id, "balance": balance }