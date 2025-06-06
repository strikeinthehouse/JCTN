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
"""
Script para extrair conteúdo de TV do site archive.org
Adaptado para trabalhar com arquivos históricos de televisão
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import re
import json
import sys
import os
from urllib.parse import urljoin

print("Iniciando o script de extração do Archive.org...")

class ArchiveOrgTVExtractor:
    def __init__(self):
        self.main_url = "https://archive.org/details/@tv"
        self.output_filename = "lista_archive_org.m3u"
        self.items_info = []
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o WebDriver com as especificações do usuário"""
        print("Configurando o WebDriver...")
        
        # Configurações do Chrome conforme especificado pelo usuário
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-infobars")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("WebDriver configurado com sucesso.")
        except Exception as e:
            print(f"Erro ao configurar o WebDriver: {e}")
            raise
    
    def extract_tv_items_from_main_page(self, max_items=50):
        """Extrai lista de itens de TV da página principal"""
        print(f"Acessando a URL principal: {self.main_url}")
        self.driver.get(self.main_url)
        
        # Aguardar carregamento da página
        wait_time = 15
        print(f"Aguardando {wait_time} segundos para carregamento...")
        WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Scroll para carregar mais conteúdo
        print("Fazendo scroll para carregar mais itens...")
        self.scroll_to_load_content()
        
        # Extrair itens usando JavaScript
        print(f"Extraindo lista de itens (máximo {max_items})...")
        items_data = self.extract_items_with_js(max_items)
        
        print(f"Encontrados {len(items_data)} itens válidos")
        return items_data
    
    def scroll_to_load_content(self):
        """Faz scroll na página para carregar mais conteúdo"""
        for i in range(3):  # Máximo 3 scrolls
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
    
    def extract_items_with_js(self, max_items):
        """Extrai itens usando JavaScript"""
        js_script = f"""
        (() => {{
            const items = [];
            
            // Buscar todos os links de itens
            const itemElements = document.querySelectorAll('a[aria-label]');
            
            itemElements.forEach((element, index) => {{
                if (items.length >= {max_items}) return;
                
                const href = element.href;
                const title = element.getAttribute('aria-label') || '';
                
                // Filtrar apenas itens válidos do archive.org
                if (href && href.includes('archive.org/details/') && title) {{
                    // Extrair ID do item
                    const itemId = href.split('/details/')[1];
                    
                    if (itemId && !itemId.includes('?') && !itemId.includes('#')) {{
                        items.push({{
                            title: title.trim(),
                            url: href,
                            itemId: itemId,
                            index: index
                        }});
                    }}
                }}
            }});
            
            return items;
        }})();
        """
        
        try:
            return self.driver.execute_script(js_script)
        except Exception as e:
            print(f"Erro ao extrair itens: {e}")
            return []
    
    def extract_media_from_item(self, item_url, item_title, item_id):
        """Extrai links de mídia de um item específico"""
        print(f"  Processando: {item_title}")
        print(f"  URL: {item_url}")
        
        try:
            self.driver.get(item_url)
            time.sleep(10)  # Aguardar carregamento
            
            # Procurar por links de download direto
            print("  Procurando links de mídia...")
            
            media_info = self.extract_media_links(item_id)
            
            if media_info:
                print(f"    ✓ Mídia encontrada: {len(media_info)} arquivo(s)")
                return media_info
            else:
                print(f"    ✗ Nenhuma mídia encontrada")
                return None
                
        except Exception as e:
            print(f"  Erro ao processar {item_title}: {e}")
            return None
    
    def extract_media_links(self, item_id):
        """Extrai links de mídia usando a API do Archive.org"""
        try:
            # URL da API de metadados do Archive.org
            metadata_url = f"https://archive.org/metadata/{item_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(metadata_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                metadata = response.json()
                
                if 'files' in metadata:
                    media_files = []
                    
                    for file_info in metadata['files']:
                        filename = file_info.get('name', '')
                        format_type = file_info.get('format', '').lower()
                        
                        # Filtrar apenas arquivos de vídeo
                        if any(ext in filename.lower() for ext in ['.mp4', '.avi', '.mkv', '.mov', '.m4v']):
                            download_url = f"https://archive.org/download/{item_id}/{filename}"
                            
                            media_files.append({
                                'filename': filename,
                                'format': format_type,
                                'download_url': download_url,
                                'size': file_info.get('size', 'Unknown')
                            })
                    
                    return media_files if media_files else None
            
            return None
            
        except Exception as e:
            print(f"    Erro na API: {e}")
            return None
    
    def validate_media_link(self, url, timeout=10):
        """Valida se um link de mídia está acessível"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            return response.status_code == 200
            
        except Exception as e:
            print(f"    Erro na validação: {e}")
            return False
    
    def create_m3u_file(self, items_with_media):
        """Cria o arquivo M3U com os itens encontrados"""
        print(f"\nCriando arquivo M3U: {self.output_filename}")
        
        with open(self.output_filename, "w", encoding='utf-8') as output_file:
            output_file.write("#EXTM3U\n")
            
            for item in items_with_media:
                clean_title = item['title'].replace('\n', ' ').replace('\r', '').strip()
                
                # Se há múltiplos arquivos de mídia, criar entrada para cada um
                for media in item['media_files']:
                    filename = media['filename']
                    download_url = media['download_url']
                    file_format = media['format']
                    
                    # Criar título descritivo
                    media_title = f"{clean_title} - {filename}"
                    
                    output_file.write(f'#EXTINF:-1 tvg-logo="" group-title="Archive.org",{media_title}\n')
                    output_file.write(f"{download_url}\n")
        
        print(f"Arquivo M3U criado com sucesso!")
    
    def run(self, max_items=50):
        """Executa o processo completo de extração"""
        try:
            # Extrair lista de itens
            self.items_info = self.extract_tv_items_from_main_page(max_items)
            
            if not self.items_info:
                print("Nenhum item encontrado. Encerrando.")
                return
            
            print(f"\nTotal de {len(self.items_info)} itens para processar")
            
            # Processar cada item
            processed_count = 0
            found_media_count = 0
            items_with_media = []
            
            for i, item in enumerate(self.items_info):
                print(f"\n[{i+1}/{len(self.items_info)}] Processando: {item['title']}")
                
                media_files = self.extract_media_from_item(item['url'], item['title'], item['itemId'])
                processed_count += 1
                
                if media_files:
                    found_media_count += 1
                    
                    # Validar pelo menos um arquivo
                    valid_files = []
                    for media in media_files[:3]:  # Verificar apenas os primeiros 3 arquivos
                        if self.validate_media_link(media['download_url']):
                            valid_files.append(media)
                            print(f"    ✓ Arquivo válido: {media['filename']}")
                        else:
                            print(f"    ✗ Arquivo inacessível: {media['filename']}")
                    
                    if valid_files:
                        item['media_files'] = valid_files
                        items_with_media.append(item)
                        print(f"  ✓ Item adicionado com {len(valid_files)} arquivo(s)")
                    else:
                        print(f"  ✗ Nenhum arquivo válido encontrado")
                else:
                    print(f"  ✗ Item sem mídia válida")
                
                # Pequena pausa entre itens
                time.sleep(2)
            
            # Criar arquivo M3U
            if items_with_media:
                self.create_m3u_file(items_with_media)
            
            # Relatório final
            print(f"\n" + "="*50)
            print(f"PROCESSAMENTO CONCLUÍDO - ARCHIVE.ORG")
            print(f"="*50)
            print(f"Total de itens processados: {processed_count}")
            print(f"Total de itens com mídia: {found_media_count}")
            print(f"Taxa de sucesso: {(found_media_count/processed_count)*100:.1f}%")
            print(f"Arquivo M3U gerado: {self.output_filename}")
            
            # Salvar relatório detalhado
            self.save_detailed_report(items_with_media, processed_count, found_media_count)
            
        except Exception as e:
            print(f"Erro crítico no processamento: {e}")
        finally:
            if self.driver:
                print("Fechando o WebDriver...")
                self.driver.quit()
                print("Script finalizado.")
    
    def save_detailed_report(self, items_with_media, processed_count, found_media_count):
        """Salva um relatório detalhado do processamento"""
        report_filename = "archive_org_extraction_report.txt"
        
        with open(report_filename, "w", encoding='utf-8') as report_file:
            report_file.write("RELATÓRIO DE EXTRAÇÃO - ARCHIVE.ORG\n")
            report_file.write("="*45 + "\n\n")
            report_file.write(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            report_file.write(f"Total de itens processados: {processed_count}\n")
            report_file.write(f"Total de itens com mídia: {found_media_count}\n")
            report_file.write(f"Taxa de sucesso: {(found_media_count/processed_count)*100:.1f}%\n\n")
            
            report_file.write("ITENS COM MÍDIA DISPONÍVEL:\n")
            report_file.write("-"*30 + "\n")
            
            for i, item in enumerate(items_with_media, 1):
                report_file.write(f"{i}. {item['title']}\n")
                report_file.write(f"   URL: {item['url']}\n")
                report_file.write(f"   Item ID: {item['itemId']}\n")
                report_file.write(f"   Arquivos de mídia:\n")
                
                for media in item['media_files']:
                    report_file.write(f"     - {media['filename']} ({media['format']})\n")
                    report_file.write(f"       {media['download_url']}\n")
                
                report_file.write("\n")
        
        print(f"Relatório detalhado salvo: {report_filename}")

def get_max_items():
    """Obtém o número máximo de itens a processar"""
    # Verificar se foi passado como argumento de linha de comando
    if len(sys.argv) > 1:
        try:
            max_items = int(sys.argv[1])
            print(f"Usando valor do argumento: {max_items} itens")
            return max_items
        except ValueError:
            print(f"Argumento inválido '{sys.argv[1]}', usando valor padrão")
    
    # Verificar se existe variável de ambiente
    env_value = os.environ.get('MAX_ITEMS')
    if env_value:
        try:
            max_items = int(env_value)
            print(f"Usando valor da variável de ambiente MAX_ITEMS: {max_items} itens")
            return max_items
        except ValueError:
            print(f"Variável de ambiente MAX_ITEMS inválida '{env_value}', usando valor padrão")
    
    # Verificar se está em ambiente interativo
    if sys.stdin.isatty():
        try:
            max_items_input = input("Quantos itens processar? (padrão: 20): ").strip()
            if max_items_input.isdigit():
                max_items = int(max_items_input)
                print(f"Usando valor informado: {max_items} itens")
                return max_items
        except (EOFError, KeyboardInterrupt):
            print("Entrada interrompida, usando valor padrão")
    
    # Valor padrão
    print("Usando valor padrão: 20 itens")
    return 20

def main():
    """Função principal"""
    print("Archive.org TV Extractor")
    print("Este script extrai arquivos de vídeo históricos do Archive.org")
    print("Nota: Este não é um serviço de IPTV ao vivo, mas um arquivo histórico")
    print()
    print("Formas de especificar o número de itens:")
    print("1. Argumento de linha de comando: python GLOBO.py 30")
    print("2. Variável de ambiente: export MAX_ITEMS=30")
    print("3. Entrada interativa (se disponível)")
    print("4. Valor padrão: 20 itens")
    print()
    
    max_items = get_max_items()
    
    extractor = ArchiveOrgTVExtractor()
    extractor.run(max_items)

if __name__ == "__main__":
    main()



# -*- coding: utf-8 -*-
"""
Script atualizado para extrair links de IPTV do site telearg.weebly.com
Usando configuração específica do Chrome conforme solicitado
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import re
import json

