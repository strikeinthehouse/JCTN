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

driver = None
channel_data = []
processed_channels = set()  # Usando um conjunto para armazenar IDs já processados

try:
    driver = webdriver.Chrome(options=chrome_options)

    # URLs de tags fornecidas (incluindo as novas URLs)
    urls_twitch = [
        "https://www.twitch.tv/directory/all/tags/lacasadelosfamosos",  # Nova tag
        "https://www.twitch.tv/directory/all/tags/GrandeFratello",  # Tag existente
        "https://www.twitch.tv/directory/all/tags/GranHermano",  # Nova tag
        "https://www.twitch.tv/directory/all/tags/BBB24HORAS",
        "https://www.twitch.tv/directory/all/tags/granhermanoargentina",  # Nova tag

    ]

    
    for url_twitch in urls_twitch:
        driver.get(url_twitch)

        # Esperar até que os elementos dos canais estejam carregados
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-target="directory-game__card_container"]'))
        )

        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            live_channels = soup.find_all('div', {'data-target': 'directory-game__card_container'})

            for channel in live_channels:
                # Dentro de cada item de canal, encontrar os detalhes do canal
                article_tag = channel.find('article', {'data-a-target': True})
                if not article_tag:
                    continue

                link_tag = article_tag.find('a', {'data-test-selector': 'TitleAndChannel'})
                title_tag = article_tag.find('h3')
                category_tag = article_tag.find('p', {'data-a-target': 'preview-card-game-link'})

                # Alteração na extração da thumbnail para pegar da estrutura dada
                thumb_tag = article_tag.find('div', {'class': 'Layout-sc-1xcs6mc-0 eFvOkl'})
                if thumb_tag:
                    img_tag = thumb_tag.find('img', class_='tw-image')
                    thumb_url = img_tag['src'] if img_tag else ''
                else:
                    thumb_url = ''

                # Extração do texto da tag extra (categoria/tag)
                tag_tag = article_tag.find('div', {'class': 'ScTagContent-sc-14s7ciu-1 VkjPH'})
                tag_text = tag_tag.find('span').text.strip() if tag_tag else 'Unknown'

                # Verificar se o link e o título existem antes de continuar
                if not link_tag or not title_tag:
                    continue

                tvg_id = link_tag['href'].strip('/').split('/')[-1]
                channel_name = title_tag.text.strip()
                group_title = category_tag.text.strip() if category_tag else "Reality Show's Live"

                # Verificar se o canal já foi processado
                if tvg_id in processed_channels:
                    continue  # Ignorar canais duplicados

                # Adicionar o canal ao conjunto de canais processados
                processed_channels.add(tvg_id)

                # Acumular os dados de cada canal
                channel_data.append({
                    'type': 'info',
                    'ch_name': channel_name,
                    'tvg_id': tvg_id,
                    'url': f"https://www.twitch.tv/{tvg_id}",
                    'thumb': thumb_url,
                    'group_title': group_title,
                    'tag_text': tag_text  # Adicionando o texto extra
                })

            # Verificar se há uma página seguinte e navegar para ela
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'button[data-a-target="pagination-forward-button"]')
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(3)  # Esperar carregar a próxima página
                else:
                    break  # Não há mais páginas
            except Exception as e:
                logger.error("Erro ao tentar navegar para a próxima página: %s", e)
                break  # Se não houver próximo botão ou houver erro, saímos do loop

except Exception as e:
    logger.error("Erro geral: %s", e)

finally:
    if driver:
        driver.quit()

# Adicionar o canal 'universoreality_gh' manualmente se não aparecer nos resultados
manual_channel = {
    'type': 'info',
    'ch_name': 'GHDUO',
    'tvg_id': 'Telecinco',
    'url': 'https://www.twitch.tv/servidor225',
    'thumb': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_servidor225-1920x1090.jpg',
    'group_title': "Reality Show's Live",  # Modificado para o título correto
    'tag_text': 'Reality Show',  # Tag personalizada
}


# Verificar se o canal manual já foi adicionado (pelo 'tvg_id') e adicioná-lo manualmente se necessário
if manual_channel['tvg_id'] not in processed_channels:
    channel_data.append(manual_channel)
    processed_channels.add(manual_channel['tvg_id'])
    logger.info(f"Canal {manual_channel['url']} adicionado manualmente.")

# Gerar arquivo M3U com thumbnails e texto extra
with open("TWITCH2.m3u", "w", encoding="utf-8") as m3u_file:
    m3u_file.write(banner)

    for item in channel_data:
        # Ignorar canais específicos
        if item['url'] in ["https://www.twitch.tv/jibarook", "https://www.twitch.tv/daniveintiuno"]:
            logger.info(f"Canal {item['url']} ignorado.")
            continue  # Pular para o próximo canal
        
        link = grab(item['url'])
        if link and check_url(link):
            # Adicionando o texto extra (tag) antes do nome do canal
            m3u_file.write(
                f"\n#EXTINF:-1 tvg-logo=\"{item['thumb']}\" group-title=\"{item['group_title']}\" tvg-id=\"{item['tvg_id']}\",{item['tag_text']} - {item['ch_name']}"
            )
            m3u_file.write('\n')
            m3u_file.write(link)
            m3u_file.write('\n')

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
    url_twitch = "https://www.twitch.tv/search?term=bigbrotherbrasil"
    driver.get(url_twitch)

    # Esperar até que os elementos dos canais estejam carregados
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-a-target="search-result-live-channel"]'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    live_channels = soup.find_all('div', {'data-a-target': 'search-result-live-channel'})

    channel_data = []
    channel_info_path = 'channel_twitch.txt'

    with open(channel_info_path, 'w', encoding='utf-8') as file:
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



import os
def limitar_arquivo_m3u(arquivo_original, arquivo_saida, limite_linhas=30000):
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
arquivo_original = 'TWITCH.m3u'
arquivo_saida = 'TWITCH.m3u'  # Mudando o nome do arquivo de saída para evitar sobrescrição

# Chama a função para limitar o arquivo a 60 linhas
limitar_arquivo_m3u(arquivo_original, arquivo_saida, limite_linhas=40)
