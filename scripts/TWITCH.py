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
file_handler = RotatingFileHandler(log_file)
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

        session = streamlink.Streamlink()
        streams = session.streams(url)
        logger.debug("URL Streams %s: %s", url, streams)
        if "best" in streams:
            return streams["best"].url
        return None
    except streamlink.exceptions.NoPluginError as err:
        logger.error("URL Error No PluginError %s: %s", url, err)
        return None
    except streamlink.StreamlinkError as err:
        logger.error("URL Error %s: %s", url, err)
        return None

# Função para verificar URL
def check_url(url):
    try:
        response = requests.head(url, timeout=15)
        if response.status_code == 200:
            logger.debug("URL Streams %s: %s", url, response)
            return True
    except requests.exceptions.RequestException as err:
        pass

    try:
        response = requests.head(url, timeout=15, verify=False)
        if response.status_code == 200:
            logger.debug("URL Streams %s: %s", url, response)
            return True
    except requests.exceptions.RequestException as err:
        logger.error("URL Error %s: %s", url, err)
        return False

    return False

# Configuração do Selenium para coleta dos dados do Twitch
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

try:
    # Inicializa o WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # URL da página de busca no Twitch
    url_twitch = "https://www.twitch.tv/search?term=gran%20hermano"
    driver.get(url_twitch)
    time.sleep(5)

    # Faz o parse do HTML da página
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('div', class_='InjectLayout-sc-1i43xsx-0 fMQokC search-result-card')

    # Criação do arquivo .txt
    channel_data = []
    channel_info_path = 'channel_twitch.txt'

    with open(channel_info_path, 'w', encoding='utf-8') as file:
        for card in cards:
            link_tag = card.find('a', class_='ScCoreLink-sc-16kq0mq-0')
            title_tag = card.find('p', class_='CoreText-sc-1txzju1-0')

            if not link_tag or not title_tag or 'href' not in link_tag.attrs:
                continue

            tvg_id = link_tag['href'].strip('/')
            channel_name = title_tag.text.strip()

            output_line = f"{channel_name} | Reality Show's Live | Logo Not Found"
            file.write(output_line + " | \n")
            file.write(f"https://www.twitch.tv/{tvg_id}\n\n")

            channel_data.append({
                'type': 'info',
                'ch_name': channel_name,
                'tvg_id': tvg_id,
                'url': f"https://www.twitch.tv/{tvg_id}",
                'live_title': channel_name  # Adiciona o título da live
            })

    # Criação do arquivo .m3u
    with open("TWITCH.m3u", "w", encoding="utf-8") as m3u_file:
        m3u_file.write(banner)
        prev_item = None

        for item in channel_data:
            link = grab(item['url'])
            if link and check_url(link):
                # Agora o nome do canal vai em tvg-url e o título da live após a vírgula
                m3u_file.write(f'\n#EXTINF:-1 tvg-id="{item["tvg_id"]}" tvg-url="{item["ch_name"]}", {item["live_title"]}')
                m3u_file.write('\n')
                m3u_file.write(link)
                m3u_file.write('\n')

except Exception as e:
    logger.error(f"Erro: {e}")

finally:
    # Fecha o WebDriver
    if 'driver' in locals():
        driver.quit()
