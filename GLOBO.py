from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurações do Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Criação do driver
driver = webdriver.Chrome(options=options)

# URL base (Google já com os filtros)
base_url = "https://duckduckgo.com/?q=assista+ao+vivo+site%3Aglobo.com&t=h_&iar=videos&start=1&iax=videos&ia=videos"

# Carrega a página
driver.get(base_url)

# Aguarda até que os links no estilo desejado estejam presentes
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li a[href*='globo.com']"))
    )

    # Extrai os elementos <a> com estrutura <li><a><article>...</a></li>
    video_elements = driver.find_elements(By.CSS_SELECTOR, "li a[href*='globo.com']")

    links_list = []
    for el in video_elements:
        href = el.get_attribute("href")
        if href:
            links_list.append(href)

    if links_list:
        print("Links encontrados:")
        for link in links_list:
            print(link)

        # Salva os links em um arquivo
        with open("links_video.txt", "w") as file:
            for link in links_list:
                file.write(link + "\n")
    else:
        print("Nenhum link encontrado.")

except Exception as e:
    print(f"Ocorreu um erro ao buscar os links: {e}")

# Função para extrair o link m3u8 e o título da página
def extract_m3u8_url_and_title(driver, url):
    driver.get(url)
    time.sleep(30)  # Pode ser ajustado ou substituído por espera dinâmica

    title = driver.title
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")

    m3u8_url = None
    logo_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name']:
            logo_url = entry['name']

    return title, m3u8_url, logo_url

# Abre o arquivo com os links
with open("links_video.txt", "r") as file:
    links = file.readlines()

# Gera arquivo M3U
with open("lista1.m3u", "w") as output_file:
    for link in links:
        link = link.strip()

        if not link:
            continue

        print(f"Processando link: {link}")

        try:
            title, m3u8_url, logo_url = extract_m3u8_url_and_title(driver, link)

            if m3u8_url:
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="VOD GLOBO", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"✓ M3U8 encontrado: {m3u8_url}")
            else:
                print(f"⚠️ Link .m3u8 não encontrado para: {title}")

        except Exception as e:
            print(f"❌ Erro ao processar o link {link}: {e}")

# Finaliza o driver
driver.quit()




from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import concurrent.futures

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
    "https://g1.globo.com/sp/campinas-regiao/ao-vivo/eptv-2-campinas-ao-vivo.ghtml"
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/eptv-2-ribeirao-e-franca-ao-vivo.ghtml",  # EPTV 2ª Edição - Ribeirão e Franca
    "https://g1.globo.com/pe/petrolina-regiao/ao-vivo/ao-vivo-assista-ao-gr2.ghtml",  # GR2 - Petrolina
    "https://g1.globo.com/ap/ao-vivo/assista-ao-bdap-desta-sexta-feira-7.ghtml",  # BDAP - Amapá
    "https://g1.globo.com/pr/parana/ao-vivo/acontece-agora-em-curitiba.ghtml",
    "https://globoplay.globo.com/v/1467373/",  # Globoplay - Transmissão ao vivo
    "https://globoplay.globo.com/v/1328766/",  # G1 SERVIÇO
    "https://globoplay.globo.com/v/4064559/",  # G1 SERVIÇO
    "https://globoplay.globo.com/v/992055/",  # G1 SERVIÇO
    "https://globoplay.globo.com/v/602497/",  # ge SERVIÇO
    "https://globoplay.globo.com/v/2135579/",  # G1 RS - Telejornais da RBS TV
    "https://globoplay.globo.com/ao-vivo/5472979/",
    "https://globoplay.globo.com/v/6120663/",  # G1 RS - Jornal da EPTV 1ª Edição - Ribeirão Preto
    "https://globoplay.globo.com/v/2145544/",  # G1 SC - Telejornais da NSC TV
    "https://globoplay.globo.com/v/4039160/",  # G1 CE - TV Verdes Mares ao vivo
    "https://globoplay.globo.com/v/6329086/",  # Globo Esporte BA - Travessia Itaparica-Salvador ao vivo
    "https://g1.globo.com/ba/bahia/video/assista-aos-telejornais-da-tv-subae-11348407.ghtml",
    "https://globoplay.globo.com/v/11999480/",  # G1 ES - Jornal Regional ao vivo
    "https://g1.globo.com/al/alagoas/ao-vivo/assista-aos-telejornais-da-tv-gazeta-de-alagoas.ghtml",  # Telejornais da TV Gazeta de Alagoas
    "https://globoplay.globo.com/ao-vivo/3667427/",  # Globoplay - Transmissão ao vivo
    "https://globoplay.globo.com/v/4218681/",  # G1 Triângulo Mineiro - Transmissão ao vivo
    "https://globoplay.globo.com/v/12945385/",  # Globoplay - Transmissão ao vivo
    "https://globoplay.globo.com/v/3065772/",  # G1 MS - Transmissão ao vivo em MS
    "https://globoplay.globo.com/v/2923579/",  # G1 AP - Telejornais da Rede Amazônica
    "https://g1.globo.com/am/amazonas/ao-vivo/assista-aos-telejornais-da-rede-amazonica.ghtml",  # Telejornais da Rede Amazônica - Amazonas
    "https://g1.globo.com/am/amazonas/carnaval/2025/ao-vivo/carnaboi-2025-assista-ao-vivo.ghtml",
    "https://g1.globo.com/ap/ao-vivo/assista-ao-jap2-deste-sabado-10.ghtml",
    "https://globoplay.globo.com/v/2923546/",  # G1 AC - Jornais da Rede Amazônica
    "https://globoplay.globo.com/v/2168377/",  # Telejornais da TV Liberal
    "https://g1.globo.com/rs/rio-grande-do-sul/video/assista-ao-saude-em-dia-6740172-1741626453929.ghtml",
    "https://globoplay.globo.com/v/10747444/",  # CBN SP - Transmissão ao vivo
    "https://globoplay.globo.com/v/10740500/",  # CBN RJ - Transmissão ao vivo
    "https://g1.globo.com/pe/petrolina-regiao/video/gr1-ao-vivo-6812170-1744985218335.ghtml",
]

