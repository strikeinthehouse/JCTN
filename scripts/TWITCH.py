import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configurações do navegador Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executa sem abrir o navegador
chrome_options.add_argument("--disable-gpu")  # Necessário para o headless funcionar bem

# Inicializa o driver do Chrome
driver = webdriver.Chrome(options=chrome_options)

# URL da pesquisa no YouTube (ajuste conforme necessário)
url_youtube = "https://www.youtube.com/results?search_query=zadruga&sp=CAMSAkAB"

# Abrir a página de resultados no navegador
driver.get(url_youtube)

# Esperar a página carregar
time.sleep(5)

# Capturar os dados dos vídeos e canais
videos_info = []

try:
    # Encontrar os elementos de vídeo
    video_elements = driver.find_elements(By.XPATH, "//ytd-video-renderer")

    for video in video_elements:
        # Tentar encontrar o título do vídeo (aria-label)
        title_element = video.find_element(By.XPATH, ".//yt-formatted-string[@class='style-scope ytd-video-renderer']")
        video_title = title_element.get_attribute("aria-label") if title_element else "Desconhecido"
        
        # Tentar encontrar o nome do canal
        channel_element = video.find_element(By.XPATH, ".//a[@class='yt-simple-endpoint style-scope yt-formatted-string']")
        channel_name = channel_element.text.strip() if channel_element else "Desconhecido"
        
        # Tentar encontrar a URL da miniatura
        thumbnail_element = video.find_element(By.XPATH, ".//img[@class='yt-core-image yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded']")
        thumbnail_url = thumbnail_element.get_attribute("src") if thumbnail_element else "https://www.example.com/default-thumbnail.jpg"
        
        # Adicionar as informações coletadas na lista
        videos_info.append({
            'title': video_title,
            'channel': channel_name,
            'thumbnail': thumbnail_url,
            'url': "https://www.youtube.com" + video.find_element(By.XPATH, ".//a[@id='thumbnail']").get_attribute("href")
        })

except Exception as e:
    print(f"Erro ao capturar dados: {e}")
    videos_info = []

# Gerar o arquivo channel_yt.txt com os dados extraídos
txt_filename = "channel_yt.txt"
with open(txt_filename, 'w') as txt_file:
    for video in videos_info:
        txt_file.write(f"{video['title']} | CHILE | {video['thumbnail']} | {video['url']}\n")

# Fechar o navegador
driver.quit()

print(f"Arquivo {txt_filename} gerado com sucesso.")
