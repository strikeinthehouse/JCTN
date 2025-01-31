import os
import time
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configurações do navegador Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)

# URL da página desejada (YouTube com resultados de busca)
url_youtube = "https://www.youtube.com/results?search_query=2º+Temporada+Reality+do+Sul+Ao+Vivo"

# Abrir a página no navegador
driver.get(url_youtube)

# Esperar a página carregar
time.sleep(5)

# Definir o diretório pai
parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))

# Gerar o arquivo .m3u no diretório pai
m3u_filename = os.path.join(parent_directory, "TWITCH.m3u")

# Abrir o arquivo para escrita
with open(m3u_filename, 'a') as m3u_file:
    # Escrever o cabeçalho do arquivo M3U
    m3u_file.write("#EXTM3U\n")

    # Conjunto para armazenar links já processados (evitar duplicação)
    processed_links = set()

    try:
        # Capturar os links dos vídeos
        link_elements = driver.find_elements(By.XPATH, "//a[@class='yt-simple-endpoint style-scope yt-formatted-string']")

        if link_elements:
            # Iterar sobre os links de vídeo encontrados
            for link_element in link_elements:
                link_href = link_element.get_attribute("href")
                if link_href and link_href not in processed_links:  # Verifica se o link já foi processado
                    processed_links.add(link_href)  # Adiciona o link ao conjunto

                    # Usar yt-dlp para extrair informações sobre o vídeo
                    ydl_opts = {
                        'quiet': True,
                        'force_generic_extractor': True,
                        'extract_flat': True,
                        'dump_single_json': True
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(link_href, download=False)
                        if 'channel_id' in info_dict:
                            channel_id = info_dict['channel_id']
                            video_url = f"https://ythls-v3.onrender.com/channel/{channel_id}.m3u8"

                            # Extrair o título do vídeo
                            title_element = link_element.find_element(By.XPATH, "ancestor::ytd-video-renderer//yt-formatted-string[@class='style-scope ytd-video-renderer']")
                            video_title = title_element.text if title_element else "Título Desconhecido"
                            
                            # Extrair a URL da thumbnail do vídeo
                            thumbnail_element = link_element.find_element(By.XPATH, "ancestor::ytd-video-renderer//img[contains(@class, 'yt-core-image--fill-parent-height')]")
                            thumbnail_url = thumbnail_element.get_attribute("src") if thumbnail_element else "https://yt3.googleusercontent.com/u6H_TO65Atxmpc98XR-HcMFZ16o1UVppXqO7gj4hMUfz6H6YHjXZh4rLGTkyMHXNmeOfRFa0=s900-c-k-c0x00ffffff-no-rj"
                            
                            # Escrever a linha EXTINF para cada vídeo no arquivo M3U
                            m3u_file.write(f"#EXTINF:-1 group-title=\"Reality Show's Live\" tvg-logo=\"{thumbnail_url}\" tvg-id=\"Zadruga live 1.rs\" ,{video_title}\n")
                            m3u_file.write(f"{video_url}\n")
                            print(f"Adicionado vídeo: {video_title} ({video_url})")
                        else:
                            print("ID do canal não encontrado para o link:", link_href)
        else:
            print("Elementos de link não encontrados")
    except Exception as e:
        print(f"Erro: {e}")

# Fechar o navegador após o processo
driver.quit()
