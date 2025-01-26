import json
from bs4 import BeautifulSoup
import requests
from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse, parse_qs
from config import DRIVER_PATH
router = APIRouter()

class CourseData:
    def __init__(self, department: str, course_code: str, class_id: str, type: str, course_name: str, credit: str, instructor:str, note:str, time_slot: str):
        self.department = department
        self.course_code = course_code
        self.class_id = class_id
        self.type = type
        self.course_name = course_name
        self.credit = credit
        self.instructor = instructor
        self.note = note
        self.time_slot = time_slot
    def formatted_data(self):
        data = {
            "department": self.department,
            "course_code": self.course_code,
            "class": self.class_id,
            "type": self.type,
            "course_name": self.course_name,
            "credit": self.credit,
            "instructor": self.instructor,
            "note": self.note,
            "time_slot": self.time_slot
        }
        return data

def fetch_table_data(url: str, headers: dict):
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    div = soup.select_one(".hidden-xs.hidden-sm")
    table = div.select_one("table")

    data = []
    rows = table.select("tbody tr")
    for row in rows:
        cells = row.select("td")
        cell_values = [cell.text.strip() for cell in cells]
        data.append(cell_values)
    return data

@router.get("/get_all_csie_course")
def get_all_csie_course():
    url = "https://course.ncku.edu.tw/index.php?c=qry11215&i=W2kHbVtmCzQGflchADgNPQZuVilVaw8iAWgAPwI4BjMAMwo7Vm9UeQUzVTcJOAMhWz4JKlduAGEMa1cwA2sHfAc9UzlfZgo0B2UAP1NgAToGLwEvBGkONgNrXSkGYgtqViQJdAdaVWUGZQZ3XW1WJQA8CDxZYQYkDW4BcgATBD1bLwd1W2kLcwZsV2gAMw09BmRWMFVjDzoBYQBsAnkGcQA4CjBWblQoBXpVfwlxAyFbZgl7V28ANQxrVyEDJAdpBzBTZl8kCi0HPwB2U2sBNwZuAX4EMA5uAz1dZwZjC2hWMQkiBz5VeAYwBmRdbFZ0AFAIK1lgBnsNOQFvAGMENVs9B2xbMws0BjRXaAB5DX8GblY8VTgPIgE3ADMCcgZ2AF0KbVY7VCgFMlV1CTgDMVtnCSpXEwA3DHNXOAMsB3oHJ1M5X2cKNQcmAHdTcwE7BjUBZgRnDjsDKl1iBjwLP1ZvCWkHP1U7BjEGPF1sVmcAPQhgWWEGNw1gAWUAaQRtWzIHZVtpC2cGP1djADMNPAZvVmJVOA8zAWgAPwI4BjMAMwo2Vm9UdwV6VTwJMwM5W38Jb1d3ADsMM1c5A2EHPAcp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    }
    data = fetch_table_data(url, headers)
    return json.dumps(data, ensure_ascii=False, indent=4)


@router.get("/query/{course_name}")
def query_by_name(course_name: str):
    url = "https://course.ncku.edu.tw/index.php?c=qry11215&i=ADoJPQBjUW8CelB3BjtXNAdrA3ENOFUmDjoPMwQ7VTEFNwc8CzdQcFVhU2MDOFJyUDQBdlJuUDYJOAM9DDRbLFFjX2tdOgwzVTcFawM1BW0CL1JxWz1QNg47DnkFZAMzAnEAd1MLBDlVNFd0U2kGd1ZrUDAEOVB1XGkGLFQXDDkAfAklAGxRKAJoUD4GMFc0B2EDaA0wVT4OMw9gBHpVcwU8BzcLNlAhVShTKwNxUnJQbAEnUm9QYgk4AywMe1s5UW5fNF14DCpVbQUiAz4FYAJuUiBbZFBuDm0ONwVlAzECZAAhU28EJFVhV2dTaAYmVgdQJwQ4UCpcPgYxVGcMMQBuCTwANlFvAjBQPgZ6V3YHawNkDWtVJg5lDz8EcVV0BVkHagtjUCFVYFMhAzhSYlBtAXZSE1BgCSADNQxzWypReV9rXTsMMlV0BSMDJgVsAjVSOFszUDsOeg4yBToDZgI6AGpTbgRnVWBXP1NoBjVWalBsBDlQZlxnBjtUbQxpAGEJNQBsUTwCO1A1BjBXNQdqAzoNa1U3DjoPMwQ7VTEFNwcxCzdQflUoU2gDM1JqUHUBM1J3UGwJYAM0DD5bbFF3"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    }
    data = fetch_table_data(url, headers)
    target_course = course_name

    for row in data:
        if target_course in row[4]:
            course_data = CourseData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            return course_data.formatted_data()

    raise HTTPException(status_code=404, detail=f"課程名稱 '{target_course}' NOT FOUND")

class WebDriver:
    def __init__(self, chrome_driver_path: str):
        self.chrome_driver_path = chrome_driver_path
        self.service = Service(chrome_driver_path)
        self.options = Options()
        self.url = ""
      #  self.options.add_argument("--headless") 
        self.options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def __call__(self, *args, **kwds):
        if len(args) > 0:
            url = args[0]
            self.url = url
            self.driver.get(url)
            self.driver.implicitly_wait(10)

    def click_Byclass(self, class_name: str):
        button = self.driver.find_element(By.CLASS_NAME, class_name)
        button.click()
        WebDriverWait(self.driver, 10).until(
            lambda driver: self.driver.current_url != self.url
        )
    def driver_close(self):
        input("close...")
        self.driver.quit()

@router.get("/update_url")
def update_url():
    webdriver = WebDriver(DRIVER_PATH)
    webdriver("https://course.ncku.edu.tw/index.php?c=qry11215")
    webdriver.click_Byclass("btn_menu_main")
    current_url = webdriver.driver.current_url
    parsed_url = urlparse(current_url)
    url_params = parse_qs(parsed_url.query)
    webdriver.driver_close()
    
    return {
        "current_url": current_url,
        "url_parameters": url_params
    }