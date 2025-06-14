from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import concurrent.futures
import os
import re

# Configurações do Chrome
options = Options()
options.add_argument("--headless")  # Executa sem interface gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")
options.add_argument("--disable-web-security")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# URLs dos vídeos ABC News
abcnews_urls = [
    "https://abcnews.go.com/live/video/special-live-01/",
    "https://abcnews.go.com/live/video/special-live-02/",
    "https://abcnews.go.com/live/video/special-live-03/",
    "https://abcnews.go.com/live/video/special-live-04/",
    "https://abcnews.go.com/live/video/special-live-05/",
    "https://abcnews.go.com/live/video/special-live-06/",
    "https://abcnews.go.com/live/video/special-live-07/",
    "https://abcnews.go.com/live/video/special-live-08/",
    "https://abcnews.go.com/live/video/special-live-09/",
    "https://abcnews.go.com/live/video/special-live-10/",
    "https://abcnews.go.com/live/video/special-live-11/"
]

def handle_cookie_consent(driver):
    """Trata mensagens de cookies e consentimento"""
    try:
        # Aguarda um pouco para elementos carregarem
        time.sleep(3)
        
        # Possíveis seletores para botões de aceitar cookies
        cookie_selectors = [
            "button[id*='accept']",
            "button[class*='accept']",
            "button[data-testid*='accept']",
            "button:contains('Accept')",
            "button:contains('I Accept')",
            "button:contains('Accept All')",
            "button:contains('Agree')",
            "button:contains('OK')",
            ".cookie-accept",
            ".accept-cookies",
            "#onetrust-accept-btn-handler",
            ".ot-sdk-show-settings",
            "button[aria-label*='Accept']",
            "button[title*='Accept']",
            "button[data-cy*='accept']",
            ".privacy-manager-accept-all",
            ".gdpr-accept",
            ".consent-accept"
        ]
        
        for selector in cookie_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        driver.execute_script("arguments[0].click();", element)
                        print(f"Clicou no botão de cookies: {selector}")
                        time.sleep(2)
                        return True
            except Exception:
                continue
                
        # Tenta fechar modais/overlays genéricos
        close_selectors = [
            "button[aria-label*='close']",
            "button[aria-label*='Close']",
            ".close",
            ".modal-close",
            "button.close",
            "[data-dismiss='modal']",
            ".overlay-close",
            ".popup-close"
        ]
        
        for selector in close_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        driver.execute_script("arguments[0].click();", element)
                        print(f"Fechou modal/overlay: {selector}")
                        time.sleep(1)
                        return True
            except Exception:
                continue
                
    except Exception as e:
        print(f"Erro ao tratar cookies/modals: {e}")
    
    return False

def wait_for_video_load(driver, timeout=30):
    """Aguarda o vídeo carregar completamente"""
    try:
        # Aguarda elementos de vídeo aparecerem
        video_selectors = [
            "video",
            ".video-player",
            ".player-container",
            "[data-testid*='video']",
            ".live-player",
            "iframe[src*='player']",
            "iframe[src*='video']"
        ]
        
        for selector in video_selectors:
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Elemento de vídeo encontrado: {selector}")
                return True
            except TimeoutException:
                continue
                
    except Exception as e:
        print(f"Erro ao aguardar carregamento do vídeo: {e}")
    
    return False

def handle_iframes(driver):
    """Trata iframes que podem conter o player de vídeo"""
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Encontrados {len(iframes)} iframes")
        
        for i, iframe in enumerate(iframes):
            try:
                # Verifica se o iframe pode conter vídeo
                src = iframe.get_attribute("src") or ""
                if any(keyword in src.lower() for keyword in ['player', 'video', 'live', 'stream']):
                    print(f"Iframe {i} parece conter vídeo: {src[:100]}...")
                    
                    # Muda para o iframe
                    driver.switch_to.frame(iframe)
                    
                    # Procura por elementos de vídeo dentro do iframe
                    video_elements = driver.find_elements(By.TAG_NAME, "video")
                    if video_elements:
                        print(f"Encontrados {len(video_elements)} elementos de vídeo no iframe {i}")
                        
                        # Tenta dar play
                        for video in video_elements:
                            try:
                                driver.execute_script("arguments[0].play();", video)
                                print(f"Play executado no vídeo do iframe {i}")
                            except Exception:
                                pass
                    
                    # Volta para o contexto principal
                    driver.switch_to.default_content()
                    
            except Exception as e:
                print(f"Erro ao processar iframe {i}: {e}")
                # Garante que volta para o contexto principal
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass
                    
    except Exception as e:
        print(f"Erro ao tratar iframes: {e}")

