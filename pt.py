from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


# Configure Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Create the webdriver instance
driver = webdriver.Chrome(options=options)

# URL of the desired page
url_archive = "https://tviplayer.iol.pt/videos/ultimos/1/canal:"

# Open the desired page
driver.get(url_archive)

# Wait for the page to load
time.sleep(5)  # Adjust the sleep time if needed to ensure page load

# Find all relevant video links
video_elements = driver.find_elements(By.CSS_SELECTOR, 'a.item')

# Prepare to write the links to a file
with open('pt.txt', 'a') as file:
    for element in video_elements:
        link = element.get_attribute('href')
        # Check if the link is valid and not empty
        if link:
            full_link = f"{link}"
            file.write(full_link + '\n')

# Close the driver
driver.quit()



import subprocess
import json
import os
import requests
from bs4 import BeautifulSoup

def get_video_details_youtube(url):
    """Obtém os detalhes dos vídeos usando youtube-dl."""
    try:
        result = subprocess.run(
            ['youtube-dl', '-j', '--flat-playlist', url],
            capture_output=True,
            text=True,
            check=True
        )
        entries = result.stdout.strip().split('\n')
        details = [json.loads(entry) for entry in entries]
        return details

    except subprocess.CalledProcessError:
        return []

def get_video_details_yt_dlp(url):
    """Obtém os detalhes dos vídeos usando yt-dlp."""
    try:
        result = subprocess.run(
            ['yt-dlp', '-j', '--flat-playlist', url],
            capture_output=True,
            text=True,
            check=True
        )
        entries = result.stdout.strip().split('\n')
        details = [json.loads(entry) for entry in entries]
        return details

    except subprocess.CalledProcessError:
        return []

def get_video_details_streamlink(url):
    """Obtém os detalhes dos vídeos usando streamlink."""
    try:
        # Usa o streamlink para obter a URL do stream
        result = subprocess.run(
            ['streamlink', '--stream-url', url, 'best'],
            capture_output=True,
            text=True,
            check=True
        )
        stream_url = result.stdout.strip()
        
        # Faz uma requisição para obter o título da página
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = get_title(soup)
        
        if stream_url and title:
            return [{'url': stream_url, 'title': title, 'thumbnail': 'N/A'}]
        else:
            return []

    except subprocess.CalledProcessError:
        return []
    except requests.RequestException:
        return []

def get_title(soup):
    """Obtém o título do vídeo a partir da BeautifulSoup."""
    title_element = soup.title
    if title_element:
        return title_element.string.strip()
    return "No Title"

def get_video_details(url):
    """Obtém os detalhes dos vídeos usando youtube-dl, yt-dlp ou streamlink."""
    details = get_video_details_youtube(url)
    if details:
        return details

    details = get_video_details_yt_dlp(url)
    if details:
        return details

    details = get_video_details_streamlink(url)
    if details:
        return details

    print(f"Falha ao obter detalhes para a URL {url}.")
    return []

def write_m3u_file(details, filename):
    """Escreve os detalhes dos vídeos no formato M3U em um arquivo."""
    with open(filename, 'a', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        
        for entry in details:
            video_url = entry.get('url')
            thumbnail_url = entry.get('thumbnail', 'N/A')
            title = entry.get('title', 'No Title')

            if video_url:
                file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="VOD PT",{title}\n')
                file.write(f"{video_url}\n")
            else:
                print("URL do vídeo não encontrada.")

def process_urls_from_file(input_file):
    """Lê URLs de um arquivo e processa cada uma para criar um único arquivo M3U."""
    if not os.path.exists(input_file):
        print(f"O arquivo {input_file} não foi encontrado.")
        return
    
    all_details = []
    
    with open(input_file, 'r') as file:
        urls = file.readlines()
    
    urls = [url.strip() for url in urls if url.strip()]
    
    for i, url in enumerate(urls):
        print(f"Processando URL {i + 1}: {url}")
        details = get_video_details(url)
        
        if details:
            all_details.extend(details)
        else:
            print(f"Nenhum URL encontrado para a URL {url}.")
    
    filename = 'lista1.M3U'
    write_m3u_file(all_details, filename)
    print(f"Arquivo {filename} criado com sucesso.")

if __name__ == "__main__":
    input_file = 'pt.txt'
    process_urls_from_file(input_file)
