import requests
from bs4 import BeautifulSoup

# URL do repositório GitHub com o caminho correto para a pasta
repo_url = "https://api.github.com/repos/AINMcl/MonitorTV/contents/Monitores/Senal"

# Função para obter os URLs dos arquivos .html de um repositório do GitHub
def get_html_urls(repo_url):
    html_urls = []
    try:
        response = requests.get(repo_url)
        response.raise_for_status()  # Lança uma exceção para erros HTTP
        content = response.json()
        for item in content:
            if item['name'].endswith('.html'):
                html_urls.append(item['download_url'])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {repo_url}: {e}")
    return html_urls

# Função para extrair o título e os links m3u8 de um arquivo HTML
def extract_title_and_m3u8_links(html_content):
    title = None
    m3u8_links = []
    
    # Usa o BeautifulSoup para fazer o parsing do HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extrai o título da tag <title>
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.text.strip()
    
    # Encontra todos os links .m3u8 no conteúdo
    for link in soup.find_all('a', href=True):
        if '.m3u8' in link['href']:
            m3u8_links.append(link['href'])
    
    return title, m3u8_links

# Função para gerar o arquivo .m3u com os links e títulos extraídos
def generate_m3u_file(html_urls):
    with open('HTML.m3u', 'w', encoding='utf-8') as m3u_file:
        m3u_file.write('#EXTM3U\n')  # Cabeçalho obrigatório para arquivos .m3u
        
        for url in html_urls:
            try:
                # Baixa o conteúdo do arquivo HTML diretamente
                response = requests.get(url)
                response.raise_for_status()
                
                # Extrai o título e os links m3u8 do conteúdo HTML
                title, m3u8_links = extract_title_and_m3u8_links(response.text)
                
                if title and m3u8_links:
                    for m3u8_link in m3u8_links:
                        # Formata e escreve cada entrada no arquivo .m3u
                        m3u8_link = m3u8_link if m3u8_link.startswith('http') else 'http:' + m3u8_link
                        m3u8_file_line = f"#EXTINF:-1, {title}\n{m3u8_link}?DVR\n"
                        m3u8_file_line = m3u8_file_line.strip()  # Remove espaços extras
                        m3u8_file.write(m3u8_file_line + '\n')
                        print(f"Adicionado {title} - {m3u8_link}?DVR")
                
            except Exception as e:
                print(f"Erro ao processar {url}: {e}")
        
    print("Arquivo HTML.m3u gerado com sucesso.")

# Obter os links dos arquivos .html do repositório GitHub
all_html_urls = get_html_urls(repo_url)

# Verifica se há URLs para processar
if all_html_urls:
    print(f"Arquivos .html encontrados: {len(all_html_urls)}")
    for url in all_html_urls:
        print(f"Arquivo .html: {url}")
    
    # Gera o arquivo .m3u com os links e títulos extraídos
    generate_m3u_file(all_html_urls)
else:
    print('Nenhum arquivo .html encontrado.')



    
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

    # URLs de tags fornecidas
    urls_twitch = [
        "https://www.twitch.tv/directory/all/tags/bb18",
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
    'ch_name': 'CHINA',
    'tvg_id': 'Telecinco',
    'url': 'https://www.twitch.tv/hstceline',
    'thumb': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_universoreality_gh-1920x1090.jpg',
    'group_title': "Reality Show's Live",  # Modificado para o título correto
    'tag_text': 'Reality Show',  # Tag personalizada
}

# Verificar se o canal manual já foi adicionado (pelo 'tvg_id') e adicioná-lo manualmente se necessário
if manual_channel['tvg_id'] not in processed_channels:
    channel_data.append(manual_channel)
    processed_channels.add(manual_channel['tvg_id'])
    logger.info(f"Canal {manual_channel['url']} adicionado manualmente.")

# Gerar arquivo M3U com thumbnails e texto extra
with open("lista1.m3u", "w", encoding="utf-8") as m3u_file:
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
    url_twitch = "https://www.twitch.tv/search?term=universoreality"
    driver.get(url_twitch)

    # Esperar até que os elementos dos canais estejam carregados
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-target="directory-game__card_container"]'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    live_channels = soup.find_all('div', {'data-target': 'directory-game__card_container'})

    channel_data = []
    channel_info_path = 'channel_twitch.txt'

    with open(channel_info_path, 'w', encoding='utf-8') as file:
        for channel in live_channels:
            # Dentro de cada item de canal, encontrar os detalhes do canal
            article_tag = channel.find('article', {'data-a-target': True})
            if not article_tag:
                continue

            link_tag = article_tag.find('a', {'data-test-selector': 'TitleAndChannel'})
            title_tag = article_tag.find('h3')
            category_tag = article_tag.find('a', {'data-test-selector': 'GameLink'})
            thumb_tag = article_tag.find('img', class_='tw-image-avatar')
            viewers_tag = article_tag.find('div', {'class': 'tw-media-card-stat'})

            if not link_tag or not title_tag:
                continue

            tvg_id = link_tag['href'].strip('/')
            channel_name = title_tag.text.strip()
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
    with open("PORRA2.m3u", "a", encoding="utf-8") as m3u_file:
        m3u_file.write(banner)
        
        for item in channel_data:
            link = grab(item['url'])
            if link and check_url(link):
                m3u_file.write(
                    f"\n#EXTINF:-1 tvg-logo=\"{item['thumb']}\" group-title=\"Reality Show's Live\",{item['ch_name']} ({item['viewers']} viewers)"
                )
                m3u_file.write('\n')
                m3u_file.write(link)
                m3u_file.write('\n')

except Exception as e:
    logger.error("Erro geral: %s", e)

finally:
    if 'driver' in locals():
        driver.quit()
