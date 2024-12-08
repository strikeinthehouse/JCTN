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
            # Construir o link final para o vídeo
            video_url = "https://www.youtube.com" + link_href
            print(f"Link do vídeo: {video_url}")
            
            # Tentar capturar a thumbnail do vídeo
            try:
                thumbnail_url = second_link_element.find_element(By.XPATH, "..//yt-image").get_attribute("src")
                print(f"Thumbnail: {thumbnail_url}")
            except Exception as e:
                print(f"Erro ao capturar a thumbnail: {e}")
                thumbnail_url = "https://www.example.com/default-thumbnail.jpg"  # Thumbnail padrão, caso falhe

            # Capturar informações do canal
            try:
                channel_url = second_link_element.find_element(By.XPATH, "..//ytd-channel-name/a").get_attribute("href")
                channel_thumbnail_url = second_link_element.find_element(By.XPATH, "..//ytd-channel-name//yt-img-shadow/img").get_attribute("src")
                channel_name = second_link_element.find_element(By.XPATH, "..//ytd-channel-name//yt-formatted-string").text
                print(f"Canal: {channel_name}, URL do Canal: {channel_url}, Thumbnail do Canal: {channel_thumbnail_url}")
            except Exception as e:
                print(f"Erro ao capturar as informações do canal: {e}")
                channel_name = "Unknown"
                channel_url = "https://www.youtube.com/channel/Unknown"
                channel_thumbnail_url = "https://www.example.com/default-channel-thumbnail.jpg"

        else:
            print("Link href não encontrado")
            video_url = "https://www.youtube.com/watch?v=_9Grp5tYrYI"  # Fallback para um vídeo padrão
            thumbnail_url = "https://www.example.com/default-thumbnail.jpg"  # Thumbnail padrão
            channel_name = "Unknown"
            channel_url = "https://www.youtube.com/channel/Unknown"
            channel_thumbnail_url = "https://www.example.com/default-channel-thumbnail.jpg"
    else:
        print("Elementos de link não encontrados")
        video_url = "https://www.youtube.com/watch?v=_9Grp5tYrYI"  # Fallback para um vídeo padrão
        thumbnail_url = "https://www.example.com/default-thumbnail.jpg"  # Thumbnail padrão
        channel_name = "Unknown"
        channel_url = "https://www.youtube.com/channel/Unknown"
        channel_thumbnail_url = "https://www.example.com/default-channel-thumbnail.jpg"

except Exception as e:
    print(f"Erro: {e}")
    video_url = "https://www.youtube.com/watch?v=_9Grp5tYrYI"  # Fallback para um vídeo padrão
    thumbnail_url = "https://www.example.com/default-thumbnail.jpg"  # Thumbnail padrão
    channel_name = "Unknown"
    channel_url = "https://www.youtube.com/channel/Unknown"
    channel_thumbnail_url = "https://www.example.com/default-channel-thumbnail.jpg"

# Gerar o arquivo channel_yt.txt
txt_filename = "channel_yt.txt"
with open(txt_filename, 'w') as txt_file:
    # Escrever no arquivo .txt no formato desejado
    txt_file.write(f"{channel_name} | CHILE | {channel_thumbnail_url} | {channel_url}/live\n")
    txt_file.write(f"{channel_name} | CHILE | {channel_thumbnail_url} | {video_url}\n")

# Fechar o navegador após o processo
driver.quit()

print(f"Arquivo {txt_filename} gerado com sucesso.")
