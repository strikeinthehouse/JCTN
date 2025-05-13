import os
import requests
import logging
from logging.handlers import RotatingFileHandler
import json
from bs4 import BeautifulSoup

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_file = "log.txt"
file_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Cabeçalho do arquivo M3U
banner = "#EXTM3U\n"

# Função para verificar URLs via requisição HTTP com o agente de usuário do Firefox
def check_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Firefox/89.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)  # Usando GET para verificar a URL
        if response.status_code == 200:
            logger.info("URL OK: %s", url)
            return True
        else:
            logger.warning("URL Error %s: Status Code %d", url, response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        logger.error("Request Error %s: %s", url, str(e))
        return False

# Função para processar uma linha #EXTINF
def parse_extinf_line(line):
    group_title = "Undefined"
    tvg_id = "Undefined"
    tvg_logo = "Undefined.png"
    ch_name = "Undefined"
    
    if 'group-title="' in line:
        group_title = line.split('group-title="')[1].split('"')[0]
    if 'tvg-id="' in line:
        tvg_id = line.split('tvg-id="')[1].split('"')[0]
    if 'tvg-logo="' in line:
        tvg_logo = line.split('tvg-logo="')[1].split('"')[0]
    if ',' in line:
        ch_name = line.split(',')[-1].strip()
    
    return ch_name, group_title, tvg_id, tvg_logo

# Função principal para processar o arquivo de entrada
def process_m3u_file(input_file, output_file):
    with open(input_file) as f:
        lines = f.readlines()

    channel_data = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF'):
            ch_name, group_title, tvg_id, tvg_logo = parse_extinf_line(line)
            extra_lines = []
            link = None
            
            # Procura pela URL e ignora linhas intermediárias (#EXTVLCOPT, #KODIPROP, etc.)
            while i + 1 < len(lines):
                i += 1
                next_line = lines[i].strip()
                if next_line.startswith('#'):  # Verifica se a linha começa com '#'
                    extra_lines.append(next_line)  # Armazena a linha extra
                else:
                    link = next_line  # Caso contrário, é a URL do canal
                    break
            
            # Verifica a URL antes de adicionar
            if link and check_url(link):
                # Se o canal não tiver logotipo, buscar o logo automaticamente
                if tvg_logo in ["", "N/A", "Undefined.png"]:  # Condição para logo vazio ou "N/A"
                    logo_url = search_google_images(ch_name)
                    if logo_url:
                        tvg_logo = logo_url
                    else:
                        tvg_logo = "NoLogoFound.png"  # Caso não encontre logo
                
                channel_data.append({
                    'name': ch_name,
                    'group': group_title,
                    'tvg_id': tvg_id,
                    'logo': tvg_logo,
                    'url': link,
                    'extra': extra_lines
                })
        i += 1

    # Gera o arquivo de saída M3U
    with open(output_file, "w") as f:  # Certifique-se de usar "w" e não "a" para sobrescrever
        f.write(banner)
        for channel in channel_data:
            extinf_line = (
                f'#EXTINF:-1 group-title="{channel["group"]}" '
                f'tvg-id="{channel["tvg_id"]}" '
                f'tvg-logo="{channel["logo"]}",{channel["name"]}'
            )
            f.write(extinf_line + '\n')
            for extra in channel['extra']:
                f.write(extra + '\n')
            f.write(channel['url'] + '\n')

    # Salva os dados em JSON para análise posterior
    with open("playlist.json", "w") as f:
        json.dump(channel_data, f, indent=2)

# Função para buscar imagem no Google
def search_google_images(query):
    search_url = f"https://www.google.com/search?hl=pt-BR&q={query}&tbm=isch"  # URL de busca de imagens
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # Buscar a primeira imagem
        img_tags = soup.find_all("img")
        if img_tags:
            # A primeira imagem no Google geralmente é a mais relevante
            img_url = img_tags[1]['src']  # O primeiro item é o logo do Google
            return img_url
    except Exception as e:
        logger.error("Error searching Google images: %s", e)
    
    return None

# Configuração dos arquivos de entrada e saída
input_file = "lista1.M3U"
output_file = "lista1.M3U"

# Executa o processamento
process_m3u_file(input_file, output_file)

import requests

repo_urls = [
    "https://github.com/strikeinthehouse/1/raw/refs/heads/main/lista_1.M3U",
    "https://github.com/strikeinthehouse/1/raw/refs/heads/main/lista_1.M3U"
]

lists = []
for url in repo_urls:
    response = requests.get(url)

    if response.status_code == 200:
        if url.endswith(".m3u"):
            lists.append((url.split("/")[-1], response.text))
        else:
            try:
                contents = response.json()

                m3u_files = [content for content in contents if content["name"].endswith(".m3u")]

                for m3u_file in m3u_files:
                    m3u_url = m3u_file["download_url"]
                    m3u_response = requests.get(m3u_url)

                    if m3u_response.status_code == 200:
                        lists.append((m3u_file["name"], m3u_response.text))
            except requests.exceptions.JSONDecodeError:
                print(f"Error parsing JSON from {url}")
    else:
        print(f"Error retrieving contents from {url}")

lists = sorted(lists, key=lambda x: x[0])

line_count = 0
with open("lista1.M3U", "a") as f:
    for l in lists:
        f.write(l[1])
        line_count += l[1].count("\n")
        if line_count >= 200:  # Stop writing after 200 lines
            break





from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import youtube_dl
import concurrent.futures

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
url_archive = "https://archive.org/details/television?query=XUXA&sort=date"

# Open the desired page
driver.get(url_archive)

# Wait for the page to load
time.sleep(5)

 #Scroll to the bottom of the page
#for _ in range(10):
#    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#    time.sleep(2)

# Find all elements with the specified <a> tags
elements = driver.find_elements(By.CSS_SELECTOR, 'a[title][data-event-click-tracking="GenericNonCollection|ItemTile"]')

# Create a list to store the video URLs and thumbnails
video_infos = []

# Print the href attributes, thumbnails, and add them to video_infos
for element in elements:
    href = element.get_attribute("href")
    if href:
        # Extract the thumbnail URL
        img_element = element.find_element(By.XPATH, './/img')
        thumbnail_src = img_element.get_attribute('src') if img_element else ''
        # Ensure the thumbnail URL is absolute
        if thumbnail_src and not thumbnail_src.startswith('http'):
            thumbnail_src = 'https://archive.org' + thumbnail_src
        video_infos.append((href, thumbnail_src))
        print("Adicionando URL:", href)
        print("Thumbnail:", thumbnail_src)

# Close the webdriver
driver.quit()


# Function to get the direct stream URL and title with error handling
def get_stream_info(url):
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'noplaylist': True,
        'outtmpl': '/dev/null',
        'geturl': True
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'Video Desconhecido')
            stream_url = info_dict.get('url', '')
            return video_title, stream_url
    except Exception as e:
        print(f"Error fetching info for {url}: {e}")
        return None, None  # Return None for failed entries

