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
with open("lista1.M3U", "w") as output_file:
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
