def extract_globoplay_data(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    # Função para tentar clicar no botão de play
    def try_click_play():
        try:
            # Tenta encontrar e clicar no botão de play
            play_buttons = [
                "button.poster__play-wrapper",  # Botão de play padrão
                "button[aria-label='Reproduzir vídeo']",  # Botão alternativo
                ".playkit-pre-playback-play-button",  # Outro possível botão
                "button.playkit-control-button"  # Outro possível botão
            ]
            
            for selector in play_buttons:
                try:
                    play_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if play_button and play_button.is_displayed():
                        play_button.click()
                        print(f"Clicou no botão de play ({selector}) para {url}")
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            print(f"Erro ao tentar clicar no botão de play: {e}")
            return False
    
    # Tenta clicar no botão de play
    play_clicked = try_click_play()
    
    # Implementação para tentar novamente até 4 vezes se aparecer erro
    retry_attempts = 0
    max_retries = 4
    
    while retry_attempts < max_retries:
        try:
            # Verifica se há mensagem de erro e botão "Tentar novamente"
            error_elements = [
                "a[href='javascript:void(0)'][class*='retry']",  # Link de retry
                "a:contains('Tentar novamente')",  # Texto "Tentar novamente"
                ".error-message-container a",  # Container de erro com link
                "a.retry-button"  # Botão de retry
            ]
            
            retry_button = None
            for selector in error_elements:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if "tentar novamente" in element.text.lower() or "retry" in element.text.lower():
                            retry_button = element
                            break
                    if retry_button:
                        break
                except Exception:
                    continue
            
            # Se encontrou botão de retry, clica nele
            if retry_button:
                print(f"Tentativa {retry_attempts + 1}/{max_retries}: Clicando em 'Tentar novamente' para {url}")
                retry_button.click()
                time.sleep(5)  # Espera um pouco após clicar
                
                # Tenta clicar no play novamente
                play_clicked = try_click_play()
                retry_attempts += 1
            else:
                # Se não encontrou botão de retry, sai do loop
                break
                
        except Exception as e:
            print(f"Erro ao tentar novamente: {e}")
            retry_attempts += 1
            time.sleep(3)
    
    # Espera para carregar recursos
    time.sleep(56)
    
    # Coleta informações
    title = driver.title
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    m3u8_url = None
    thumbnail_url = None
    
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name'] and not thumbnail_url:
            thumbnail_url = entry['name']
    
    driver.quit()
    return title, m3u8_url, thumbnail_url

def process_m3u_file(input_url, output_file):
    # Implementação da função process_m3u_file
    # (Esta função estava mencionada no final do código original mas não estava implementada)
    pass

with open("lista1.m3u", "a") as output_file:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(extract_globoplay_data, url): url for url in globoplay_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title, m3u8_url, thumbnail_url = future.result()
                if m3u8_url:
                    thumbnail_url = thumbnail_url if thumbnail_url else ""
                    output_file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="GLOBO AO VIVO", {title}\n')
                    output_file.write(f"{m3u8_url}\n")
                    print(f"Processado com sucesso: {url}")
                else:
                    print(f"M3U8 não encontrado para {url}")
            except Exception as e:
                print(f"Erro ao processar {url}: {e}")

# Comentado pois a função não está implementada e parece ser uma chamada incorreta
# process_m3u_file(input_url, output_file)




##VEJA AI

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

print("Iniciando o script de extração do CXTv...")

# Configure Chrome options (incorporando sugestões e mantendo headless)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage") # Importante para ambientes limitados
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,800") # Tamanho ajustado
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-infobars") # Adicionado da sugestão

# Create the webdriver instance
try:
    print("Configurando o WebDriver...")
    driver = webdriver.Chrome(options=options)
    # Tenta esconder a automação
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("WebDriver configurado.")
except Exception as e:
    print(f"Erro ao configurar o WebDriver: {e}")
    exit()

# URL de busca do CXTv
search_url = "https://www.cxtv.com.br/busca/?query=Record"
output_filename = "lista_cxtv.m3u"

# Lista para armazenar informações dos canais
channels_info = []

try:
    print(f"Acessando a URL: {search_url}")
    driver.get(search_url)

    # Esperar os cards de resultado carregarem
    wait_time = 30 # Tempo de espera
    print(f"Aguardando {wait_time} segundos pelos resultados (div.col-item a img)...")
    WebDriverWait(driver, wait_time).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.col-item a img'))
    )
    print("Resultados encontrados. Extraindo informações dos links...")

    # Encontrar todos os links dos canais na página de busca
    channel_links = driver.find_elements(By.CSS_SELECTOR, 'div.col-item a')
    print(f"Encontrados {len(channel_links)} links de canais na página de busca.")

    for link_element in channel_links:
        page_url = None
        title = None
        logo_url = None
        try:
            page_url = link_element.get_attribute('href')
            if not page_url or not page_url.startswith("http"): # Ignora links inválidos
                print(f"  - Aviso: URL inválida ou ausente encontrada, pulando.")
                continue

            # Tenta extrair o título
            try:
                # Tenta pelo h3 dentro do link
                title_element = link_element.find_element(By.CSS_SELECTOR, 'h3.mt-2')
                title = title_element.text.strip()
            except:
                # Se falhar, tenta pelo atributo 'title' do link
                try:
                    title = link_element.get_attribute('title').strip()
                except:
                    # Se falhar, tenta pegar o texto interno e limpar
                    full_text = link_element.text.strip()
                    if '\n' in full_text:
                        title = full_text.split('\n')[0] # Pega a primeira linha
                    else:
                        title = full_text # Usa o texto completo se não houver quebra

            # Tenta extrair a logo
            try:
                img_element = link_element.find_element(By.TAG_NAME, 'img')
                logo_url = img_element.get_attribute('src')
            except:
                logo_url = "" # Deixa vazio se não encontrar

            # Verifica se temos informações essenciais
            if page_url and title:
                channels_info.append({
                    'title': title,
                    'page_url': page_url,
                    'logo_url': logo_url
                })
                print(f"  - Canal adicionado: {title} ({page_url})")
            else:
                 print(f"  - Aviso: Link ({page_url}) ou título ({title}) ausente para um elemento.")

        except Exception as e:
            print(f"Erro ao processar um link da busca ({page_url}): {e}")

