from fastapi import APIRouter
import json
import random
router = APIRouter()

with open("./api/routers/fish.json", "r", encoding="utf-8") as file:
    fish_data = json.load(file)

@router.get("/")
def fishing_api():
    return {"message": "this is api of Fishing."}

@router.get("/random_fish")
async def random_fish():
    fish_list = list(fish_data["fish_list"].values())
    random_fish = random.choice(fish_list)
    return random_fish