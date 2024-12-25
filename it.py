from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import streamlink

# Configure Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Create the webdriver instance
driver = webdriver.Chrome(options=options)

def get_title(soup):
    title_element = soup.title
    if title_element:
        return title_element.string.strip()
    return None

def format_video_title(title):
    formatted_title = f"{title.replace('/', '_')}"
    return formatted_title

def extract_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('http') and not href.startswith('https://www.youtube.com') or href.startswith('https://secure2.rtve.es'):
            links.append(href)
    return links

def write_m3u_file(links, output_path):
    with open(output_path, 'w') as f:
        for link in links:
            response = requests.get(link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                title = get_title(soup)
                if title:
                    formatted_title = format_video_title(title)
                    # Adiciona a entrada no arquivo M3U
                    f.write(f"{link}\n")

url = "https://www.google.com/search?q=rai&sca_esv=90c55360f106269f&udm=7&tbs=qdr:w,srcf:H4sIAAAAAAAAAMvMKy5JTC9KzNVLzs9Vq8wvLSlNSgWzSzKzS_1KzwUztosTMgpzESr3MErWU1Jz8zJISiJq0xOTUpHyoKgCLxGqdSwAAAA&source=lnt&sa=X&ved=2ahUKEwiGsuLGzLeKAxXwK7kGHWyILAQQpwV6BAgBECw&biw=1920&bih=936&dpr=1"
driver.get(url)

for i in range(2):
    try:
        # Find the last video on the page
        last_video = driver.find_element(By.XPATH, "//a[@class='ScCoreLink-sc-16kq0mq-0 jKBAWW tw-link'][last()]")
        # Scroll to the last video
        actions = ActionChains(driver)
        actions.move_to_element(last_video).perform()
        time.sleep(2)
    except:
        # Scroll down the page
        driver.execute_script("window.scrollBy(0, 10000)")
        time.sleep(2)

try:
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.END)
    time.sleep(5)
    links = []
    for a_tag in driver.find_elements(By.CSS_SELECTOR, "a[href^='http']"):
        href = a_tag.get_attribute("href")
        if href and not href.startswith("https://www.youtube.com"):
            links.append(href)
except NoSuchElementException:
    print("Failed to find the 'body' element.")

driver.quit()

# Definindo o caminho para a pasta raiz
m3u_file_path = os.path.join(os.getcwd(), "it.txt")

# Criação do arquivo M3U na pasta raiz
write_m3u_file(links, m3u_file_path)

print(f"Arquivo M3U foi criado: {m3u_file_path}")
