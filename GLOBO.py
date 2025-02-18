from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import concurrent.futures

# Configurações do Chrome
options = Options()
options.add_argument("--headless")  # Executa sem interface gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# URLs dos vídeos Globoplay
globoplay_urls = [
    "https://kcnawatch.org/kctv-archive/67b49115648d7/",  # EPTV 1ª Edição - Ribeirão Preto
    "https://globoplay.globo.com/ao-vivo/5472979/",
]

def extract_globoplay_data(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    try:
        play_button = driver.find_element(By.CSS_SELECTOR, "button.poster__play-wrapper")
        if play_button:
            play_button.click()
            time.sleep(15)
    except Exception as e:
        print("Erro ao clicar no botão de reprodução:", e)

    time.sleep(55)  # Espera a página carregar
    title = driver.title
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    m3u8_url = None
    thumbnail_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name'] and not thumbnail_url:
            thumbnail_url = entry['name']
    driver.quit()
    return title, m3u8_url, thumbnail_url

with open("lista1.m3u", "w") as output_file:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(extract_globoplay_data, url): url for url in globoplay_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title, m3u8_url, thumbnail_url = future.result()
                if m3u8_url:
                    thumbnail_url = thumbnail_url if thumbnail_url else ""
                    output_file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="GLOBO AO VIVO", {title}\n')
                    output_file.write(f"{m3u8_url}\n")
                    print(f"Processado com sucesso: {url}")
                else:
                    print(f"M3U8 não encontrado para {url}")
            except Exception as e:
                print(f"Erro ao processar {url}: {e}")
# Executa o processamento
process_m3u_file(input_url, output_file)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
import requests
from bs4 import BeautifulSoup

# Configurar as opções do Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Criar a instância do webdriver
driver = webdriver.Chrome(options=options)

def get_title(soup):
    title_element = soup.title
    return title_element.string.strip() if title_element else None

def format_video_title(title):
    return title.replace('/', '_')

def write_m3u_file(links, output_path):
    with open(output_path, 'w') as f:
        for link in links:
            response = requests.get(link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                title = get_title(soup)
                if title:
                    f.write(f"{link}\n")

url = "https://duckduckgo.com/?q=assista+ao+vivo+site%3Aglobo.com&t=h_&iar=videos&start=1&iax=videos&ia=videos"
driver.get(url)
time.sleep(5)

links = []
video_tiles = driver.find_elements(By.CLASS_NAME, "tile")
for tile in video_tiles:
    data_link = tile.get_attribute("data-link")
    if data_link and data_link.startswith("http"):
        links.append(data_link)

driver.quit()

# Definir o caminho do arquivo
m3u_file_path = os.path.join(os.getcwd(), "it.txt")
write_m3u_file(links, m3u_file_path)

print(f"Arquivo M3U foi criado: {m3u_file_path}")
