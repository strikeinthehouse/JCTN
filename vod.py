import gdown

# ID do arquivo no Google Drive
file_id = "1CoeZEj20zmtuQPqkCzv2UQq7SsDSlTyd"
url = f"https://drive.google.com/uc?id={file_id}"

# Nome do arquivo de saída
output = "lista.m3u"

# Baixando o arquivo
gdown.download(url, output, quiet=False)

print(f"Download concluído: {output}")



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
    "https://tvmi.mt/bigbrother",  # Título não encontrado
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/bom-dia-cidade-ribeirao-preto.ghtml",
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/eptv1.ghtml",
    "https://g1.globo.com/sp/ribeirao-preto-franca/ao-vivo/eptv-2-ribeirao-e-franca-ao-vivo.ghtml",
    "https://g1.globo.com/pe/petrolina-regiao/ao-vivo/ao-vivo-assista-ao-gr2.ghtml",
    "https://g1.globo.com/ap/ao-vivo/assista-ao-bdap-desta-sexta-feira-7.ghtml",
    "https://globoplay.globo.com/v/1467373/",
    "https://globoplay.globo.com/v/4064559/",  # G1 ao vivo. g1 ao vivo: Transmissão ao vivo
    "https://g1.globo.com/ba/bahia/ao-vivo/assista-aos-telejornais-da-tv-bahia.ghtml",  # Título não encontrado
    "https://g1.globo.com/pe/caruaru-regiao/video/transmissao-ao-vivo-do-abtv-5472979.ghtml",
    "https://globoplay.globo.com/v/2135579/",  # G1 RS. Assista aos telejornais da RBS TV
    "https://globoplay.globo.com/v/6120663/",  # Título não encontrado
    "https://globoplay.globo.com/v/2145544/",  # G1 SC. AO VIVO: Assista aos telejornais da NSC TV
    "https://globoplay.globo.com/v/4039160/",  # G1 CE. Assista à TV Verdes Mares ao vivo
    "https://globoplay.globo.com/v/6329086/",  # Globo Esporte BA. AO VIVO: Travessia Itaparica-Salvador ao vivo e de graça no ge
    "https://globoplay.globo.com/v/11999480/",  # G1 ES. Transmissão ao vivo do jornal Regional no g1 ES
    "https://g1.globo.com/al/alagoas/ao-vivo/assista-aos-telejornais-da-tv-gazeta-de-alagoas.ghtml",  # Título não encontrado
    "https://globoplay.globo.com/ao-vivo/3667427/",  # Título não encontrado
    "https://globoplay.globo.com/v/4218681/",  # G1 Triângulo Mineiro. Transmissão ao vivo
    "https://globoplay.globo.com/v/12945385/",
    "https://globoplay.globo.com/v/3065772/",  # G1 MS. Transmissão ao vivo em MS
    "https://globoplay.globo.com/v/2923579/",  # G1 AP. Assista ao vivo aos telejornais da Rede Amazônica
    "https://g1.globo.com/am/amazonas/ao-vivo/assista-aos-telejornais-da-rede-amazonica.ghtml",  # Título não encontrado
    "https://globoplay.globo.com/v/2923546/",  # G1 AC. Assista aos jornais da Rede Amazônica
    "https://globoplay.globo.com/v/2168377/",  # Assista aos telejornais da TV Liberal
    "https://globoplay.globo.com/v/992055/",  # G1 ao vivo. g1 ao vivo: Transmissão ao vivo
    "https://globoplay.globo.com/v/602497/",  # ge.globo. Transmissão ao vivo
    "https://globoplay.globo.com/v/8713568/",  # Globo Esporte RS. Gauchão ao vivo
    "https://globoplay.globo.com/v/10747444/",  # CBN. CBN SP
    "https://globoplay.globo.com/v/10740500/",  # CBN. CBN RJ
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
