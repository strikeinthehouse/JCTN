import time
import logging
from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import streamlink

# Configuração de logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_file = "log.txt"
file_handler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=5)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Banner do M3U
banner = r'''
#EXTM3U
'''

# Função para obter URL do stream usando Streamlink
def grab(url):
    try:
        if url.endswith('.m3u') or url.endswith('.m3u8') or ".ts" in url:
            return url

        streams = streamlink.streams(url)
        logger.debug("Streams disponíveis para %s: %s", url, streams)
        if "best" in streams:
            return streams["best"].url
        return None
    except streamlink.exceptions.NoPluginError as err:
        logger.error("Plugin não encontrado para %s: %s", url, err)
        return None
    except streamlink.StreamlinkError as err:
        logger.error("Erro do Streamlink para %s: %s", url, err)
        return None

# Função para verificar URL
def check_url(url):
    try:
        response = requests.head(url, timeout=15)
        if response.status_code == 200:
            logger.debug("URL válida: %s", url)
            return True
    except requests.RequestException as err:
        logger.warning("Erro ao verificar URL %s: %s", url, err)
    return False

# Configuração do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

try:
    driver = webdriver.Chrome(options=chrome_options)
    url_twitch = "https://www.twitch.tv/search?term=las%20estrellas"
    driver.get(url_twitch)

    # Esperar até que os elementos dos canais estejam carregados
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-a-target="search-result-live-channel"]'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    live_channels = soup.find_all('div', {'data-a-target': 'search-result-live-channel'})

    channel_data = []
    channel_info_path = 'channel_twitch.txt'

    with open(channel_info_path, 'a', encoding='utf-8') as file:
        for channel in live_channels:
            # Dentro de cada item de canal, encontrar os detalhes do canal
            link_tag = channel.find('a', {'class': 'ScCoreLink-sc-16kq0mq-0 jLbNQX tw-link'})
            title_tag = channel.find('p', {'data-test-selector': 'search-result-live-channel__title'})
            category_tag = channel.find('p', {'data-test-selector': 'search-result-live-channel__category'})
            thumb_tag = channel.find('img', {'class': 'search-result-card__img tw-image'})
            viewers_tag = channel.find('p', {'data-test-selector': 'search-result-live-channel__viewer-count'})

            if not link_tag or not title_tag:
                continue

            # Extrair dados do canal
            tvg_id = link_tag['href'].strip('/')
            channel_name = title_tag.text.strip()  # Aqui pegamos o título do canal
            thumb_url = thumb_tag['src'] if thumb_tag else ''
            group_title = category_tag.text.strip() if category_tag else 'Unknown'
            viewers_count = viewers_tag.text.strip() if viewers_tag else 'Unknown'

            # Grava os dados de cada canal no arquivo
            output_line = f"{channel_name} | {group_title} | {viewers_count} viewers | Logo Not Found"
            file.write(output_line + "\n")
            file.write(f"https://www.twitch.tv/{tvg_id}\n\n")

            channel_data.append({
                'type': 'info',
                'ch_name': channel_name,
                'tvg_id': tvg_id,
                'url': f"https://www.twitch.tv/{tvg_id}",
                'thumb': thumb_url,
                'group_title': group_title,
                'viewers': viewers_count
            })

    # Gerar arquivo M3U com thumbnails
    with open("TWITCH.m3u", "a", encoding="utf-8") as m3u_file:
        m3u_file.write(banner)
        
        for item in channel_data:
            link = grab(item['url'])
            if link and check_url(link):
                m3u_file.write(
                    f"\n#EXTINF:-1 tvg-logo=\"{item['thumb']}\" group-title=\"MÉXICO\",{item['ch_name']}"
                )
                m3u_file.write('\n')
                m3u_file.write(link)
                m3u_file.write('\n')

except Exception as e:
    logger.error("Erro geral: %s", e)

finally:
    if 'driver' in locals():
        driver.quit()
