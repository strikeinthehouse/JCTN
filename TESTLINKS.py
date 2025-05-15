#!/usr/bin/python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import concurrent.futures
import os
import unicodedata
import re

# Configurações do Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

globoplay_urls = [
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/bom-dia-cidade-ribeirao-preto.ghtml",
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/eptv1.ghtml",
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/eptv-2-ribeirao-e-franca-ao-vivo.ghtml",
    "https://g1.globo.com/pe/petrolina-regiao/ao-vivo/ao-vivo-assista-ao-gr2.ghtml",
    "https://g1.globo.com/ap/ao-vivo/assista-ao-bdap-desta-sexta-feira-7.ghtml",
    "https://globoplay.globo.com/v/1467373/", # G1 RJ
    "https://globoplay.globo.com/v/1328766/", # G1 SP
    "https://globoplay.globo.com/v/4064559/", # G1 DF
    "https://globoplay.globo.com/v/992055/",  # GE GLOBO
    "https://globoplay.globo.com/v/602497/",  # GE SP
    "https://globoplay.globo.com/v/2135579/", # G1 RS
    "https://globoplay.globo.com/ao-vivo/5472979/", # TV Asa Branca (G1 Caruaru)
    "https://globoplay.globo.com/v/6120663/", # EPTV Ribeirão Preto (URL duplicada intencionalmente para teste)
    "https://globoplay.globo.com/v/2145544/", # G1 SC
    "https://globoplay.globo.com/v/4039160/", # G1 CE
    "https://globoplay.globo.com/v/6329086/", # Globo Esporte BA
    "https://g1.globo.com/ba/bahia/video/assista-aos-telejornais-da-tv-subae-11348407.ghtml", # TV Subaé
    "https://globoplay.globo.com/v/11999480/",# G1 ES
    "https://g1.globo.com/al/alagoas/ao-vivo/assista-aos-telejornais-da-tv-gazeta-de-alagoas.ghtml", # TV Gazeta AL
    "https://globoplay.globo.com/ao-vivo/3667427/", # G1 MG (Integração)
    "https://globoplay.globo.com/v/4218681/", # G1 Triângulo Mineiro (Uberlândia)
    "https://globoplay.globo.com/v/12945385/",# G1 Triângulo Mineiro (Uberaba)
    "https://globoplay.globo.com/v/3065772/", # G1 MS
    "https://globoplay.globo.com/v/2923579/", # G1 AP (Rede Amazônica Macapá)
    "https://g1.globo.com/am/amazonas/ao-vivo/assista-aos-telejornais-da-rede-amazonica.ghtml", # Rede Amazônica AM
    "https://g1.globo.com/am/amazonas/carnaval/2025/ao-vivo/carnaboi-2025-assista-ao-vivo.ghtml", # Eventual Amazonas
    "https://globoplay.globo.com/v/2923546/", # G1 AC (Rede Amazônica Acre)
    "https://globoplay.globo.com/v/2168377/", # G1 PA (TV Liberal)
    "https://g1.globo.com/rs/rio-grande-do-sul/video/assista-ao-saude-em-dia-6740172-1741626453929.ghtml", # Eventual RS
    "https://globoplay.globo.com/v/10747444/",# CBN SP
    "https://globoplay.globo.com/v/10740500/", # CBN RJ
    "https://g1.globo.com/pe/petrolina-regiao/video/gr1-ao-vivo-6812170-1744985218335.ghtml", # GR1 Petrolina
]

output_m3u_file = "/home/ubuntu/lista_globoplay_com_epg.m3u"
mapping_file_path = "/home/ubuntu/epg_data/mapeamento_globo_afiliadas.txt"

def normalize_text(text):
    if not text: return ""
    text = text.lower()
    nfkd_form = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    stopwords = ["hd", "sd", "ao vivo", "tv", "rede", "canal", "g1", "ge", "globoplay", "assistir", "online", "transmissao"]
    for word in stopwords:
        text = re.sub(r"\b" + re.escape(word) + r"\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[.,()!?:\"]", "", text)
    text = text.replace("&", "e")
    text = " ".join(text.split())
    return text.strip()

def load_epg_mapping(filepath):
    mapping = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            next(f)
            for line in f:
                line = line.strip()
                if ":" in line:
                    tvg_id, epg_name = line.split(":", 1)
                    normalized_epg_name = normalize_text(epg_name.strip())
                    if normalized_epg_name:
                        if normalized_epg_name not in mapping or ("hd" not in tvg_id.lower() and "hd" in mapping[normalized_epg_name][0].lower()) :
                             mapping[normalized_epg_name] = (tvg_id.strip(), epg_name.strip())
    except FileNotFoundError:
        print(f"Arquivo de mapeamento EPG não encontrado: {filepath}")
    except Exception as e:
        print(f"Erro ao carregar mapeamento EPG: {e}")
    return mapping

epg_channel_map = load_epg_mapping(mapping_file_path)
print(f"Carregados {len(epg_channel_map)} mapeamentos de EPG.")

