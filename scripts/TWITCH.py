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
id_link = "1KStqu5F3_xFAlt3viag95FsJVP4HSo7o"  # ID do Google Drive

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
