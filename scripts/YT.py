import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

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
try:
    link_elements = driver.find_elements(By.XPATH, "//a[@class='yt-simple-endpoint style-scope yt-formatted-string']")
    if link_elements:
        # Pegar o segundo vídeo da lista de resultados
        second_link_element = link_elements[1]
        link_href = second_link_element.get_attribute("href")
        if link_href:
            # Construir o link final para o vídeo ao vivo
            video_url = "https://www.youtube.com" + link_href
            print(f"Link do vídeo: {video_url}")
            
            # Capturar a thumbnail do vídeo
            thumbnail_url = second_link_element.find_element(By.XPATH, "..//yt-image").get_attribute("src")
            print(f"Thumbnail: {thumbnail_url}")
        else:
            print("Link href não encontrado")
    else:
        print("Elementos de link não encontrados")

except Exception as e:
    print(f"Erro: {e}")
    video_url = "https://www.youtube.com/watch?v=_9Grp5tYrYI"
    print(f"Link de fallback: {video_url}")

# Gerar o arquivo .m3u
m3u_filename = "TWITCH.m3u"
with open(m3u_filename, 'w') as m3u_file:
    # Escrever o cabeçalho do arquivo M3U
    m3u_file.write("#EXTM3U\n")
    
    # Linha EXTINF com título do vídeo, thumbnail e URL do vídeo
    title = "Elita uzivo [HD] Experiment X"  # Você pode ajustar isso para pegar o título real do vídeo
    thumbnail = thumbnail_url  # Thumbnail capturada
    stream_url = video_url  # URL do vídeo

    # Escrever a linha EXTINF no arquivo M3U
    m3u_file.write(f"#EXTINF:-1 tvg-logo=\"{thumbnail}\" group-title=\"Live\", {title}\n")
    m3u_file.write(f"{stream_url}\n")

# Fechar o navegador após o processo
driver.quit()

print(f"Arquivo {m3u_filename} gerado com sucesso.")