def try_play_video(driver):
    """Tenta dar play no vídeo, priorizando botão vjs-big-play-button"""
    try:
        time.sleep(3)

        # 1. Prioriza o botão vjs-big-play-button
        try:
            play_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.vjs-big-play-button"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", play_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", play_btn)
            print("Clicou no botão vjs-big-play-button")
            time.sleep(3)
            return True
        except TimeoutException:
            print("Botão vjs-big-play-button não encontrado ou não clicável.")

        # 2. Se não funcionou, tenta outros botões de play
        play_selectors = [
            "button[aria-label*='play']",
            "button[aria-label*='Play']",
            "button[title*='play']",
            "button[title*='Play']",
            "button.play-button",
            ".play-btn",
            ".video-play-button",
            "button[data-testid*='play']",
            ".player-play-button",
            "button.vjs-big-play-button",
            ".vjs-play-control",
            "button[class*='play']",
            "div[class*='play'][role='button']",
            ".poster__play-wrapper",
            "button[aria-label='Reproduzir vídeo']",
            ".playkit-pre-playback-play-button",
            "button.playkit-control-button",
            ".play-overlay",
            ".play-icon"
        ]

        for selector in play_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", element)
                        print(f"Clicou no botão de play: {selector}")
                        time.sleep(3)
                        return True
            except Exception:
                continue

        # 3. Tenta clicar diretamente no <video>
        try:
            video_elements = driver.find_elements(By.TAG_NAME, "video")
            for video in video_elements:
                if video.is_displayed():
                    driver.execute_script("arguments[0].click();", video)
                    print("Clicou diretamente no elemento <video>")
                    time.sleep(3)
                    return True
        except Exception as e:
            print(f"Erro ao clicar no vídeo: {e}")

        # 4. Tenta dar play via JavaScript
        try:
            driver.execute_script("""
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    if (videos[i].paused) {
                        videos[i].play();
                        console.log('Play via JavaScript no vídeo', i);
                    }
                }
            """)
            print("Tentou dar play via JavaScript")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Erro ao dar play via JavaScript: {e}")

    except Exception as e:
        print(f"Erro geral ao tentar dar play: {e}")

    return False


def extract_m3u8_from_network(driver):
    """Extrai URLs .m3u8 dos logs de rede"""
    try:
        # Obtém logs de performance/rede
        log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
        
        m3u8_urls = []
        for entry in log_entries:
            url = entry.get('name', '')
            if '.m3u8' in url:
                m3u8_urls.append(url)
        
        # Remove duplicatas e retorna a melhor URL
        m3u8_urls = list(set(m3u8_urls))
        
        # Prioriza URLs que parecem ser de melhor qualidade
        for url in m3u8_urls:
            if any(quality in url.lower() for quality in ['master', 'playlist', 'index']):
                return url
                
        # Se não encontrou URL prioritária, retorna a primeira
        if m3u8_urls:
            return m3u8_urls[0]
            
    except Exception as e:
        print(f"Erro ao extrair m3u8 dos logs de rede: {e}")
    
    return None

def extract_m3u8_from_source(driver):
    """Extrai URLs .m3u8 do código fonte da página"""
    try:
        page_source = driver.page_source
        
        # Padrões regex para encontrar URLs .m3u8
        m3u8_patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'"(https?://[^"]+\.m3u8[^"]*)"',
            r"'(https?://[^']+\.m3u8[^']*)'",
            r'src="([^"]+\.m3u8[^"]*)"',
            r"src='([^']+\.m3u8[^']*)'",
            r'url:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
        ]
        
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                # Se o padrão captura grupos, pega o primeiro grupo
                if isinstance(matches[0], tuple):
                    return matches[0][0] if matches[0][0] else matches[0]
                else:
                    return matches[0]
                    
    except Exception as e:
        print(f"Erro ao extrair m3u8 do código fonte: {e}")
    
    return None