# Generate the EXTINF lines with tvg-logo and URLs
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(lambda info: get_stream_info(info[0]), video_infos))

# Write the EXTINF formatted lines to a file
with open('lista1.M3U', 'a') as file:
    file.write('#EXTM3U\n')  # Add the EXT3MU header
    for (url, thumbnail), (title, stream_url) in zip(video_infos, results):
        if stream_url:
            tvg_logo = f'tvg-logo="{thumbnail}"' if thumbnail else ''
            file.write(f'#EXTINF:-1 group-title="VOD" {tvg_logo},{title}\n{stream_url}\n')

print("A playlist M3U foi gerada com sucesso.")

import yt_dlp

# Define a URL de pesquisa
search_query = 'https://www.youtube.com/results?search_query=%E5%9C%B0%E9%9C%87'

# Define as opções para o yt-dlp
ydl_opts = {
    'format': 'best',  # Obtém a melhor qualidade
    'write_all_thumbnails': False,  # Não faz download das thumbnails
    'skip_download': True,  # Não faz download do vídeo
    'extract_flat': True,  # Extrai apenas a informação sobre o vídeo
    'force_generic_extractor': True,
}

# Função para obter as URLs dos vídeos a partir da pesquisa
def get_video_urls(query_url, max_results=10):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(query_url, download=False)
        videos = info_dict.get('entries', [])
        # Filtra apenas links de vídeos, ignorando canais e playlists
        video_entries = [entry for entry in videos if entry.get('_type') == 'video']
        return video_entries[:max_results]

