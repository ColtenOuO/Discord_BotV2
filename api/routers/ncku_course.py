import json
from bs4 import BeautifulSoup
import requests
from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse, parse_qs
from config import DRIVER_PATH, PHPSESSID, COURSE_WEB
router = APIRouter()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
}
cookies = [
    {"name": "PHPSESSID", "value": PHPSESSID, "domain": "course.ncku.edu.tw", "path": "/"},
    {"name": "COURSE_WEB", "value": COURSE_WEB, "domain": "course.ncku.edu.tw", "path": "/"}
]
cookies_dictformat = {
    "PHPSESSID": PHPSESSID,
    "COURSE_WEB": COURSE_WEB
}
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
    response = requests.get(url, headers=headers, cookies=cookies_dictformat)
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

@router.get("/query/{college}/{department}/{course_name}")
def query_by_name(college:str, department:str, course_name: str):
    file_path = "./api/routers/department.json"
    with open(file_path, "r", encoding="utf-8") as json_file:
        dep_data = json.load(json_file)
    url = dep_data[college][department]
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
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def __call__(self, *args, **kwds):
        if len(args) > 0:
            url = args[0]
            self.url = url
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            

    def wait_urlChange(self):
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url != self.url
        )
        self.url = self.driver.current_url

    def click_Byclass(self, class_name: str):
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, class_name))
        )
        button.click()
        self.wait_urlChange()

    def click_Bybutton(self, button_name: str):
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[text()='{button_name}']"))
        )

        button.click()
        self.wait_urlChange()

    def click_ByListItem(self, item_text: str):
        li = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//ul[@class='ui-choose']/li[text()='{item_text}']"))

        )
        li.click()

    def driver_close(self):
        self.driver.quit()

    def driver_back(self):
        self.driver.back()
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url != self.url
        )
        self.url = self.driver.current_url


class ParsingNCKU():
    def __init__(self, target_url: str):
        self.target_url = target_url
    def list_college(self):
        response = requests.get(self.target_url, headers=headers, cookies=cookies_dictformat)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        college_select = soup.find("select", id="college")
        college_names = [option.text for option in college_select.find_all("option")]
        return college_names
    def list_department(self, college_name: str):
        
        webdriver = WebDriver(DRIVER_PATH)
        webdriver(self.target_url)
        department_elements = webdriver.driver.find_elements(By.CSS_SELECTOR, "ul.ui-choose li")
        departments_data = {}
        departments = [ 
            element.get_attribute("title") for element in department_elements
            if "年級" not in element.get_attribute("title")
        ]

        for dep in departments:
            webdriver.click_ByListItem(dep)
            webdriver.click_Byclass("btn_send")
            departments_data[dep] = webdriver.driver.current_url
            webdriver.driver_back()

        webdriver.driver_close()
        print(f"[OK]: {college_name} 資料更新成功！")
        return departments_data


@router.get("/update_url")
def update_url():
    webdriver = WebDriver(DRIVER_PATH)
    webdriver("https://course.ncku.edu.tw/index.php?c=qry11215")
    webdriver.click_Bybutton("系所課程")
    webdriver.click_Bybutton("依學院、系所")
    current_url = webdriver.driver.current_url
    parsed_url = urlparse(current_url)
    url_params = parse_qs(parsed_url.query)
    webdriver.driver_close()
    return {
        "current_url": current_url,
        "url_parameters": url_params
    }

@router.get("/list/all_college")
def list_all_college():
    url = update_url()["current_url"]
    parsing = ParsingNCKU(target_url=url)
    college_list = parsing.list_college()
    webdriver = WebDriver(DRIVER_PATH)
    webdriver(url)

    dep_dict = {}

    for college in college_list:
        webdriver.click_ByListItem(college)
        webdriver.click_Byclass("btn_send") 
        dep_dict[college] = webdriver.driver.current_url
        webdriver.driver_back()
    
    webdriver.driver_close()
    
    with open("./api/routers/college.json", "w", encoding="utf-8") as json_file:
        json.dump(dep_dict, json_file, ensure_ascii=False, indent=4)

    return dep_dict

@router.get("/list/all_department")
def list_all_department():
    
    file_path = "./api/routers/college.json"
    with open(file_path, "r", encoding="utf-8") as json_file:
        college_list = json.load(json_file)
    
    all_data = {}
    for college, college_url in college_list.items():
        parsing = ParsingNCKU(college_url)
        data = parsing.list_department(college)
        all_data[college] = data
    
    
    with open("./api/routers/department.json", "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)
    return "OK"

@router.get("/get/url/general/{type_name}")
def get_general_course_url(type_name: str):
    url = "https://course.ncku.edu.tw/index.php?c=qry11215"
    webdriver = WebDriver(DRIVER_PATH)
    webdriver(url)
    webdriver.click_Bybutton("通識類課程")
    webdriver.click_Bybutton(type_name)
    target = webdriver.driver.current_url
    webdriver.driver_close()
    return target