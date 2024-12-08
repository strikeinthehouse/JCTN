import os
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By

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

# Capturar os links dos vídeos
videos = []
try:
    # Alterado o XPath para capturar corretamente os links dos vídeos do YouTube
    link_elements = driver.find_elements(By.XPATH, "//a[@href and contains(@href, '/watch?v=')]")
    if link_elements:
        for link_element in link_elements:
            link_href = link_element.get_attribute("href")
            if link_href and 'watch' in link_href:
                videos.append(link_href)
    else:
        print("Elementos de link não encontrados")
except Exception as e:
    print(f"Erro ao capturar vídeos: {e}")

# Gerar o arquivo M3U na pasta anterior ao diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório do script
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))  # Diretório pai

m3u_filename = os.path.join(parent_dir, "TWITCH.m3u")

# Abrir o arquivo M3U para escrita
with open(m3u_filename, 'w') as m3u_file:
    # Escrever o cabeçalho do arquivo M3U
    m3u_file.write("#EXTM3U\n")
    
    for video_url in videos:
        try:
            # Extrair informações do vídeo usando yt-dlp
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,  # Não baixar o vídeo, apenas extrair informações
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                if 'channel' in info_dict:
                    channel_id = info_dict['channel_id']
                    stream_url = f"https://ythls.armelin.one/channel/{channel_id}.m3u8"
                    title = info_dict.get('title', 'Título do vídeo')
                    thumbnail_url = info_dict.get('thumbnail', 'https://i.ytimg.com/vi/FjBntFoMIuc/hqdefault.jpg')  # Thumbnail do vídeo
                else:
                    # URL de fallback para vídeos que não possuem canal identificado
                    stream_url = f"https://ythlsgo.onrender.com/channel/{info_dict['id']}.m3u8"
                    title = "Vídeo sem canal identificado"
                    thumbnail_url = 'https://i.ytimg.com/vi/FjBntFoMIuc/hqdefault.jpg'  # Thumbnail fixa

                # Escrever a linha EXTINF no arquivo M3U
                m3u_file.write(f"#EXTINF:-1 tvg-logo=\"{thumbnail_url}\" group-title=\"Live\", {title}\n")
                m3u_file.write(f"{stream_url}\n")

        except Exception as e:
            print(f"Erro ao processar o vídeo {video_url}: {e}")

# Fechar o navegador após o processo
driver.quit()

print(f"Arquivo {m3u_filename} gerado com sucesso.")
