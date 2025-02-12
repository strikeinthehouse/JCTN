from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

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


# Função para extrair o link m3u8, título e thumbnail
def extract_globoplay_data(driver, url):
    driver.get(url)

    try:
        # Verifica se o botão de reprodução <button class="poster__play-wrapper"> está presente
        play_button = driver.find_element(By.CSS_SELECTOR, "button.poster__play-wrapper")
        
        if play_button:
            # Clica no botão de reprodução se ele existir
            play_button.click()
            time.sleep(15)  # Espera após o clique para a nova página carregar ou ação ser executada
            print("Clique realizado no botão de reprodução.")
    
    except Exception as e:
        print("Erro ao tentar clicar no botão de reprodução:", e)



    time.sleep(45)  # Aguarde a página carregar completamente após a ação de clique
    
    # Obter o título da página
    title = driver.title

    # Obter o link m3u8 dos recursos de rede
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    m3u8_url = None
    thumbnail_url = None

    # Buscar o link m3u8 e o primeiro arquivo .jpg nos recursos de rede
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name'] and not thumbnail_url:  # Pega o primeiro arquivo .jpg
            thumbnail_url = entry['name']

    return title, m3u8_url, thumbnail_url


# Inicializar o WebDriver
driver = webdriver.Chrome(options=options)

# Criar ou abrir o arquivo lista1.m3u para escrever os links e títulos
with open("lista1.m3u", "w") as output_file:
    for link in globoplay_urls:
        print(f"Processando link: {link}")

        try:
            title, m3u8_url, thumbnail_url = extract_globoplay_data(driver, link)

            if m3u8_url:
                # Escrever no formato extinf iptv
                thumbnail_url = thumbnail_url if thumbnail_url else ""  # Se não encontrar a imagem, deixar em branco
                output_file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="GLOBO AO VIVO", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"M3U8 link encontrado: {m3u8_url}")
            else:
                print(f"Link .m3u8 não encontrado para {link}")
        
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Sair do driver
driver.quit()



import os
import shutil
import subprocess

# Caminho a ser deletado
delete_path = "/assets"
if os.path.exists(delete_path):
    shutil.rmtree(delete_path, ignore_errors=True)

# Definição do caminho de saída e nome do arquivo
output_path = "."  # Define o diretório atual
file_name = "TWITCH.m3u"

# Criar diretório, se necessário
os.makedirs(output_path, exist_ok=True)

# Configuração de modo e ID do Google Drive
mode = "file"  # "file" para um único arquivo, "folder" para pasta inteira
id_link = "1CoeZEj20zmtuQPqkCzv2UQq7SsDSlTyd"  # ID do Google Drive

# Construção do comando gdown
if mode == "file":
    command = ["gdown", "--remaining-ok", id_link, "-O", os.path.join(output_path, file_name)]
else:
    command = ["gdown", "--folder", "--remaining-ok", id_link]

# Executar o comando de forma segura
subprocess.run(command, check=True)

print("Download concluído com sucesso!")


import os
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
from bs4 import BeautifulSoup

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_file = "log.txt"
file_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Cabeçalho do arquivo M3U
banner = "#EXTM3U\n"

# Função para verificar URLs via requisição HTTP com o agente de usuário do Firefox
def check_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Firefox/89.0"
    }
    try:
        response = requests.head(url, headers=headers, timeout=15)  # Usando HEAD para verificar a URL rapidamente
        if response.status_code == 200:
            logger.info("URL OK: %s", url)
            return True
        else:
            logger.warning("URL Error %s: Status Code %d", url, response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        logger.error("Request Error %s: %s", url, str(e))
        return False

# Função para processar uma linha #EXTINF
def parse_extinf_line(line):
    group_title = "Undefined"
    tvg_id = "Undefined"
    tvg_logo = "Undefined.png"
    ch_name = "Undefined"
    
    if 'group-title="' in line:
        group_title = line.split('group-title="')[1].split('"')[0]
    if 'tvg-id="' in line:
        tvg_id = line.split('tvg-id="')[1].split('"')[0]
    if 'tvg-logo="' in line:
        tvg_logo = line.split('tvg-logo="')[1].split('"')[0]
    if ',' in line:
        ch_name = line.split(',')[-1].strip()
    
    return ch_name, group_title, tvg_id, tvg_logo

# Função principal para processar o arquivo de entrada
def process_m3u_file(input_url, output_file):
    # Baixa o conteúdo do arquivo M3U diretamente da URL fornecida
    response = requests.get(input_url)
    
    if response.status_code != 200:
        logger.error("Failed to fetch the M3U file from URL: %s", input_url)
        return
    
    lines = response.text.splitlines()

    channel_data = []
    i = 0
    with open(output_file, "a") as f:
        f.write(banner)  # Adiciona o cabeçalho no arquivo M3U

        while i < len(lines):
            line = lines[i].strip()
            
            # Escreve as linhas com #EXTM3U url-tvg= diretamente no arquivo
            if line.startswith('#EXTM3U'):
                f.write(line + '\n')
                i += 1  # Avança para a próxima linha e continua o loop
                continue
            
            if line.startswith('#EXTINF'):
                ch_name, group_title, tvg_id, tvg_logo = parse_extinf_line(line)
                extra_lines = []
                link = None
                
                # Procura pela URL e ignora linhas intermediárias (#EXTVLCOPT, #KODIPROP, etc.)
                while i + 1 < len(lines):
                    i += 1
                    next_line = lines[i].strip()
                    if next_line.startswith('#'):  # Verifica se a linha começa com '#'
                        extra_lines.append(next_line)  # Armazena a linha extra
                    else:
                        link = next_line  # Caso contrário, é a URL do canal
                        break
                
                # Verifica a URL antes de adicionar
                if link and check_url(link):
                    # Se o canal não tiver logotipo, buscar o logo automaticamente
                    if tvg_logo in ["", "N/A", "Undefined.png"]:  # Condição para logo vazio ou "N/A"
                        logo_url = search_google_images(ch_name)
                        if logo_url:
                            tvg_logo = logo_url
                        else:
                            tvg_logo = "NoLogoFound.png"  # Caso não encontre logo
                    
                    # Escreve a linha EXTINF e a URL do canal
                    extinf_line = (
                        f'#EXTINF:-1 group-title="{group_title}" '
                        f'tvg-id="{tvg_id}" '
                        f'tvg-logo="{tvg_logo}",{ch_name}'
                    )
                    f.write(extinf_line + '\n')
                    for extra in extra_lines:
                        f.write(extra + '\n')
                    f.write(link + '\n')
            
            i += 1  # Avança para a próxima linha

    # Salva os dados em JSON para análise posterior
    with open("playlist.json", "a") as f:
        json.dump(channel_data, f, indent=2)

# Função para buscar imagem no Google
def search_google_images(query):
    search_url = f"https://www.google.com/search?hl=pt-BR&q={query}&tbm=isch"  # URL de busca de imagens
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # Buscar a primeira imagem
        img_tags = soup.find_all("img")
        if img_tags:
            # A primeira imagem no Google geralmente é a mais relevante
            img_url = img_tags[1]['src']  # O primeiro item é o logo do Google
            return img_url
    except Exception as e:
        logger.error("Error searching Google images: %s", e)
    
    return None

# URL do arquivo M3U hospedado no GitHub
input_url = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/TWITCH.txt"
output_file = "TWITCH.m3u"

# Executa o processamento
process_m3u_file(input_url, output_file)