# Função para salvar os resultados em um arquivo M3U com tvg-logo
def save_to_m3u(video_list, filename='YOUTUBEPLAY1.m3u'):
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for video in video_list:
                video_id = video.get('id', '')
                url = video.get('url', '')
                title = video.get('title', 'Unknown Title')
                thumbnail = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
                description = video.get('description', '')[:10]

                if not url:
                    print(f"Erro ao gravar informações do vídeo {video_id}: 'url'")
                    continue

                # Grava no arquivo M3U
                f.write(f"#EXTINF:-1 group-title=\"YOUTUBE\" tvg-logo=\"{thumbnail}\",{title} - {description}...\n")
                f.write(f"{url}\n")
                f.write("\n")
    except Exception as e:
        print(f"Erro ao criar o arquivo .m3u: {e}")

# Obter vídeos e salvar no arquivo M3U
videos = get_video_urls(search_query)
save_to_m3u(videos)

print(f"Arquivo M3U gerado com {len(videos)} vídeos.")









import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import yt_dlp
import re
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")



# Create the webdriver instance
driver = webdriver.Chrome(options=options)

# URL da página desejada
url_youtube = "https://www.youtube.com/results?search_query=%E5%9C%B0%E9%9C%87"

# Abrir a página desejada
driver.get(url_youtube)

# Aguardar alguns segundos para carregar todo o conteúdo da página
time.sleep(5)

from selenium.webdriver.common.keys import Keys
for i in range(5):
    try:
        # Find the last video on the page
        last_video = driver.find_element(By.XPATH, "//a[@class='ScCoreLink-sc-16kq0mq-0 jKBAWW tw-link'][last()]")
        # Scroll to the last video
        actions = ActionChains(driver)
        actions.move_to_element(last_video).perform()
        time.sleep(2)
    except:
        # Press the down arrow key for 50 seconds
        driver.execute_script("window.scrollBy(0, 10000)")
        time.sleep(2)

# Get the page source again after scrolling to the bottom
html_content = driver.page_source

time.sleep(5)

# Find the links and titles of the videos found
try:
    soup = BeautifulSoup(html_content, "html.parser")
    videos = soup.find_all("a", id="video-title", class_="yt-simple-endpoint style-scope ytd-video-renderer")
    links = ["https://www.youtube.com" + video.get("href") for video in videos]
    titles = [video.get("title") for video in videos]
except Exception as e:
    print(f"Erro: {e}")
finally:
    # Close the driver
    driver.quit()

# Define as opções para o youtube-dl
ydl_opts = {
    'format': 'best',  # Obtém a melhor qualidade
    'write_all_thumbnails': False,  # Não faz download das thumbnails
    'skip_download': True,  # Não faz download do vídeo
}