def extract_globoplay_data(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    title = driver.title
    m3u8_url = None
    thumbnail_url = None
    time.sleep(5)
    try:
        play_button_selectors = [
            "button.poster__play-wrapper",
            "div[data-testid='player-wrapper'] button[aria-label='Play']",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'assistir') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'play')]"
        ]
        clicked_play = False
        for selector in play_button_selectors:
            try:
                element = driver.find_element(By.XPATH, selector) if selector.startswith("//") else driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed() and element.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", element)
                    print(f"Botão de play clicado para {url} usando seletor: {selector}")
                    time.sleep(20)
                    clicked_play = True
                    break
            except Exception:
                pass
        if not clicked_play:
            print(f"Nenhum botão de play funcional encontrado ou clicado para {url}. Esperando carregamento da página.")
            time.sleep(15)
    except Exception as e:
        print(f"Erro geral ao tentar interagir com o player para {url}: {e}")
        time.sleep(10)

    title = driver.title
    try:
        og_title = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute("content")
        if og_title and len(og_title) > 5: title = og_title
    except: pass
    try:
        og_image = driver.find_element(By.XPATH, "//meta[@property='og:image']").get_attribute("content")
        if og_image: thumbnail_url = og_image
    except: pass

    time.sleep(5)
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    possible_m3u8s = [entry['name'] for entry in log_entries if ".m3u8" in entry['name']]
    if possible_m3u8s:
        for m_url_option in possible_m3u8s:
            if any(k in m_url_option for k in ["master.m3u8", "playlist.m3u8", "index.m3u8"]) and not any(k in m_url_option for k in ["chunklist", "audio", "video=", "subtitle"]):
                m3u8_url = m_url_option
                break
        if not m3u8_url: m3u8_url = possible_m3u8s[-1]

    if not thumbnail_url:
        img_entries = [entry['name'] for entry in log_entries if entry['initiatorType'] == 'img' and entry['name'].endswith(('.jpg', '.jpeg', '.png', '.webp')) and not any(k in entry['name'].lower() for k in ['logo', 'avatar', 'icon'])]
        if img_entries: thumbnail_url = img_entries[0]

    driver.quit()
    return title, m3u8_url, thumbnail_url

with open(output_m3u_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U url-tvg=\"https://www.open-epg.com/files/brazil1.xml.gz\" url-tvg=\"https://www.open-epg.com/files/brazil2.xml.gz\"\n")

processed_channels_info = []
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    future_to_url = {executor.submit(extract_globoplay_data, url): url for url in globoplay_urls}
    for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
        url = future_to_url[future]
        try:
            extracted_title, m3u8_url, thumbnail_url = future.result()
            if m3u8_url:
                title_parts = extracted_title.split("|")
                display_title = title_parts[0].strip()
                if not display_title or len(display_title) < 3: display_title = extracted_title.strip()
                
                normalized_extracted_title = normalize_text(display_title)
                
                tvg_id = ""
                tvg_name = display_title

                matched_epg_id = None
                matched_epg_name = None

                if normalized_extracted_title in epg_channel_map:
                    matched_epg_id, matched_epg_name = epg_channel_map[normalized_extracted_title]
                else:
                    for norm_epg_name, (epg_id, original_epg_name) in epg_channel_map.items():
                        if normalized_extracted_title in norm_epg_name or norm_epg_name in normalized_extracted_title:
                            if len(normalized_extracted_title) > 3 and len(norm_epg_name) > 3:
                                matched_epg_id = epg_id
                                matched_epg_name = original_epg_name
                                print(f"Match parcial para \"{display_title}\" (norm: \"{normalized_extracted_title}\") com EPG \"{original_epg_name}\" (norm: \"{norm_epg_name}\") -> ID: {epg_id}")
                                break
                
                if matched_epg_id:
                    tvg_id = matched_epg_id
                    tvg_name = matched_epg_name
                    print(f"EPG Match: \"{display_title}\" -> EPG Name: \"{tvg_name}\", EPG ID: \"{tvg_id}\"")
                else:
                    tvg_id_base = "".join(c for c in normalized_extracted_title if c.isalnum() or c.isspace()).strip()
                    tvg_id = "-".join(tvg_id_base.split())
                    if not tvg_id: tvg_id = f"canal-gerado-{i+1}"
                    tvg_name = display_title
                    print(f"Sem EPG Match para \"{display_title}\" (norm: \"{normalized_extracted_title}\"). Gerado ID: {tvg_id}")

                thumbnail_url_str = thumbnail_url if thumbnail_url else ""
                group_title = "GLOBO AO VIVO"
                
                final_extinf_name = tvg_name
                if normalize_text(final_extinf_name) == "" or len(final_extinf_name) < 5:
                    final_extinf_name = display_title if len(display_title) > 5 else extracted_title.split("|")[0].strip()
                    if not final_extinf_name: final_extinf_name = f"Canal {i+1}"

                processed_channels_info.append((f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{tvg_name}\" tvg-logo=\"{thumbnail_url_str}\" group-title=\"{group_title}\",{final_extinf_name}\n", m3u8_url + "\n"))
                print(f"Processado (para M3U): {url} -> Nome EXTINF: {final_extinf_name}, TVG-ID: {tvg_id}")
            else:
                print(f"M3U8 não encontrado para {url}")
        except Exception as e:
            print(f"Erro ao processar {url}: {e}")

with open(output_m3u_file, "a", encoding="utf-8") as output_file_obj:
    for extinf_line, m3u8_line in processed_channels_info:
        output_file_obj.write(extinf_line)
        output_file_obj.write(m3u8_line)

print(f"Processamento concluído. Arquivo gerado: {output_m3u_file}")




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

 
