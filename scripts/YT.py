import os
import time
import re
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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

# Função para rolar para baixo e carregar mais vídeos
def scroll_to_load_more_videos():
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3)  # Espera os vídeos carregarem
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:  # Se não houver mais vídeos para carregar
            break
        last_height = new_height

# Rolando a página para carregar mais vídeos
scroll_to_load_more_videos()

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
                    
                    # Usar yt-dlp para extrair a ID do canal
                    try:
                        result = subprocess.run(
                            ['yt-dlp', '--get-id', link_href],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        # O comando yt-dlp vai retornar o ID do canal ou erro
                        channel_id = result.stdout.strip()
                        
                        if channel_id:
                            # Extrair o título do vídeo
                            title_element = link_element.find_element(By.XPATH, "ancestor::ytd-video-renderer//yt-formatted-string[@class='style-scope ytd-video-renderer']")
                            video_title = title_element.text if title_element else "Título Desconhecido"
                            
                            # Thumbnail fixa
                            thumbnail_url = "https://i.ytimg.com/vi/FjBntFoMIuc/hqdefault.jpg"
                            
                            # Gerar a URL do canal com o ID extraído
                            video_url = f"https://ythls.armelin.one/channel/{channel_id}.m3u8"

                            # Escrever a linha EXTINF para cada vídeo no arquivo M3U
                            m3u_file.write(f"#EXTINF:-1 tvg-logo=\"{thumbnail_url}\" group-title=\"Live\", {video_title}\n")
                            m3u_file.write(f"{video_url}\n")
                            print(f"Adicionado vídeo: {video_title} ({video_url})")
                        else:
                            print(f"Não foi possível extrair o ID do canal para o vídeo {link_href}.")
                    except Exception as e:
                        print(f"Erro ao extrair o ID do canal para o vídeo {link_href}: {e}")
        else:
            print("Elementos de link não encontrados")
    except Exception as e:
        print(f"Erro: {e}")

# Fechar o navegador após o processo
driver.quit()

print(f"Arquivo {m3u_filename} gerado com sucesso.")