except Exception as e:
    print(f"Erro crítico ao carregar ou processar a página de busca: {e}")
    try:
        driver.save_screenshot("erro_busca.png")
        print("Screenshot 'erro_busca.png' salvo.")
    except:
        print("Não foi possível salvar o screenshot.")

print(f"\nTotal de {len(channels_info)} canais encontrados para processar.")

# Função para extrair o link m3u8
def extract_m3u8_url(driver, url):
    print(f"  Acessando página do canal: {url}")
    m3u8_url = None
    try:
        driver.get(url)
        print("  Aguardando até 60 segundos para carregamento e possível início do stream...")
        # Espera um pouco mais flexível por algum elemento que indique carregamento, ou apenas tempo
        time.sleep(60) # Aumentado para dar tempo a players complexos/ads

        print("  Verificando logs de rede para M3U8...")
        try:
            log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
            for entry in log_entries:
                if entry and 'name' in entry and '.m3u8' in entry['name']:
                    m3u8_url = entry['name']
                    print(f"    * Encontrado M3U8 nos logs de rede: {m3u8_url}")
                    return m3u8_url # Retorna o primeiro encontrado
        except Exception as log_err:
            print(f"    Erro ao obter logs de rede: {log_err}")

        if not m3u8_url:
             print("    - Nenhum M3U8 encontrado nos logs de rede iniciais. Verificando iframes...")
             try:
                 iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                 if iframes:
                     print(f"    Encontrado(s) {len(iframes)} iframe(s).")
                     for i, frame in enumerate(iframes):
                         try:
                             print(f"      Entrando no iframe {i}...")
                             driver.switch_to.frame(frame)
                             print("      Aguardando 15 segundos dentro do iframe...")
                             time.sleep(15)
                             print("      Verificando logs de rede dentro do iframe...")
                             iframe_log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
                             for entry in iframe_log_entries:
                                 if entry and 'name' in entry and '.m3u8' in entry['name']:
                                     m3u8_url = entry['name']
                                     print(f"        * Encontrado M3U8 no iframe: {m3u8_url}")
                                     driver.switch_to.default_content()
                                     return m3u8_url # Retorna assim que encontrar
                             print(f"      Saindo do iframe {i} (M3U8 não encontrado nele).")
                             driver.switch_to.default_content()
                         except Exception as frame_error:
                             print(f"      Erro ao processar iframe {i}: {frame_error}")
                             # Tenta sair do iframe mesmo em caso de erro
                             try:
                                 driver.switch_to.default_content()
                             except:
                                 pass # Ignora se já estiver fora
                 else:
                     print("    Nenhum iframe encontrado na página.")
             except Exception as iframe_find_error:
                 print(f"    Erro ao procurar/processar iframes: {iframe_find_error}")

        if not m3u8_url:
            print("  M3U8 não encontrado após todas as tentativas.")
            # Salvar screenshot apenas se não encontrar
            try:
                safe_filename = f"erro_m3u8_{url.split('//')[-1].replace('/', '_').replace('?', '_').replace('=', '_')}.png"
                driver.save_screenshot(safe_filename)
                print(f"  Screenshot '{safe_filename}' salvo.")
            except Exception as ss_error:
                print(f"  Não foi possível salvar o screenshot de erro M3U8: {ss_error}")
        return None # Retorna None se não encontrou

    except Exception as e:
        print(f"  Erro crítico ao processar a página do canal {url}: {e}")
        try:
            safe_filename = f"erro_pagina_{url.split('//')[-1].replace('/', '_').replace('?', '_').replace('=', '_')}.png"
            driver.save_screenshot(safe_filename)
            print(f"  Screenshot '{safe_filename}' salvo.")
        except Exception as ss_error:
             print(f"  Não foi possível salvar o screenshot de erro da página: {ss_error}")
        return None