def extract_abcnews_data(url):
    """Função principal para extrair dados da ABC News"""
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        
        # Configura user agent para parecer mais com navegador real
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"Acessando: {url}")
        driver.get(url)
        
        # Aguarda carregamento inicial
        time.sleep(5)
        
        # Trata mensagens de cookies/consentimento
        handle_cookie_consent(driver)
        time.sleep(2)
        
        # Aguarda vídeo carregar
        video_loaded = wait_for_video_load(driver)
        if not video_loaded:
            print(f"Vídeo não carregou para {url}")
        
        # Trata iframes que podem conter o player
        handle_iframes(driver)
        time.sleep(3)
        
        # Tenta dar play no vídeo
        play_success = try_play_video(driver)
        if play_success:
            print(f"Play executado com sucesso para {url}")
        else:
            print(f"Não conseguiu dar play para {url}")
        
        # Aguarda um tempo para o stream carregar
        print(f"Aguardando stream carregar para {url}...")
        time.sleep(20)
        
        # Tenta extrair .m3u8 dos logs de rede primeiro
        m3u8_url = extract_m3u8_from_network(driver)
        
        # Se não encontrou nos logs, tenta no código fonte
        if not m3u8_url:
            m3u8_url = extract_m3u8_from_source(driver)
        
        # Aguarda mais um pouco se ainda não encontrou
        if not m3u8_url:
            print(f"Aguardando mais tempo para {url}...")
            time.sleep(30)
            m3u8_url = extract_m3u8_from_network(driver)
            
        if not m3u8_url:
            m3u8_url = extract_m3u8_from_source(driver)
        
        # Coleta informações adicionais
        title = driver.title
        
        # Busca thumbnail
        thumbnail_url = None
        try:
            log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
            for entry in log_entries:
                url_entry = entry.get('name', '')
                if any(ext in url_entry.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']) and any(keyword in url_entry.lower() for keyword in ['thumb', 'preview', 'poster']):
                    thumbnail_url = url_entry
                    break
        except Exception:
            pass
        
        return title, m3u8_url, thumbnail_url
        
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return None, None, None
        
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

# Função para tentar clicar no botão de play (mantida para compatibilidade)
def try_click_play():
    # Esta função foi integrada na função try_play_video
    pass

# Implementação para tentar novamente até 4 vezes se aparecer erro (mantida para compatibilidade)
def retry_on_error(driver, url):
    retry_attempts = 0
    max_retries = 4
    
    while retry_attempts < max_retries:
        try:
            # Verifica se há mensagem de erro e botão "Tentar novamente"
            error_elements = [
                "a[href='javascript:void(0)'][class*='retry']",
                "a:contains('Tentar novamente')",
                ".error-message-container a",
                "a.retry-button",
                "button[class*='retry']",
                "button:contains('Try Again')",
                "button:contains('Retry')"
            ]
            
            retry_button = None
            for selector in error_elements:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if any(keyword in element.text.lower() for keyword in ["tentar novamente", "retry", "try again"]):
                            retry_button = element
                            break
                    if retry_button:
                        break
                except Exception:
                    continue
            
            # Se encontrou botão de retry, clica nele
            if retry_button:
                print(f"Tentativa {retry_attempts + 1}/{max_retries}: Clicando em 'Tentar novamente' para {url}")
                driver.execute_script("arguments[0].click();", retry_button)
                time.sleep(5)
                retry_attempts += 1
            else:
                break
                
        except Exception as e:
            print(f"Erro ao tentar novamente: {e}")
            retry_attempts += 1
            time.sleep(3)

def process_m3u_file(input_url, output_file):
    """Processa arquivo M3U (implementação básica)"""
    pass

def main():
    """Função principal"""
    print("Iniciando extração de streams da ABC News...")
    
    with open("lista_abcnews.m3u", "w", encoding='utf-8') as output_file:
        output_file.write("#EXTM3U\n")
        
        # Processa URLs sequencialmente para evitar sobrecarga
        for url in abcnews_urls:
            try:
                print(f"\n{'='*60}")
                print(f"Processando: {url}")
                print(f"{'='*60}")
                
                title, m3u8_url, thumbnail_url = extract_abcnews_data(url)
                
                if m3u8_url:
                    thumbnail_url = thumbnail_url if thumbnail_url else ""
                    output_file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="ABC NEWS LIVE", {title}\n')
                    output_file.write(f"{m3u8_url}\n")
                    print(f"✅ Sucesso: {url}")
                    print(f"   Título: {title}")
                    print(f"   M3U8: {m3u8_url}")
                else:
                    print(f"❌ M3U8 não encontrado para {url}")
                    
                # Pausa entre requisições
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Erro ao processar {url}: {e}")
    
    print(f"\n{'='*60}")
    print("Processamento concluído! Arquivo salvo como: lista_abcnews.m3u")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()


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
    "https://abcnews.go.com/live/video/special-live-01/",
    "https://abcnews.go.com/live/video/special-live-02/",
    "https://abcnews.go.com/live/video/special-live-03/",
    "https://abcnews.go.com/live/video/special-live-04/",
    "https://abcnews.go.com/live/video/special-live-05/",
    "https://abcnews.go.com/live/video/special-live-06/",
    "https://abcnews.go.com/live/video/special-live-07/",
    "https://abcnews.go.com/live/video/special-live-08/",
    "https://abcnews.go.com/live/video/special-live-09/",
    "https://abcnews.go.com/live/video/special-live-10/",
    "https://abcnews.go.com/live/video/special-live-11/",
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

with open("lista1.m3u", "w") as output_file:
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
