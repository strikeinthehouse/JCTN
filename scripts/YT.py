import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
import re

# Configurações do navegador Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)

# URL da página desejada (YouTube com resultados de busca)
url_youtube = "https://www.youtube.com/results?search_query=zadruga&sp=CAMSAkAB"

# Abrir a página no navegador
driver.get(url_youtube)

# Esperar a página carregar
time.sleep(5)

# Definir o diretório pai
parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))

# Gerar o arquivo .m3u no diretório pai
m3u_filename = os.path.join(parent_directory, "TWITCH.m3u")

# Abrir o arquivo para escrita
with open(m3u_filename, 'w') as m3u_file:
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
                    
                    # Extrair o ID do canal da URL
                    match = re.search(r"youtube\.com/(?:@([^/]+)|channel/([^/]+))", link_href)
                    if match:
                        channel_id = match.group(1) if match.group(1) else match.group(2)
                        video_url = f"https://ythls.armelin.one/channel/{channel_id}.m3u8"

                        # Extrair o título do vídeo
                        title_element = link_element.find_element(By.XPATH, "ancestor::ytd-video-renderer//yt-formatted-string[@class='style-scope ytd-video-renderer']")
                        video_title = title_element.text if title_element else "Título Desconhecido"
                        
                        # Thumbnail fixa
                        thumbnail_url = "https://i.ytimg.com/vi/FjBntFoMIuc/hqdefault.jpg"
                        
                        # Escrever a linha EXTINF para cada vídeo no arquivo M3U
                        m3u_file.write(f"#EXTINF:-1 tvg-logo=\"{thumbnail_url}\" group-title=\"Reality Show's Live\", {video_title}\n")
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
