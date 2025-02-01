# Bibliotecas necessárias
import os
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do Selenium WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

driver = webdriver.Chrome(options=options)

# URL da playlist do YouTube
url_playlist = "https://www.youtube.com/watch?v=ToSWxxvXFN0&list=PL3ZQ5CpNulQmA2Tegc98c0XXJTzuKb0wS"
driver.get(url_playlist)

# Esperar a página carregar completamente
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'watch?v=')]"))
    )
except Exception as e:
    print(f"Erro ao esperar os vídeos carregarem: {e}")
    driver.quit()
    exit()

# Definir o diretório onde o arquivo .m3u será salvo
parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))
m3u_filename = os.path.join(parent_directory, "TWITCH.m3u")

# Abrir o arquivo para escrita
with open(m3u_filename, 'a') as m3u_file:
    m3u_file.write("#EXTM3U\n")
    processed_links = set()

    try:
        # Capturar os links dos vídeos na playlist
        link_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'watch?v=')]")

        if link_elements:
            for link_element in link_elements:
                link_href = link_element.get_attribute("href")
                if link_href and link_href not in processed_links:
                    processed_links.add(link_href)

                    # Configuração do yt-dlp para capturar informações dos vídeos
                    ydl_opts = {
                        'quiet': True,
                        'extract_flat': False,
                        'format': 'best',
                        'writeinfojson': True,
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        try:
                            info_dict = ydl.extract_info(link_href, download=False)
                            # Print do info_dict para depuração
                            print(info_dict)

                            # Pegar o título diretamente com Selenium (caso não tenha sido extraído com yt-dlp)
                            title_element = link_element.find_element(By.XPATH, ".//ancestor::ytd-video-renderer//a[@id='video-title']")
                            video_title = title_element.text if title_element else "Título Desconhecido"

                            # Pegar a URL da thumbnail
                            thumbnail_element = link_element.find_element(By.XPATH, ".//ancestor::ytd-video-renderer//img[contains(@class, 'yt-core-image--fill-parent-height')]")
                            thumbnail_url = thumbnail_element.get_attribute("src") if thumbnail_element else "https://yt3.googleusercontent.com/u6H_TO65Atxmpc98XR-HcMFZ16o1UVppXqO7gj4hMUfz6H6YHjXZh4rLGTkyMHXNmeOfRFa0=s900-c-k-c0x00ffffff-no-rj"

                            # Escrever no arquivo M3U
                            video_url = f"https://ythls-v3.onrender.com/channel/{info_dict['id']}.m3u8"  # Supondo que info_dict tenha um id
                            m3u_file.write(f"#EXTINF:-1 group-title=\"Reality Show's Live\" tvg-logo=\"{thumbnail_url}\" ,{video_title}\n")
                            m3u_file.write(f"{video_url}\n")
                            print(f"Adicionado vídeo: {video_title} ({video_url})")

                        except Exception as e:
                            print(f"Erro ao processar o vídeo {link_href}: {e}")
        else:
            print("Elementos de link não encontrados")
    except Exception as e:
        print(f"Erro: {e}")

# Fechar o navegador após o processo
driver.quit()
