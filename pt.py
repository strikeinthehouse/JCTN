import os

# Acessando as variáveis de ambiente do GitHub
email_ia = os.getenv('EMAIL_IA')
senha_ia = os.getenv('SENHA_IA')

# Verificando se as variáveis de ambiente estão presentes
if not email_ia or not senha_ia:
    print("Erro: As variáveis de ambiente EMAIL_IA ou SENHA_IA não estão definidas.")
else:
    # Criando o conteúdo para o arquivo .m3u8
    conteudo = f"#EXTM3U\n#EMAIL={email_ia}\n#SENHA={senha_ia}\n"

    # Salvando o conteúdo no arquivo IA.m3u8
    with open('IA.m3u8', 'w') as arquivo:
        arquivo.write(conteudo)
    
    print("Arquivo IA.m3u8 criado com sucesso!")




import subprocess

# URL do vídeo ou live do YouTube
url = "https://www.youtube.com/@recordnews/live"

# Comando para rodar o haruhi-dl
command = ["haruhi-dl", "-g", url]

# Executando o comando
result = subprocess.run(command, capture_output=True, text=True)

# Exibindo o link gerado para o download
print("Link para download:", result.stdout)




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
input_url = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/lista1.m3u"
output_file = "lista1"

# Executa o processamento
process_m3u_file(input_url, output_file)