print("Iniciando o script atualizado de extração do TeleArg...")

class TeleArgExtractorUpdated:
    def __init__(self):
        self.main_url = "https://telearg.weebly.com/"
        self.output_filename = "lista_telearg_updated.m3u"
        self.channels_info = []
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o WebDriver com as especificações do usuário"""
        print("Configurando o WebDriver...")
        
        # Configurações do Chrome conforme especificado pelo usuário
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-infobars")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("WebDriver configurado com sucesso.")
        except Exception as e:
            print(f"Erro ao configurar o WebDriver: {e}")
            raise
    
    def extract_channels_from_main_page(self):
        """Extrai lista de canais da página principal"""
        print(f"Acessando a URL principal: {self.main_url}")
        self.driver.get(self.main_url)
        
        # Aguardar carregamento da página
        wait_time = 15
        print(f"Aguardando {wait_time} segundos para carregamento...")
        WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Scroll para carregar todo o conteúdo
        print("Fazendo scroll para carregar todos os canais...")
        self.scroll_to_load_content()
        
        # Extrair canais usando JavaScript
        print("Extraindo lista de canais...")
        channels_data = self.extract_channels_with_js()
        
        print(f"Encontrados {len(channels_data)} canais válidos")
        return channels_data
    
    def scroll_to_load_content(self):
        """Faz scroll na página para carregar todo o conteúdo"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(5):  # Máximo 5 scrolls
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def extract_channels_with_js(self):
        """Extrai canais usando JavaScript"""
        js_script = """
        (() => {
            const channels = [];
            
            // Buscar todos os links de canais na grade
            const channelElements = document.querySelectorAll('a[href*=".html"]');
            
            channelElements.forEach((element, index) => {
                const href = element.href;
                const img = element.querySelector('img');
                let title = '';
                let logo = '';
                
                if (img) {
                    title = img.alt || '';
                    logo = img.src || '';
                }
                
                // Se não tem título do alt, tentar pegar do texto
                if (!title) {
                    title = element.textContent.trim();
                }
                
                // Extrair nome do canal da URL se necessário
                if (!title && href.includes('.html')) {
                    const urlParts = href.split('/');
                    const filename = urlParts[urlParts.length - 1];
                    title = filename.replace('.html', '').replace(/-/g, ' ').toUpperCase();
                }
                
                // Filtrar apenas canais válidos (não páginas de categoria)
                const skipPages = [
                    'argentina.html', 'noticias-internacionales.html', 'caba.html', 
                    'buenos-aires.html', 'catamarca.html', 'chaco.html', 'chubut.html',
                    'cordoba.html', 'corrientes.html', 'entre-rios.html', 'formosa.html',
                    'jujuy.html', 'la-pampa.html', 'la-rioja.html', 'mendoza.html',
                    'misiones.html', 'neuquen.html', 'rio-negro.html', 'salta.html',
                    'san-juan.html', 'san-luis1.html', 'santa-cruz.html', 'santa-fe.html',
                    'tierra-del-fuego.html', 'tucuman.html', 'religiosos.html', 'otros.html',
                    'radio-tv.html', 'internacionales.html', 'streaming.html'
                ];
                
                const isSkipPage = skipPages.some(page => href.includes(page));
                
                if (href && title && !isSkipPage && logo) {
                    channels.push({
                        title: title.trim(),
                        url: href,
                        logo: logo
                    });
                }
            });
            
            return channels;
        })();
        """
        
        try:
            return self.driver.execute_script(js_script)
        except Exception as e:
            print(f"Erro ao extrair canais: {e}")
            return []
    
    def validate_m3u8_link(self, url, timeout=10):
        """Valida se um link m3u8 está funcionando"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
            if response.status_code == 200:
                return True
            
            response = requests.get(url, timeout=timeout, stream=True, headers=headers)
            if response.status_code == 200:
                content = response.iter_content(chunk_size=1024).__next__().decode('utf-8', errors='ignore')
                if '#EXTM3U' in content or '#EXT-X-' in content:
                    return True
            
            return False
        except Exception as e:
            print(f"    Erro na validação: {e}")
            return False
    
    def extract_m3u8_from_network_logs(self):
        """Extrai links m3u8 dos logs de rede"""
        try:
            log_entries = self.driver.execute_script("return window.performance.getEntriesByType('resource');")
            m3u8_links = []
            
            for entry in log_entries:
                if entry and 'name' in entry and ".m3u8" in entry['name']:
                    m3u8_links.append(entry['name'])
            
            return m3u8_links
        except Exception as e:
            print(f"    Erro ao obter logs de rede: {e}")
            return []
    
    def extract_m3u8_from_page_source(self):
        """Extrai links m3u8 do código fonte da página"""
        try:
            page_source = self.driver.page_source
            # Padrões para encontrar links m3u8
            patterns = [
                r'https?://[^\s"\']+\.m3u8[^\s"\']*',
                r'"(https?://[^"]+\.m3u8[^"]*)"',
                r"'(https?://[^']+\.m3u8[^']*)'"
            ]
            
            m3u8_links = []
            for pattern in patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                m3u8_links.extend(matches)
            
            # Remover duplicatas
            return list(set(m3u8_links))
        except Exception as e:
            print(f"    Erro ao extrair do código fonte: {e}")
            return []
    
    def extract_m3u8_url(self, channel_url, channel_title):
        """Extrai o link m3u8 de uma página de canal"""
        print(f"  Processando: {channel_title}")
        print(f"  URL: {channel_url}")
        
        try:
            self.driver.get(channel_url)
            
            # Aguardar carregamento inicial
            time.sleep(10)
            
            # Primeira tentativa: logs de rede
            print("  Verificando logs de rede...")
            m3u8_links = self.extract_m3u8_from_network_logs()
            
            for link in m3u8_links:
                print(f"    * Testando M3U8: {link}")
                if self.validate_m3u8_link(link):
                    print(f"    ✓ Link validado com sucesso")
                    return link
                else:
                    print(f"    ✗ Link não está funcionando")
            
            # Segunda tentativa: aguardar mais tempo
            print("  Aguardando mais tempo para carregamento...")
            time.sleep(30)
            
            m3u8_links = self.extract_m3u8_from_network_logs()
            for link in m3u8_links:
                print(f"    * Testando M3U8 (2ª tentativa): {link}")
                if self.validate_m3u8_link(link):
                    print(f"    ✓ Link validado com sucesso")
                    return link
            
            # Terceira tentativa: código fonte
            print("  Verificando código fonte...")
            m3u8_links = self.extract_m3u8_from_page_source()
            
            for link in m3u8_links:
                print(f"    * Testando M3U8 do código fonte: {link}")
                if self.validate_m3u8_link(link):
                    print(f"    ✓ Link do código fonte validado")
                    return link
            
            # Quarta tentativa: verificar iframes
            print("  Verificando iframes...")
            return self.extract_from_iframes()
            
        except Exception as e:
            print(f"  Erro crítico ao processar {channel_title}: {e}")
            return None
    
    def extract_from_iframes(self):
        """Extrai links m3u8 de iframes"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            if not iframes:
                print("    Nenhum iframe encontrado")
                return None
            
            print(f"    Encontrado(s) {len(iframes)} iframe(s)")
            
            for i, frame in enumerate(iframes):
                try:
                    print(f"      Processando iframe {i+1}...")
                    self.driver.switch_to.frame(frame)
                    time.sleep(15)
                    
                    # Verificar logs de rede do iframe
                    iframe_links = self.extract_m3u8_from_network_logs()
                    
                    for link in iframe_links:
                        print(f"        * Testando M3U8 do iframe: {link}")
                        self.driver.switch_to.default_content()
                        
                        if self.validate_m3u8_link(link):
                            print(f"        ✓ Link do iframe validado")
                            return link
                        
                        # Voltar para o iframe para continuar
                        self.driver.switch_to.frame(frame)
                    
                    self.driver.switch_to.default_content()
                    
                except Exception as frame_error:
                    print(f"      Erro ao processar iframe {i+1}: {frame_error}")
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
            
            return None
            
        except Exception as e:
            print(f"    Erro ao processar iframes: {e}")
            return None
    
    def create_m3u_file(self, channels_with_links):
        """Cria o arquivo M3U com os canais encontrados"""
        print(f"\nCriando arquivo M3U: {self.output_filename}")
        
        with open(self.output_filename, "w", encoding='utf-8') as output_file:
            output_file.write("#EXTM3U\n")
            
            for channel in channels_with_links:
                clean_title = channel['title'].replace('\n', ' ').replace('\r', '').strip()
                logo_url = channel.get('logo', '')
                m3u8_link = channel['m3u8_url']
                
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="TeleArg",{clean_title}\n')
                output_file.write(f"{m3u8_link}\n")
        
        print(f"Arquivo M3U criado com sucesso!")
    
    def run(self):
        """Executa o processo completo de extração"""
        try:
            # Extrair lista de canais
            self.channels_info = self.extract_channels_from_main_page()
            
            if not self.channels_info:
                print("Nenhum canal encontrado. Encerrando.")
                return
            
            print(f"\nTotal de {len(self.channels_info)} canais para processar")
            
            # Processar cada canal
            processed_count = 0
            found_m3u8_count = 0
            channels_with_links = []
            
            for i, channel in enumerate(self.channels_info):
                print(f"\n[{i+1}/{len(self.channels_info)}] Processando: {channel['title']}")
                
                m3u8_link = self.extract_m3u8_url(channel['url'], channel['title'])
                processed_count += 1
                
                if m3u8_link:
                    found_m3u8_count += 1
                    channel['m3u8_url'] = m3u8_link
                    channels_with_links.append(channel)
                    print(f"  ✓ Link encontrado e validado")
                else:
                    print(f"  ✗ Canal sem link válido")
                
                # Pequena pausa entre canais
                time.sleep(2)
            
            # Criar arquivo M3U
            if channels_with_links:
                self.create_m3u_file(channels_with_links)
            
            # Relatório final
            print(f"\n" + "="*50)
            print(f"PROCESSAMENTO CONCLUÍDO - TELEARG (ATUALIZADO)")
            print(f"="*50)
            print(f"Total de canais processados: {processed_count}")
            print(f"Total de links M3U8 encontrados: {found_m3u8_count}")
            print(f"Taxa de sucesso: {(found_m3u8_count/processed_count)*100:.1f}%")
            print(f"Arquivo M3U gerado: {self.output_filename}")
            
            # Salvar relatório detalhado
            self.save_detailed_report(channels_with_links, processed_count, found_m3u8_count)
            
        except Exception as e:
            print(f"Erro crítico no processamento: {e}")
        finally:
            if self.driver:
                print("Fechando o WebDriver...")
                self.driver.quit()
                print("Script finalizado.")
    
    def save_detailed_report(self, channels_with_links, processed_count, found_m3u8_count):
        """Salva um relatório detalhado do processamento"""
        report_filename = "telearg_updated_extraction_report.txt"
        
        with open(report_filename, "w", encoding='utf-8') as report_file:
            report_file.write("RELATÓRIO DE EXTRAÇÃO - TELEARG (ATUALIZADO)\n")
            report_file.write("="*50 + "\n\n")
            report_file.write(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            report_file.write(f"Total de canais processados: {processed_count}\n")
            report_file.write(f"Total de links M3U8 encontrados: {found_m3u8_count}\n")
            report_file.write(f"Taxa de sucesso: {(found_m3u8_count/processed_count)*100:.1f}%\n\n")
            
            report_file.write("CANAIS COM LINKS FUNCIONAIS:\n")
            report_file.write("-"*30 + "\n")
            
            for i, channel in enumerate(channels_with_links, 1):
                report_file.write(f"{i}. {channel['title']}\n")
                report_file.write(f"   URL: {channel['url']}\n")
                report_file.write(f"   M3U8: {channel['m3u8_url']}\n")
                report_file.write(f"   Logo: {channel.get('logo', 'N/A')}\n\n")
        
        print(f"Relatório detalhado salvo: {report_filename}")

def main():
    """Função principal"""
    extractor = TeleArgExtractorUpdated()
    extractor.run()

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Script para extrair links de IPTV do site 5900.tv
Adaptado para funcionar com players do Twitch embarcados
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import re
import json

print("Iniciando o script de extração do 5900.tv...")

class FiveNineHundredTVExtractor:
    def __init__(self):
        self.main_url = "https://www.5900.tv/category/vivo/television/"
        self.output_filename = "lista_5900tv.m3u"
        self.channels_info = []
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o WebDriver com as especificações do usuário"""
        print("Configurando o WebDriver...")
        
        # Configurações do Chrome conforme especificado pelo usuário
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-infobars")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("WebDriver configurado com sucesso.")
        except Exception as e:
            print(f"Erro ao configurar o WebDriver: {e}")
            raise
    
    def extract_channels_from_main_page(self):
        """Extrai lista de canais da página principal"""
        print(f"Acessando a URL principal: {self.main_url}")
        self.driver.get(self.main_url)
        
        # Aguardar carregamento da página
        wait_time = 15
        print(f"Aguardando {wait_time} segundos para carregamento...")
        WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Scroll para carregar todo o conteúdo
        print("Fazendo scroll para carregar todos os canais...")
        self.scroll_to_load_content()
        
        # Extrair canais usando JavaScript
        print("Extraindo lista de canais...")
        channels_data = self.extract_channels_with_js()
        
        print(f"Encontrados {len(channels_data)} canais válidos")
        return channels_data
    
    def scroll_to_load_content(self):
        """Faz scroll na página para carregar todo o conteúdo"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(3):  # Máximo 3 scrolls
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def extract_channels_with_js(self):
        """Extrai canais usando JavaScript"""
        js_script = """
        (() => {
            const channels = [];
            
            // Buscar todos os links de canais na seção de televisión
            const channelElements = document.querySelectorAll('a[href*="5900.tv"]');
            
            channelElements.forEach((element, index) => {
                const href = element.href;
                const img = element.querySelector('img');
                let title = '';
                let logo = '';
                
                // Extrair título e logo
                if (img) {
                    title = img.alt || '';
                    logo = img.src || '';
                }
                
                // Se não tem título do alt, tentar pegar do texto do link
                if (!title) {
                    const textContent = element.textContent.trim();
                    if (textContent && textContent.length > 0) {
                        title = textContent;
                    }
                }
                
                // Filtrar apenas links de canais válidos (não categorias)
                const isChannelPage = href.includes('5900.tv/') && 
                                    !href.includes('/category/') && 
                                    !href.includes('/tag/') &&
                                    href !== 'https://www.5900.tv/' &&
                                    title.length > 0;
                
                if (isChannelPage && title) {
                    channels.push({
                        title: title.trim(),
                        url: href,
                        logo: logo
                    });
                }
            });
            
            // Remover duplicatas baseado na URL
            const uniqueChannels = [];
            const seenUrls = new Set();
            
            channels.forEach(channel => {
                if (!seenUrls.has(channel.url)) {
                    seenUrls.add(channel.url);
                    uniqueChannels.push(channel);
                }
            });
            
            return uniqueChannels;
        })();
        """
        
        try:
            return self.driver.execute_script(js_script)
        except Exception as e:
            print(f"Erro ao extrair canais: {e}")
            return []
    
    def extract_twitch_channel_from_page(self, channel_url, channel_title):
        """Extrai o canal do Twitch de uma página específica"""
        print(f"  Processando: {channel_title}")
        print(f"  URL: {channel_url}")
        
        try:
            self.driver.get(channel_url)
            time.sleep(10)  # Aguardar carregamento
            
            # Procurar por iframe do Twitch
            print("  Procurando player do Twitch...")
            
            js_script = """
            (() => {
                const iframes = document.querySelectorAll('iframe');
                const twitchData = [];
                
                iframes.forEach(iframe => {
                    const src = iframe.src;
                    if (src && src.includes('twitch.tv')) {
                        // Extrair nome do canal do Twitch
                        const urlParams = new URLSearchParams(src.split('?')[1]);
                        const channel = urlParams.get('channel');
                        
                        if (channel) {
                            twitchData.push({
                                twitchChannel: channel,
                                embedUrl: src,
                                streamUrl: `https://www.twitch.tv/${channel}`
                            });
                        }
                    }
                });
                
                return twitchData;
            })();
            """
            
            twitch_data = self.driver.execute_script(js_script)
            
            if twitch_data and len(twitch_data) > 0:
                twitch_info = twitch_data[0]
                print(f"    ✓ Canal Twitch encontrado: {twitch_info['twitchChannel']}")
                return twitch_info
            else:
                print(f"    ✗ Nenhum player Twitch encontrado")
                return None
                
        except Exception as e:
            print(f"  Erro ao processar {channel_title}: {e}")
            return None
    
    def convert_twitch_to_m3u8(self, twitch_channel):
        """Converte canal do Twitch para URL M3U8 (se possível)"""
        # Nota: Twitch usa URLs M3U8 dinâmicas que requerem autenticação
        # Esta é uma aproximação - URLs reais podem variar
        try:
            # URL base para streams do Twitch (pode não funcionar sem autenticação)
            m3u8_url = f"https://usher.ttvnw.net/api/channel/hls/{twitch_channel}.m3u8"
            
            # Verificar se a URL responde (provavelmente falhará sem token)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            try:
                response = requests.head(m3u8_url, timeout=5, headers=headers)
                if response.status_code == 200:
                    return m3u8_url
            except:
                pass
            
            # Retornar URL do Twitch como fallback
            return f"https://www.twitch.tv/{twitch_channel}"
            
        except Exception as e:
            print(f"    Erro na conversão: {e}")
            return f"https://www.twitch.tv/{twitch_channel}"
    
    def create_m3u_file(self, channels_with_links):
        """Cria o arquivo M3U com os canais encontrados"""
        print(f"\nCriando arquivo M3U: {self.output_filename}")
        
        with open(self.output_filename, "w", encoding='utf-8') as output_file:
            output_file.write("#EXTM3U\n")
            
            for channel in channels_with_links:
                clean_title = channel['title'].replace('\n', ' ').replace('\r', '').strip()
                logo_url = channel.get('logo', '')
                stream_url = channel['stream_url']
                
                # Adicionar informação do Twitch se disponível
                if 'twitch_channel' in channel:
                    group_title = f"5900TV-Twitch"
                    clean_title = f"{clean_title} (Twitch: {channel['twitch_channel']})"
                else:
                    group_title = "5900TV"
                
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="{group_title}",{clean_title}\n')
                output_file.write(f"{stream_url}\n")
        
        print(f"Arquivo M3U criado com sucesso!")
    
    def run(self):
        """Executa o processo completo de extração"""
        try:
            # Extrair lista de canais
            self.channels_info = self.extract_channels_from_main_page()
            
            if not self.channels_info:
                print("Nenhum canal encontrado. Encerrando.")
                return
            
            print(f"\nTotal de {len(self.channels_info)} canais para processar")
            
            # Processar cada canal
            processed_count = 0
            found_streams_count = 0
            channels_with_links = []
            
            for i, channel in enumerate(self.channels_info):
                print(f"\n[{i+1}/{len(self.channels_info)}] Processando: {channel['title']}")
                
                twitch_info = self.extract_twitch_channel_from_page(channel['url'], channel['title'])
                processed_count += 1
                
                if twitch_info:
                    found_streams_count += 1
                    
                    # Tentar converter para M3U8 ou usar URL do Twitch
                    stream_url = self.convert_twitch_to_m3u8(twitch_info['twitchChannel'])
                    
                    channel['stream_url'] = stream_url
                    channel['twitch_channel'] = twitch_info['twitchChannel']
                    channel['embed_url'] = twitch_info['embedUrl']
                    
                    channels_with_links.append(channel)
                    print(f"  ✓ Stream encontrado")
                else:
                    print(f"  ✗ Canal sem stream válido")
                
                # Pequena pausa entre canais
                time.sleep(2)
            
            # Criar arquivo M3U
            if channels_with_links:
                self.create_m3u_file(channels_with_links)
            
            # Relatório final
            print(f"\n" + "="*50)
            print(f"PROCESSAMENTO CONCLUÍDO - 5900.TV")
            print(f"="*50)
            print(f"Total de canais processados: {processed_count}")
            print(f"Total de streams encontrados: {found_streams_count}")
            print(f"Taxa de sucesso: {(found_streams_count/processed_count)*100:.1f}%")
            print(f"Arquivo M3U gerado: {self.output_filename}")
            
            # Salvar relatório detalhado
            self.save_detailed_report(channels_with_links, processed_count, found_streams_count)
            
        except Exception as e:
            print(f"Erro crítico no processamento: {e}")
        finally:
            if self.driver:
                print("Fechando o WebDriver...")
                self.driver.quit()
                print("Script finalizado.")
    
    def save_detailed_report(self, channels_with_links, processed_count, found_streams_count):
        """Salva um relatório detalhado do processamento"""
        report_filename = "5900tv_extraction_report.txt"
        
        with open(report_filename, "w", encoding='utf-8') as report_file:
            report_file.write("RELATÓRIO DE EXTRAÇÃO - 5900.TV\n")
            report_file.write("="*40 + "\n\n")
            report_file.write(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            report_file.write(f"Total de canais processados: {processed_count}\n")
            report_file.write(f"Total de streams encontrados: {found_streams_count}\n")
            report_file.write(f"Taxa de sucesso: {(found_streams_count/processed_count)*100:.1f}%\n\n")
            
            report_file.write("CANAIS COM STREAMS FUNCIONAIS:\n")
            report_file.write("-"*30 + "\n")
            
            for i, channel in enumerate(channels_with_links, 1):
                report_file.write(f"{i}. {channel['title']}\n")
                report_file.write(f"   URL: {channel['url']}\n")
                report_file.write(f"   Stream: {channel['stream_url']}\n")
                if 'twitch_channel' in channel:
                    report_file.write(f"   Twitch: {channel['twitch_channel']}\n")
                report_file.write(f"   Logo: {channel.get('logo', 'N/A')}\n\n")
        
        print(f"Relatório detalhado salvo: {report_filename}")

def main():
    """Função principal"""
    extractor = FiveNineHundredTVExtractor()
    extractor.run()

if __name__ == "__main__":
    main()







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