# Get the playlist and write to file
try:
    with open('./YOUTUBEPLAY1.m3u', 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for i, link in enumerate(links):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
            if 'url' not in info:
                print(f"Erro ao gravar informações do vídeo {link}: 'url'")
                continue
            url = info['url']
            thumbnail_url = info['thumbnail']
            description = info.get('description', '')[:10]
            title = info.get('title', '')
            f.write(f"#EXTINF:-1 group-title=\"YOUTUBE\" tvg-logo=\"{thumbnail_url}\",{title} - {description}...\n")
            f.write(f"{url}\n")
            f.write("\n")
except Exception as e:
    print(f"Erro ao criar o arquivo .m3u8: {e}")








import requests
from datetime import datetime, timezone, timedelta





# Defina o fuso horário do Brasil
brazil_timezone = timezone(timedelta(hours=-3))

def is_within_time_range(start_time, end_time):
    current_time = datetime.now(brazil_timezone)
    return start_time <= current_time <= end_time

# Horários locais do Brasil para 17h30 e 23h00
start_time_br = datetime.now(brazil_timezone).replace(hour=17, minute=30, second=0, microsecond=0)
end_time_br = datetime.now(brazil_timezone).replace(hour=23, minute=0, second=0, microsecond=0)

# Nome do arquivo de saída
output_file = "lista1.M3U"

if is_within_time_range(start_time_br, end_time_br):
    m3upt_url = "https://github.com/LITUATUI/M3UPT/raw/main/M3U/M3UPT.m3u"
    m3upt_response = requests.get(m3upt_url)

    if m3upt_response.status_code == 200:
        m3upt_lines = m3upt_response.text.split('\n')[:25]

        with open(output_file, "a") as f:
            for line in m3upt_lines:
                f.write(line + '\n')
else:
    with open(output_file, "a") as f:
        f.write("#EXTM3U\n")





#GLOBO


from datetime import datetime
import pytz
import requests

# Definir o fuso horário do Brasil
brazil_timezone = pytz.timezone('America/Sao_Paulo')

def is_within_time_range(start_time, end_time):
    current_time = datetime.now(brazil_timezone)
    return start_time <= current_time <= end_time

# Verificar o dia da semana (0 = segunda-feira, 6 = domingo)
current_weekday = datetime.now(brazil_timezone).weekday()

# Horários locais do Brasil para 11h30 e 13h30
start_time_br_morning = datetime.now(brazil_timezone).replace(hour=11, minute=30, second=0, microsecond=0)
end_time_br_morning = datetime.now(brazil_timezone).replace(hour=13, minute=30, second=0, microsecond=0)

# Horários locais do Brasil para 19h00 e 19h45
start_time_br_evening = datetime.now(brazil_timezone).replace(hour=19, minute=0, second=0, microsecond=0)
end_time_br_evening = datetime.now(brazil_timezone).replace(hour=19, minute=45, second=0, microsecond=0)

# Horários locais do Brasil para 17h30 e 23h00
start_time_br_night = datetime.now(brazil_timezone).replace(hour=17, minute=30, second=0, microsecond=0)
end_time_br_night = datetime.now(brazil_timezone).replace(hour=20, minute=0, second=0, microsecond=0)

# Nome do arquivo de saída
output_file = "lista1.M3U"

# Verificar se o dia é de segunda a sábado (0 a 5)
if current_weekday < 6:
    if (is_within_time_range(start_time_br_morning, end_time_br_morning) or 
        is_within_time_range(start_time_br_evening, end_time_br_evening) or
        is_within_time_range(start_time_br_night, end_time_br_night)):

        m3upt_url = "https://github.com/strikeinthehouse/1/raw/main/lista2.M3U"
        m3upt_response = requests.get(m3upt_url)

        if m3upt_response.status_code == 200:
            m3upt_lines = m3upt_response.text.split('\n')[:422]

            with open(output_file, "a") as f:
                for line in m3upt_lines:
                    f.write(line + '\n')
    else:
        with open(output_file, "a") as f:
            f.write("#EXTM3U\n")



        





import requests
from datetime import datetime, timezone, timedelta

# Defina o fuso horário do Brasil
brazil_timezone = timezone(timedelta(hours=-3))

def is_within_time_range(start_time, end_time):
    current_time = datetime.now(brazil_timezone)
    return start_time <= current_time <= end_time

# Horários locais do Brasil para 17h30 e 23h00
start_time_br = datetime.now(brazil_timezone).replace(hour=6, minute=00, second=0, microsecond=0)
end_time_br = datetime.now(brazil_timezone).replace(hour=23, minute=59, second=0, microsecond=0)

# Nome do arquivo de saída
output_file = "lista1.M3U"

if is_within_time_range(start_time_br, end_time_br):
    m3upt_url = "https://github.com/punkstarbr/STR-YT/raw/main/lista1.M3U"
    m3upt_response = requests.get(m3upt_url)

    if m3upt_response.status_code == 200:
        m3upt_lines = m3upt_response.text.split('\n')[:500]

        with open(output_file, "a") as f:
            for line in m3upt_lines:
                f.write(line + '\n')
else:
    with open(output_file, "a") as f:
        f.write("#EXTM3U\n")

import requests
from datetime import datetime, timezone, timedelta

# Defina o fuso horário do Brasil
brazil_timezone = timezone(timedelta(hours=-3))

def is_within_time_range(start_time, end_time):
    current_time = datetime.now(brazil_timezone)
    return start_time <= current_time <= end_time

# Horários locais do Brasil para 17h30 e 23h00
start_time_br = datetime.now(brazil_timezone).replace(hour=6, minute=00, second=0, microsecond=0)
end_time_br = datetime.now(brazil_timezone).replace(hour=23, minute=59, second=0, microsecond=0)

# Nome do arquivo de saída
output_file = "lista1.M3U"

if is_within_time_range(start_time_br, end_time_br):
    m3upt_url = "https://github.com/strikeinthehouse/M3UPT/raw/main/M3U/M3UPT.m3u"
    m3upt_response = requests.get(m3upt_url)

    if m3upt_response.status_code == 200:
        m3upt_lines = m3upt_response.text.split('\n')[:500]

        with open(output_file, "a") as f:
            for line in m3upt_lines:
                f.write(line + '\n')
else:
    with open(output_file, "a") as f:
        f.write("#EXTM3U\n")

import requests

# Lista de URLs dos repositórios do GitHub
repo_urls = [
    "https://api.github.com/repos/strikeinthehouse/JCTN/contents",
]

# Função para obter os URLs dos arquivos .m3u de um repositório GitHub
def get_m3u_urls(repo_url):
    m3u_urls = []
    try:
        response = requests.get(repo_url)
        response.raise_for_status()  # Lança uma exceção para erros HTTP
        content = response.json()
        for item in content:
            if item['name'].endswith('.m3u'):
                m3u_urls.append(item['download_url'])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {repo_url}: {e}")
    return m3u_urls

# Lista para armazenar todos os URLs dos arquivos .m3u
all_m3u_urls = []

# Itera sobre os URLs dos repositórios e coleta os URLs dos arquivos .m3u
for url in repo_urls:
    if "api.github.com" in url:
        # Se for uma API do GitHub, obtenha os URLs dos arquivos .m3u
        m3u_urls = get_m3u_urls(url)
        all_m3u_urls.extend(m3u_urls)
    elif url.endswith('.m3u'):
        # Se for um arquivo .m3u diretamente, adiciona à lista
        all_m3u_urls.append(url)

# Lista para armazenar o conteúdo dos arquivos .m3u
all_content = []

# Itera sobre os URLs dos arquivos .m3u e coleta o conteúdo de cada um
for url in all_m3u_urls:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança uma exceção para erros HTTP
        if response.status_code == 200:
            content = response.text.strip()
            all_content.append(content)
            print(f"Conteúdo do arquivo {url} coletado com sucesso.")
        else:
            print(f"Erro ao acessar {url}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")

# Verifica se há conteúdo para escrever no arquivo .m3u
if all_content:
    with open('lista1.M3U', 'a', encoding='utf-8') as f:
        f.write('#EXTM3U\n')  # Cabeçalho obrigatório para arquivos .m3u
        for content in all_content:
            f.write(content + '\n')

    print('Arquivo lista1.m3u foi criado com sucesso.')
else:
    print('Nenhum conteúdo de arquivo .m3u foi encontrado para escrever.')

import requests

# Lista de URLs dos repositórios do GitHub
repo_urls = [
    "https://api.github.com/repos/punkstarbr/STR-YT/contents"
]

# Função para obter os URLs dos arquivos .m3u de um repositório GitHub
def get_m3u_urls(repo_url):
    m3u_urls = []
    try:
        response = requests.get(repo_url)
        response.raise_for_status()  # Lança uma exceção para erros HTTP
        content = response.json()
        for item in content:
            if item['name'].endswith('.m3u'):
                m3u_urls.append(item['download_url'])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {repo_url}: {e}")
    return m3u_urls

# Lista para armazenar todos os URLs dos arquivos .m3u
all_m3u_urls = []

# Itera sobre os URLs dos repositórios e coleta os URLs dos arquivos .m3u
for url in repo_urls:
    if "api.github.com" in url:
        # Se for uma API do GitHub, obtenha os URLs dos arquivos .m3u
        m3u_urls = get_m3u_urls(url)
        all_m3u_urls.extend(m3u_urls)
    elif url.endswith('.m3u'):
        # Se for um arquivo .m3u diretamente, adiciona à lista
        all_m3u_urls.append(url)

# Lista para armazenar o conteúdo dos arquivos .m3u
all_content = []

# Itera sobre os URLs dos arquivos .m3u e coleta o conteúdo de cada um
for url in all_m3u_urls:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança uma exceção para erros HTTP
        if response.status_code == 200:
            content = response.text.strip()
            all_content.append(content)
            print(f"Conteúdo do arquivo {url} coletado com sucesso.")
        else:
            print(f"Erro ao acessar {url}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")

# Verifica se há conteúdo para escrever no arquivo .m3u
if all_content:
    with open('lista1.M3U', 'a', encoding='utf-8') as f:
        f.write('#EXTM3U\n')  # Cabeçalho obrigatório para arquivos .m3u
        for content in all_content:
            f.write(content + '\n')

    print('Arquivo lista1.m3u foi criado com sucesso.')
else:
    print('Nenhum conteúdo de arquivo .m3u foi encontrado para escrever.')


def limitar_arquivo_m3u(arquivo_original, arquivo_saida, limite_linhas=2800):
    try:
        # Abre o arquivo M3U original para leitura
        with open(arquivo_original, 'r') as file:
            # Lê todas as linhas do arquivo
            linhas = file.readlines()

        # Filtra as linhas para remover linhas vazias e linhas com certos padrões
        linhas_filtradas = [
            linha for linha in linhas 
            if linha.strip() and 
            '#EXTVLCOPT:http-user-agent=iPhone' not in linha and 
            '####' not in linha and 
            '_____' not in linha and 
            '#EXTVLCOPT--http-reconnect=true' not in linha
        ]

        # Limita as linhas conforme o valor de limite_linhas
        linhas_limitadas = linhas_filtradas[:limite_linhas]
        
        # Abre o arquivo de saída para escrita
        with open(arquivo_saida, 'w') as file:
            # Escreve as linhas limitadas no novo arquivo
            file.writelines(linhas_limitadas)
        
        print(f"O arquivo {arquivo_original} foi limitado a {limite_linhas} linhas e salvo como {arquivo_saida}.")
    
    except FileNotFoundError:
        print(f"Erro: O arquivo {arquivo_original} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Nome do arquivo original e do arquivo de saída
arquivo_original = 'lista1.M3U'
arquivo_saida = 'lista1.M3U'

# Chama a função para limitar o arquivo
limitar_arquivo_m3u(arquivo_original, arquivo_saida)
