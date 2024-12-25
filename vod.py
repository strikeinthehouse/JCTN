from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Configurações do Chrome
options = Options()
options.add_argument("--headless")  # Executa sem interface gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# URLs dos vídeos Globoplay
globoplay_urls = [
    "https://globoplay.globo.com/tv-globo/ao-vivo/6120663/",
    "https://www.rtp.pt/play/direto/rtpdesporto1",
    "https://globoplay.globo.com/v/2145544/",
    "https://globoplay.globo.com/v/6120663/",
    "https://globoplay.globo.com/v/2135579/",
    "https://globoplay.globo.com/v/2168377/",
    "https://globoplay.globo.com/v/2923546/",
    "https://globoplay.globo.com/v/3383021/"
]

# Função para extrair o link m3u8, título e favicon
def extract_globoplay_data(driver, url):
    driver.get(url)
    time.sleep(10)  # Aguarde a página carregar completamente
    
    # Obter o título da página
    title = driver.title

    # Obter o link m3u8 dos recursos de rede
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    m3u8_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
            break

    # Obter o favicon como thumbnail
    try:
        favicon_element = driver.find_element(By.XPATH, "//link[@rel='icon' or @rel='shortcut icon']")
        favicon_url = favicon_element.get_attribute("href")
    except:
        favicon_url = None

    return title, m3u8_url, favicon_url

# Inicializar o WebDriver
driver = webdriver.Chrome(options=options)

# Criar ou abrir o arquivo lista1.m3u para escrever os links e títulos
with open("lista1.M3U", "a") as output_file:
    for link in globoplay_urls:
        print(f"Processando link: {link}")

        try:
            title, m3u8_url, favicon_url = extract_globoplay_data(driver, link)

            if m3u8_url:
                # Escrever no formato extinf iptv
                thumbnail_url = favicon_url if favicon_url else ""  # Se não encontrar o favicon, deixar em branco
                output_file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="GLOBO AO VIVO", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"M3U8 link encontrado: {m3u8_url}")
            else:
                print(f"Link .m3u8 não encontrado para {link}")
        
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Sair do driver
driver.quit()


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome options
options = Options()
options.add_argument("--headless")  # Descomente se você não precisar de uma interface gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Create the webdriver instance
driver = webdriver.Chrome(options=options)

# URL base (substitua com a URL real)
base_url = "https://www.google.com/search?q=puntata&sca_esv=90c55360f106269f&udm=7&tbas=0&tbs=qdr:w,srcf:H4sIAAAAAAAAAKvMLy0pTUrVS87PVStKzCzISazUyyxRy0k0B1G5qSmZicWpJSB2WmJyalJ-fjZYqXZxNlgdADjpIOk_1AAAA&source=lnt&sa=X&ved=2ahUKEwiS7KjwicGKAxUFELkGHcdIOE4QpwV6BAgBEC4&biw=1920&bih=936&dpr=1"

# Load the page
driver.get(base_url)

# Wait until the video links are present
try:
    # Wait for the video links to load
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[jsname="UWckNb"]')))
    
    # Extract links
    video_links = driver.find_elements(By.CSS_SELECTOR, 'a[jsname="UWckNb"]')
    links_list = [link.get_attribute('href') for link in video_links]

    # Print the links found
    if links_list:
        print("Links encontrados:")
        for link in links_list:
            print(link)
        
        # Write the links to the file
        with open("links_video.txt", "w") as file:
            for link in links_list:
                file.write(link + "\n")
    else:
        print("Nenhum link encontrado.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")


# Função para extrair o link m3u8 e o título da página
def extract_m3u8_url_and_title(driver, url):
    driver.get(url)
    time.sleep(10)  # Aguarde a página carregar completamente
    
    # Obter o título da página
    title = driver.title

    # Obter o link m3u8
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")

    m3u8_url = None
    logo_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name']:
            logo_url = entry['name']

    return title, m3u8_url, logo_url

# Criar a instância do webdriver
driver = webdriver.Chrome(options=options)

# Abrir o arquivo links_video.txt e ler os links
with open("links_video.txt", "r") as file:
    links = file.readlines()

# Criar ou abrir o arquivo lista1.m3u para escrever os links e títulos
with open("lista1.M3U", "a") as output_file:
    for link in links:
        link = link.strip()  # Remover espaços em branco e quebras de linha

        if not link:
            continue
        
        print(f"Processando link: {link}")

        try:
            title, m3u8_url, logo_url = extract_m3u8_url_and_title(driver, link)

            if m3u8_url:
                # Escrever no formato extinf iptv
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="VOD TV", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"M3U8 link encontrado: {m3u8_url}")
            else:
                print(f"Link .m3u8 não encontrado para {link}")
        
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Sair do driver
driver.quit()











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
m3u_file_path = os.path.join(os.getcwd(), "pt.txt")

# Criação do arquivo M3U na pasta raiz
write_m3u_file(links, m3u_file_path)

print(f"Arquivo M3U foi criado: {m3u_file_path}")



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
                file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="VOD",{title}\n')
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
