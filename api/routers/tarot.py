from fastapi import APIRouter, HTTPException
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import json
import random
from PIL import Image
from config import GENAI_APIKEY

router = APIRouter()
with open("./api/routers/tarot.json", "r", encoding="utf-8") as file:
    tarot_data = json.load(file)

genai.configure(api_key=GENAI_APIKEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@router.get("/get_all_tarot")
def get_all_tarot():
    tarot_data = {}
    now_id: int = 1
    for page in range(1, 5):
        url = f'https://t.8s8s.com/photo/tarot/tarot_177_{page}.htm'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="連不上網站")        
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            tarot_cards = soup.select("div.t2_photo_3 ul li")
            for idx, card in enumerate(tarot_cards, start=now_id):
                name = card.text.strip()
                img_url = card.find("img")["src"]
                full_img_url = f"https://t.8s8s.com{img_url}"
                tarot_data[idx] = {"name": name, "url": full_img_url}
                now_id += 1
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    return tarot_data

@router.get("/random_tarot")
def random_tarot():
    card_list = list(tarot_data.values())
    random_card = random.choice(card_list)
    return random_card

@router.get("/get_tarot/description/{card_name}")
def get_description(card_name: str):
    try:
        response = model.generate_content(
            f"請用繁體中文回答塔羅牌 {card_name} 所代表的意涵，就回答這樣就好，不要自己額外新增其他東西，大約 100 字"
        )
        description = response.text.strip() if hasattr(response, "text") else None
        
        if not description:
            raise HTTPException(status_code=500, detail="AI 無法生成描述")
        
        return {"card_name": card_name, "description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 回應錯誤: {str(e)}")
