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
    "https://www.earthcam.com/usa/newyork/timessquare/?cam=tsrobo1",
    "https://globoplay.globo.com/v/6120663/",
    "https://globoplay.globo.com/v/2135579/",
    "https://globoplay.globo.com/v/2168377/",
    "https://globoplay.globo.com/v/2923546/",
    "https://globoplay.globo.com/v/3383021/",
    "https://cbn.globo.com/ao-vivo/video/cbn-sp/",
    "https://cbn.globo.com/ao-vivo/video/cbn-rj/"
]

# Função para extrair o link m3u8, título e favicon
def extract_globoplay_data(driver, url):
    driver.get(url)
    time.sleep(25)  # Aguarde a página carregar completamente
    
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
with open("lista1.m3u", "w") as output_file:
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
