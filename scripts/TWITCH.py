import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configuração do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

try:
    # Inicializa o WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # URL da página de busca no Twitch
    url_twitch = "https://www.twitch.tv/search?term=gh"
    driver.get(url_twitch)
    time.sleep(5)

    # Faz o parse do HTML da página
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('div', class_='InjectLayout-sc-1i43xsx-0 fMQokC search-result-card')

    # Criação do arquivo .txt
    with open('channel_twitch.txt', 'w', encoding='utf-8') as file:
        for card in cards:
            # Extrai o `tvg-id` do link do canal
            link_tag = card.find('a', class_='ScCoreLink-sc-16kq0mq-0')
            if not link_tag or 'href' not in link_tag.attrs:
                continue
            tvg_id = link_tag['href'].strip('/')

            # Extrai o título do canal
            title_tag = card.find('p', {'data-test-selector': 'search-result-live-channel__title'})
            if not title_tag:
                continue
            channel_title = title_tag.text.strip()

            # Extrai o logo do canal
            img_tag = card.find('img', class_='search-result-card__img')
            logo_url = img_tag['src'] if img_tag else "Logo Not Found"

            # Escreve os dados no arquivo
            output_line = f"{channel_title} | Reality Show's Live | {logo_url}"
            file.write(output_line + " | \n")
            file.write(f"https://www.twitch.tv/{tvg_id}\n\n")

except Exception as e:
    print(f"Erro: {e}")

finally:
    if 'driver' in locals():
        driver.quit()


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

# Processamento para criar o arquivo .m3u
channel_data = []

# Lendo o arquivo .txt gerado na primeira parte
with open('channel_twitch.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(0, len(lines), 2):  # Cada canal ocupa duas linhas no arquivo .txt
        info_line = lines[i].strip()
        url_line = lines[i + 1].strip()

        if not info_line or not url_line:
            continue

        # Extrai informações do arquivo .txt
        parts = info_line.split('|')
        if len(parts) < 3:
            continue

        ch_name = parts[0].strip()
        tvg_logo = parts[2].strip()
        tvg_id = url_line.split('/')[-1].strip()
        url = url_line.strip()

        channel_data.append({
            'type': 'info',
            'ch_name': ch_name,
            'tvg_logo': tvg_logo,
            'tvg_id': tvg_id,
            'url': url
        })

# Geração do arquivo M3U
with open("TWITCH.m3u", "w", encoding="utf-8") as m3u_file:
    m3u_file.write(banner)

    for item in channel_data:
        link = grab(item['url'])
        if link and check_url(link):
            m3u_file.write(f'\n#EXTINF:-1 tvg-id="{item["tvg_id"]}" tvg-logo="{item["tvg_logo"]}", {item["ch_name"]}')
            m3u_file.write('\n')
            m3u_file.write(link)
            m3u_file.write('\n')
