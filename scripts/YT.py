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

# URL da pesquisa no YouTube
url_youtube = "https://www.youtube.com/results?search_query=zadruga&sp=CAMSAkAB"

# Abrir a página de resultados no navegador
driver.get(url_youtube)

# Esperar a página carregar
time.sleep(5)

# Capturar os dados dos canais
channels_info = []

try:
    # Encontrar os elementos que contêm informações sobre os canais ao vivo
    channel_elements = driver.find_elements(By.XPATH, "//ytd-channel-renderer//a[@id='channel-info']")
    
    for element in channel_elements:
        channel_url = element.get_attribute("href")  # URL do canal
        if channel_url:
            # Extrair o nome do canal (se disponível) e a URL da miniatura
            channel_name = element.get_attribute("aria-label") or element.text.strip()
            thumbnail_url = element.find_element(By.XPATH, "..//yt-image").get_attribute("src")
            
            # Adicionar as informações do canal à lista
            channels_info.append({
                'name': channel_name,
                'country': 'CHILE',  # País fixo, mas você pode adicionar lógica para extrair o país se necessário
                'thumbnail': thumbnail_url,
                'url': channel_url
            })
    
    # Procurar pelo vídeo ao vivo, caso exista
    video_elements = driver.find_elements(By.XPATH, "//ytd-video-renderer//a[@id='thumbnail']")
    
    if len(video_elements) > 0:
        live_video_url = video_elements[0].get_attribute("href")  # Pega o primeiro vídeo encontrado
    else:
        live_video_url = "https://www.youtube.com/watch?v=default_video"  # Fallback caso não encontre

except Exception as e:
    print(f"Erro ao capturar dados: {e}")
    channels_info = []
    live_video_url = "https://www.youtube.com/watch?v=default_video"

# Gerar o arquivo channel_yt.txt com os dados extraídos
txt_filename = "channel_yt.txt"
with open(txt_filename, 'w') as txt_file:
    # Escrever os dados dos canais ao vivo no arquivo
    for channel in channels_info:
        txt_file.write(f"{channel['name']} | {channel['country']} | {channel['thumbnail']} | {channel['url']}\n")
    
    # Adicionar o link do vídeo ao vivo encontrado
    txt_file.write(f"Unknown | CHILE | https://www.example.com/default-thumbnail.jpg | {live_video_url}\n")

# Fechar o navegador
driver.quit()

print(f"Arquivo {txt_filename} gerado com sucesso.")
