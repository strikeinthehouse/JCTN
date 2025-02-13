from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import concurrent.futures

# Configurações do Chrome
options = Options()
options.add_argument("--headless")  # Executa sem interface gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# URLs dos vídeos Globoplay
globoplay_urls = [
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/bom-dia-cidade-ribeirao-preto.ghtml",  # Bom Dia Cidade Ribeirão Preto
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/eptv1.ghtml",  # EPTV 1ª Edição - Ribeirão Preto
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/eptv-2-ribeirao-e-franca-ao-vivo.ghtml",  # EPTV 2ª Edição - Ribeirão e Franca
    "https://g1.globo.com/pe/petrolina-regiao/ao-vivo/ao-vivo-assista-ao-gr2.ghtml",  # GR2 - Petrolina
    "https://g1.globo.com/ap/ao-vivo/assista-ao-bdap-desta-sexta-feira-7.ghtml",  # BDAP - Amapá
    "https://globoplay.globo.com/v/1467373/",  # Globoplay - Transmissão ao vivo
    "https://globoplay.globo.com/v/4064559/",  # G1 ao vivo - Transmissão ao vivo
    "https://g1.globo.com/ba/bahia/ao-vivo/assista-aos-telejornais-da-tv-bahia.ghtml",  # Telejornais da TV Bahia
    "https://g1.globo.com/pe/caruaru-regiao/video/transmissao-ao-vivo-do-abtv-5472979.ghtml",  # ABTV - Caruaru
    "https://globoplay.globo.com/v/5472979/",
    "https://globoplay.globo.com/v/2135579/",  # G1 RS - Telejornais da RBS TV
    "https://globoplay.globo.com/v/6120663/",  # G1 RS - Jornal da EPTV 1ª Edição - Ribeirão Preto
    "https://globoplay.globo.com/v/2145544/",  # G1 SC - Telejornais da NSC TV
    "https://globoplay.globo.com/v/4039160/",  # G1 CE - TV Verdes Mares ao vivo
    "https://globoplay.globo.com/v/6329086/",  # Globo Esporte BA - Travessia Itaparica-Salvador ao vivo
    "https://globoplay.globo.com/v/11999480/",  # G1 ES - Jornal Regional ao vivo
    "https://g1.globo.com/al/alagoas/ao-vivo/assista-aos-telejornais-da-tv-gazeta-de-alagoas.ghtml",  # Telejornais da TV Gazeta de Alagoas
    "https://globoplay.globo.com/ao-vivo/3667427/",  # Globoplay - Transmissão ao vivo
    "https://globoplay.globo.com/v/4218681/",  # G1 Triângulo Mineiro - Transmissão ao vivo
    "https://globoplay.globo.com/v/12945385/",  # Globoplay - Transmissão ao vivo
    "https://globoplay.globo.com/v/3065772/",  # G1 MS - Transmissão ao vivo em MS
    "https://globoplay.globo.com/v/2923579/",  # G1 AP - Telejornais da Rede Amazônica
    "https://g1.globo.com/am/amazonas/ao-vivo/assista-aos-telejornais-da-rede-amazonica.ghtml",  # Telejornais da Rede Amazônica - Amazonas
    "https://globoplay.globo.com/v/2923546/",  # G1 AC - Jornais da Rede Amazônica
    "https://globoplay.globo.com/v/2168377/",  # Telejornais da TV Liberal
    "https://globoplay.globo.com/v/992055/",  # G1 ao vivo - Transmissão ao vivo
    "https://globoplay.globo.com/v/602497/",  # ge.globo - Transmissão ao vivo
    "https://globoplay.globo.com/v/8713568/",  # Globo Esporte RS - Gauchão ao vivo
    "https://globoplay.globo.com/v/10747444/",  # CBN SP - Transmissão ao vivo
    "https://globoplay.globo.com/v/10740500/",  # CBN RJ - Transmissão ao vivo
]

def extract_globoplay_data(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    try:
        play_button = driver.find_element(By.CSS_SELECTOR, "button.poster__play-wrapper")
        if play_button:
            play_button.click()
            time.sleep(15)
    except Exception as e:
        print("Erro ao clicar no botão de reprodução:", e)

    time.sleep(50)  # Espera a página carregar
    title = driver.title
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    m3u8_url = None
    thumbnail_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name'] and not thumbnail_url:
            thumbnail_url = entry['name']
    driver.quit()
    return title, m3u8_url, thumbnail_url

with open("lista1.m3u", "w") as output_file:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(extract_globoplay_data, url): url for url in globoplay_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title, m3u8_url, thumbnail_url = future.result()
                if m3u8_url:
                    thumbnail_url = thumbnail_url if thumbnail_url else ""
                    output_file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="GLOBO AO VIVO", {title}\n')
                    output_file.write(f"{m3u8_url}\n")
                    print(f"Processado com sucesso: {url}")
                else:
                    print(f"M3U8 não encontrado para {url}")
            except Exception as e:
                print(f"Erro ao processar {url}: {e}")
                





             
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome options
options = Options()
options.add_argument("--headless")  # Uncomment if you don't need a GUI
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Create the webdriver instance
driver = webdriver.Chrome(options=options)

# New base URL
base_url = "https://duckduckgo.com/?q=+vivo+site%3Aglobo.com&t=h_&iar=videos&iax=videos&ia=videos"

# Load the page
driver.get(base_url)

# Wait until the video links are present
try:
    # Wait for the video links to load
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tile.tile--vid')))

    # Extract video links and titles
    video_elements = driver.find_elements(By.CSS_SELECTOR, 'div.tile.tile--vid')
    video_links = [video.get_attribute('data-link') for video in video_elements]
    video_titles = [video.find_element(By.CSS_SELECTOR, 'h6.tile__title').text for video in video_elements]

    # Print the links found
    if video_links:
        print("Links encontrados:")
        for title, link in zip(video_titles, video_links):
            print(f"Title: {title}, Link: {link}")
        
        # Write the links and titles to a file
        with open("links_video.txt", "w") as file:
            for title, link in zip(video_titles, video_links):
                file.write(f"{title}\n{link}\n")
    else:
        print("Nenhum link encontrado.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")


# Function to extract m3u8 URL and title from a video page
def extract_m3u8_url_and_title(driver, url):
    driver.get(url)
    time.sleep(10)  # Wait for the page to fully load
    
    # Get the page title
    title = driver.title

    # Get the m3u8 link
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")

    m3u8_url = None
    logo_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name']:
            logo_url = entry['name']

    return title, m3u8_url, logo_url


# Create the webdriver instance
driver = webdriver.Chrome(options=options)

# Open the file containing the video links
with open("links_video.txt", "r") as file:
    lines = file.readlines()

# Create or append to the m3u file
with open("lista1.m3u", "a") as output_file:
    for i in range(0, len(lines), 2):  # Video title and link are stored in pairs
        title = lines[i].strip()
        link = lines[i+1].strip()

        if not link:
            continue

        print(f"Processando link: {link}")

        try:
            title, m3u8_url, logo_url = extract_m3u8_url_and_title(driver, link)

            if m3u8_url:
                # Write in IPTV format
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="VOD IT", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"M3U8 link encontrado: {m3u8_url}")
            else:
                print(f"Link .m3u8 não encontrado para {link}")

        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")
