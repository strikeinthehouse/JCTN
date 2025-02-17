from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurações do Chrome
options = Options()
options.add_argument("--headless")  # Executa o navegador em modo headless
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Cria a instância do webdriver
driver = webdriver.Chrome(options=options)

# URL base para pesquisa
base_url = "https://duckduckgo.com/?q=assista+ao+site%3Aglobo.com&t=h_&iar=videos&start=1&iax=videos&ia=videos"

try:
    driver.get(base_url)

    # Espera até que os elementos de vídeo carreguem
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tile--vid"))
    )

    video_elements = driver.find_elements(By.CSS_SELECTOR, "div.tile--vid")
    video_links = []
    video_titles = []

    for video in video_elements:
        try:
            link_element = video.find_element(By.CSS_SELECTOR, "h6.tile__title a")
            link = link_element.get_attribute("href")
            title = link_element.text
            video_links.append((title, link))
        except Exception as e:
            print(f"Erro ao extrair informações do vídeo: {e}")

    if video_links:
        print("Links encontrados:")
        with open("links_video.txt", "w", encoding="utf-8") as file:
            for title, link in video_links:
                print(f"Título: {title}, Link: {link}")
                file.write(f"{title}\n{link}\n")
    else:
        print("Nenhum link encontrado.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")

# Função para extrair URL m3u8 e título da página do vídeo
def extract_m3u8_url_and_title(driver, url):
    driver.get(url)
    time.sleep(10)  # Aguarda o carregamento completo da página

    # Obtém o título da página
    title = driver.title
    try:
        # Aguarda o botão de reprodução estar clicável
        play_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.poster__play-wrapper"))
        )
        play_button.click()  # Clica no botão de reprodução
        time.sleep(15)  # Aguarda o início da reprodução do vídeo
    except Exception as e:
        print("Erro ao clicar no botão de reprodução:", e)

    # Obtém o link m3u8
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    m3u8_url = None
    logo_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name']:
            logo_url = entry['name']

    return title, m3u8_url, logo_url

# Abre o arquivo contendo os links dos vídeos
with open("links_video.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Cria ou adiciona ao arquivo m3u
with open("lista1.m3u", "a", encoding="utf-8") as output_file:
    output_file.write("#EXTM3U\n")  # Cabeçalho do arquivo m3u
    for i in range(0, len(lines), 2):  # Título e link são armazenados em pares
        title = lines[i].strip()
        link = lines[i + 1].strip()

        if not link:
            continue

        print(f"Processando link: {link}")

        try:
            title, m3u8_url, logo_url = extract_m3u8_url_and_title(driver, link)
            if m3u8_url:
                # Escreve no formato IPTV
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="GLOBO AO VIVO", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"Link M3U8 encontrado: {m3u8_url}")
            else:
                print(f"Link .m3u8 não encontrado para {link}")
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Encerra o driver após a conclusão
driver.quit()
