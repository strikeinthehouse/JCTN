from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome options
options = Options()
options.add_argument("--headless")  # Descomente se não precisar de interface gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Create the webdriver instance
driver = webdriver.Chrome(options=options)

# URL base (Google)
base_url = "https://www.google.com/search?q=tvi&sca_esv=78aae0fabe89f8a8&udm=7&tbs=srcf:H4sIAAAAAAAAANPOzM_1RKyhRq8wvLSlNStVLzs9VS0tMTk3Kz88Gc0oys0ugzMy84pLE9KLEXDAvPSc_1KR_1MAgCXPf-TRAAAAA,dur:l&source=lnt&sa=X&ved=2ahUKEwiOpPKFk-WMAxUeLLkGHXbWNvUQpwV6BAgDEA4&biw=1912&bih=1000&dpr=1#ip=1"

# Load the page
driver.get(base_url)

# Wait until the links are present
try:
    # Esperar até os links de transmissão estarem presentes
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[jsname="UWckNb"]')))

    # Extrair os links de transmissão ao vivo
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
    time.sleep(56)  # Espera a página carregar

    # Obter o título da página
    title = driver.title

    # Obter o link m3u8 (se presente)
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")

    m3u8_url = None
    logo_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name']:
            logo_url = entry['name']

    return title, m3u8_url, logo_url

# Criar ou abrir o arquivo lista1.m3u para escrever os links e títulos
with open("links_video.txt", "r") as file:
    links = file.readlines()

# Criar ou abrir o arquivo lista1.m3u para escrever os dados
with open("lista1.m3u", "w") as output_file:
    for link in links:
        link = link.strip()  # Remover espaços em branco e quebras de linha

        if not link:
            continue

        print(f"Processando link: {link}")

        try:
            # Extrair título, URL do m3u8 e logo
            title, m3u8_url, logo_url = extract_m3u8_url_and_title(driver, link)

            if m3u8_url:
                # Escrever no formato extinf iptv
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="VOD GLOBO", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"M3U8 link encontrado: {m3u8_url}")
            else:
                print(f"Link .m3u8 não encontrado para {link}")

        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Sair do driver
driver.quit()