# Processar cada canal encontrado
print("\nIniciando processamento individual dos canais para extrair M3U8...")

processed_count = 0
found_m3u8_count = 0

# Abrir o arquivo de saída M3U
with open(output_filename, "w", encoding='utf-8') as output_file:
    output_file.write("#EXTM3U\n") # Cabeçalho padrão M3U

    for i, channel in enumerate(channels_info):
        print(f"\nProcessando canal {i+1}/{len(channels_info)}: {channel['title']}")

        m3u8_link = extract_m3u8_url(driver, channel['page_url'])
        processed_count += 1

        if m3u8_link:
            found_m3u8_count += 1
            # Escrever no formato EXTM3U - CORRIGIDO
            # Limpa o título para evitar quebras de linha ou caracteres problemáticos no M3U
            clean_title = channel['title'].replace('\n', ' ').replace('\r', '').strip()
            output_file.write(f'#EXTINF:-1 tvg-logo="{channel["logo_url"]}" group-title="Record",{clean_title}\n')
            output_file.write(f"{m3u8_link}\n")
            print(f"  -> M3U8 encontrado e adicionado ao arquivo: {m3u8_link}")
        else:
            print(f"  -> M3U8 não encontrado para {channel['title']}")

print(f"\nProcessamento concluído.")
print(f"Total de canais processados: {processed_count}")
print(f"Total de links M3U8 encontrados: {found_m3u8_count}")
print(f"Arquivo M3U gerado: {output_filename}")

# Sair do driver
print("Fechando o WebDriver...")
driver.quit()
print("Script finalizado.")




# Definir o caminho do arquivo
m3u_file_path = os.path.join(os.getcwd(), "it.txt")
write_m3u_file(links, m3u_file_path)

print(f"Arquivo M3U foi criado: {m3u_file_path}")

import os
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
from bs4 import BeautifulSoup
from streamlink import Streamlink

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

# Função para verificar URLs usando Streamlink
def check_url_with_streamlink(url):
    session = Streamlink()
    try:
        streams = session.streams(url)
        if streams:
            logger.info("URL válida com Streamlink: %s", url)
            return True
        else:
            logger.warning("Nenhum stream encontrado para a URL: %s", url)
            return False
    except Exception as e:
        logger.error("Erro ao processar a URL com Streamlink %s: %s", url, str(e))
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
            if link and check_url_with_streamlink(link):
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
        logger.error("Erro ao buscar imagens no Google: %s", e)
    
    return None

# URL do arquivo M3U
input_url = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/lista1.m3u"
output_file = "lista1.m3u"

# Executa o processamento
process_m3u_file(input_url, output_file)
