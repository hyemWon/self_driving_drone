from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import urllib.request

driver = webdriver.Chrome('/home/piai/ActionAI/crawling/chromedriver')
driver.get("https://www.google.co.kr/imghp?hl=ko&ogbl")

elem = driver.find_element_by_name("q") # 입력창
elem.send_keys("머리 위 하트") # 입력값
elem.send_keys(Keys.RETURN) #엔터키

# 이미지 선택전에 스크롤 전부 내려서 모든 이미지 불러오기
SCROLL_PAUSE_TIME = 1

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        try:
            driver.find_element_by_css_selector(".r0zKGf").click() # r0zKGf  mye4qd
        except:
            try:
                driver.find_element_by_css_selector(".mye4qd").click()
            except:
                break
    last_height = new_height
   
 
images = driver.find_elements_by_css_selector(".rg_i.Q4LuWd")

time.sleep(3) 

count = 1
for image in images: 
    try:
        image.click()
        time.sleep(4) # 이미지 로딩 시간 기다리기
        imgURL = driver.find_element_by_css_selector(".n3VNCb").get_attribute("src")
        urllib.request.urlretrieve(imgURL, "/home/piai/ActionAI_dataset/heart/" + str(count) + ".jpg")
        count += 1
    except:
        pass
    
driver.close()
