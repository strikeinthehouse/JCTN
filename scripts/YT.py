import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import yt_dlp
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import concurrent.futures
import os
import requests
import streamlink
import yt_dlp

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")


driver = webdriver.Chrome(options=chrome_options)

# URL da página desejada
url_youtube = "https://www.youtube.com/results?search_query=zadruga&sp=CAMSAkAB"

# Open the desired page
driver.get(url_youtube)

# Wait for the page to load
time.sleep(5)

# Find all link elements in the search results
try:
    link_elements = driver.find_elements(By.XPATH, "//a[@class='yt-simple-endpoint style-scope yt-formatted-string']")
    if link_elements:
        # Get the href attribute of the first link element
        second_link_element = link_elements[1]
        link_href = second_link_element.get_attribute("href")
        if link_href:
            # Modify the link to include 'https://www.youtube.com' and '/live'
            vindodonavegador6 = link_href + "/live"
            print(vindodonavegador6)
        else:
            print("Link href not found")
    else:
        print("Link elements not found")

except Exception as e:
    print(f"Erro: {e}")
    vindodonavegador6 = "https://www.youtube.com/watch?v=_9Grp5tYrYI"
    print(vindodonavegador6)

# Close the browser
driver.quit()
