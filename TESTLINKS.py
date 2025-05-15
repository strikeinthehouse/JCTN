####


import requests
import logging
from logging.handlers import RotatingFileHandler
import json
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_file = "log.txt"
file_handler = RotatingFileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# URL do arquivo .txt
CHANNEL_FILE_URL = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/TWITCH.m3u"

# Funções utilitárias
def download_channel_file(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text.splitlines()  # Retorna o conteúdo do arquivo como uma lista de linhas
    except requests.exceptions.RequestException as err:
        logger.error("Erro ao baixar o arquivo: %s", err)
        sys.exit("Erro ao baixar o arquivo .txt")

def extract_youtube_id(url):
    """Extrai o ID do canal do YouTube ou do vídeo a partir da URL."""
    # Para URLs do tipo "/channel/<ID>"
    channel_match = re.search(r"youtube\.com/channel/([a-zA-Z0-9_-]+)", url)
    if channel_match:
        return channel_match.group(1)
    
    # Para URLs do tipo "/watch?v=<ID>" ou "/live/<ID>"
    video_match = re.search(r"(?:youtube\.com/watch\?v=|youtube\.com/live/|youtube\.com/live/\S+)[a-zA-Z0-9_-]+", url)
    if video_match:
        return video_match.group(1)
    
    logger.warning("ID não encontrado para URL: %s", url)
    return None

# Baixa e processa o arquivo de canais
lines = download_channel_file(CHANNEL_FILE_URL)

channel_data = []
channel_data_json = []

banner = r'''
#EXTM3U
###########################################################################
#EXTM3U url-tvg="https://www.bevy.be/bevyfiles/argentina.xml"
'''

# Processa as linhas do arquivo
for line in lines:
    line = line.strip()
    if not line or line.startswith('~~'):
        continue
    if not line.startswith('http') and len(line.split("|")) == 4:
        line = line.split('|')
        ch_name = line[0].strip()
        grp_title = line[1].strip().title()
        tvg_logo = line[2].strip()
        tvg_id = None
        channel_data.append({
            'type': 'info',
            'ch_name': ch_name,
            'grp_title': grp_title,
            'tvg_logo': tvg_logo,
            'tvg_id': tvg_id
        })
    else:
        # Pega o ID do canal a partir da URL do YouTube
        youtube_id = extract_youtube_id(line)
        if youtube_id:
            channel_data.append({
                'type': 'link',
                'url': f"https://ythls.armelin.one/channel/{youtube_id}.m3u8"
            })

# Escreve no arquivo .m3u
with open("ARGENTINA.m3u", "w") as f:
    f.write(banner)

    prev_item = None

    for item in channel_data:
        if item['type'] == 'info':
            prev_item = item
        if item['type'] == 'link' and item['url']:
            f.write(f'\n#EXTINF:-1 group-title="{prev_item["grp_title"]}" tvg-logo="{prev_item["tvg_logo"]}", {prev_item["ch_name"]}')
            f.write('\n')
            f.write(item['url'])
            f.write('\n')

# Escreve no arquivo JSON (opcional, mantém o formato detalhado)
prev_item = None
for item in channel_data:
    if item['type'] == 'info':
        prev_item = item
    if item['type'] == 'link' and item['url']:
        channel_data_json.append({
            "id": prev_item.get("tvg_id", ""),
            "name": prev_item["ch_name"],
            "alt_names": [""],
            "network": "",
            "owners": [""],
            "country": "AR",
            "subdivision": "",
            "city": "Buenos Aires",
            "broadcast_area": [""],
            "languages": ["spa"],
            "categories": [prev_item["grp_title"]],
            "is_nsfw": False,
            "launched": "2016-07-28",
            "closed": "2020-05-31",
            "replaced_by": "",
            "website": item['url'],
            "logo": prev_item["tvg_logo"]
        })

with open("ARGENTINA.json", "w") as f:
    json_data = json.dumps(channel_data_json, indent=2)
    f.write(json_data)


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
def process_m3u_file(input_file, output_file):
    # Faz o download do arquivo M3U da URL
    try:
        response = requests.get(input_file)
        response.raise_for_status()  # Verifica se ocorreu algum erro no download
        lines = response.text.splitlines()
    except requests.exceptions.RequestException as e:
        logger.error("Erro ao baixar o arquivo M3U: %s", str(e))
        return
    
    channel_data = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
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
                
                channel_data.append({
                    'name': ch_name,
                    'group': group_title,
                    'tvg_id': tvg_id,
                    'logo': tvg_logo,
                    'url': link,
                    'extra': extra_lines
                })
        i += 1

    # Gera o arquivo de saída M3U
    with open(output_file, "w") as f:
        f.write(banner)
        for channel in channel_data:
            extinf_line = (
                f'#EXTINF:-1 group-title="{channel["group"]}" '
                f'tvg-id="{channel["tvg_id"]}" '
                f'tvg-logo="{channel["logo"]}",{channel["name"]}'
            )
            f.write(extinf_line + '\n')
            for extra in channel['extra']:
                f.write(extra + '\n')
            f.write(channel['url'] + '\n')

    # Salva os dados em JSON para análise posterior
    with open("playlist.json", "w") as f:
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

# URL do arquivo M3U
input_url = "https://github.com/punkstarbr/STR-YT/raw/refs/heads/main/lista1.m3u"
output_file = "MASTER.m3u"

# Executa o processamento
process_m3u_file(input_url, output_file)

 
