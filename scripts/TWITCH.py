import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import streamlink
import logging
from logging.handlers import RotatingFileHandler

# Configurando logging
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
    url_twitch = "https://www.twitch.tv/search?term=gran%20hermano&type=channels"
    driver.get(url_twitch)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Filtrar apenas itens com data-a-target="search-result-live-channel"
    live_channels = soup.find_all('div', {'data-a-target': 'search-result-live-channel'})

    channel_data = []
    channel_info_path = 'channel_twitch.txt'

    with open(channel_info_path, 'w', encoding='utf-8') as file:
        for channel in live_channels:
            # Selecionar elementos dentro do bloco live-channel
            link_tag = channel.find('a', href=True)
            title_tag = channel.find('strong', {'data-test-selector': 'search-result-live-channel__name'})
            category_tag = channel.find('p', {'data-test-selector': 'search-result-live-channel__category'})
            thumb_tag = channel.find('img', class_='search-result-card__img')

            if not link_tag or not title_tag:
                continue

            tvg_id = link_tag['href'].strip('/')
            channel_name = title_tag.text.strip()
            thumb_url = thumb_tag['src'] if thumb_tag else ''
            group_title = category_tag.text.strip() if category_tag else 'Unknown'

            output_line = f"{channel_name} | {group_title} | Logo Not Found"
            file.write(output_line + "\n")
            file.write(f"https://www.twitch.tv/{tvg_id}\n\n")

            channel_data.append({
                'type': 'info',
                'ch_name': channel_name,
                'tvg_id': tvg_id,
                'url': f"https://www.twitch.tv/{tvg_id}",
                'thumb': thumb_url,
                'group_title': group_title
            })

    # Gerar arquivo M3U com thumbnails
    with open("TWITCH.m3u", "w", encoding="utf-8") as m3u_file:
        m3u_file.write(banner)
        
        for item in channel_data:
            link = grab(item['url'])
            if link and check_url(link):
                m3u_file.write(
                    f"\n#EXTINF:-1 tvg-logo=\"{item['thumb']}\" group-title=\"Reality Show's Live\",{item['ch_name']}"
                )
                m3u_file.write('\n')
                m3u_file.write(link)
                m3u_file.write('\n')


except Exception as e:
    logger.error("Erro geral: %s", e)

finally:
    if 'driver' in locals():
        driver.quit()


import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import streamlink
import logging
from logging.handlers import RotatingFileHandler

# Configurando logging
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
    url_twitch = "https://www.twitch.tv/directory/all/tags/grandefratello?sort=RELEVANCE"
    driver.get(url_twitch)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Filtrar os canais ao vivo usando o novo seletor
    live_channels = soup.find_all('div', {'data-target': 'directory-first-item'})

    channel_data = []
    channel_info_path = 'channel_twitch.txt'

    with open(channel_info_path, 'w', encoding='utf-8') as file:
        for channel in live_channels:
            # Alterar a extração conforme a nova estrutura HTML
            link_tag = channel.find('a', {'data-test-selector': 'TitleAndChannel'})
            title_tag = channel.find('h3')
            category_tag = channel.find('p', {'data-test-selector': 'GameLink'})
            thumb_tag = channel.find('img', class_='tw-image')

            if not link_tag or not title_tag:
                continue

            tvg_id = link_tag['href'].strip('/')
            channel_name = title_tag.text.strip()
            thumb_url = thumb_tag['src'] if thumb_tag else ''
            group_title = category_tag.text.strip() if category_tag else 'Unknown'

            output_line = f"{channel_name} | {group_title} | Logo Not Found"
            file.write(output_line + "\n")
            file.write(f"https://www.twitch.tv/{tvg_id}\n\n")

            channel_data.append({
                'type': 'info',
                'ch_name': channel_name,
                'tvg_id': tvg_id,
                'url': f"https://www.twitch.tv/{tvg_id}",
                'thumb': thumb_url,
                'group_title': group_title
            })

    # Gerar arquivo M3U com thumbnails
    with open("TWITCH2.m3u", "w", encoding="utf-8") as m3u_file:
        m3u_file.write(banner)
        
        for item in channel_data:
            link = grab(item['url'])
            if link and check_url(link):
                m3u_file.write(
                    f"\n#EXTINF:-1 tvg-logo=\"{item['thumb']}\" group-title=\"Reality Show's Live\",{item['ch_name']}"
                )
                m3u_file.write('\n')
                m3u_file.write(link)
                m3u_file.write('\n')

except Exception as e:
    logger.error("Erro geral: %s", e)

finally:
    if 'driver' in locals():
        driver.quit()


