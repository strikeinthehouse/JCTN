from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome options
options = Options()
options.add_argument("--headless")  # Uncomment if you don't need a GUI
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")

# Create the webdriver instance
driver = webdriver.Chrome(options=options)

try:
    driver.get(base_url)

    # Esperar até que os elementos de vídeo carreguem
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tile--vid"))
    )

    video_elements = driver.find_elements(By.CSS_SELECTOR, "div.tile--vid")
    video_links = []
    video_titles = []

    for video in video_elements:
        try:
            link_element = video.find_element(By.CSS_SELECTOR, "h6.tile__title a")
            link = link_element.get_attribute("href")
            title = link_element.text
            video_links.append(link)
            video_titles.append(title)
        except Exception as e:
            print(f"Erro ao extrair informações do vídeo: {e}")

    if video_links:
        print("Links encontrados:")
        with open("links_video.txt", "w") as file:
            for title, link in zip(video_titles, video_links):
                print(f"Título: {title}, Link: {link}")
                file.write(f"{title}\n{link}\n")
    else:
        print("Nenhum link encontrado.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
    
# Function to extract m3u8 URL and title from a video page
def extract_m3u8_url_and_title(driver, url):
    driver.get(url)
    time.sleep(10)  # Wait for the page to fully load
    
    # Get the page title
    title = driver.title
    try:
        # Wait for the play button to be clickable
        play_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.poster__play-wrapper"))
        )
        play_button.click()  # Click the play button
        time.sleep(15)  # Wait for the video to start playing
    except Exception as e:
        print("Erro ao clicar no botão de reprodução:", e)
    
    # Get the m3u8 link
    log_entries = driver.execute_script("return window.performance.getEntriesByType('resource');")
    m3u8_url = None
    logo_url = None
    for entry in log_entries:
        if ".m3u8" in entry['name']:
            m3u8_url = entry['name']
        if ".jpg" in entry['name']:
            logo_url = entry['name']
    
    return title, m3u8_url, logo_url


# Open the file containing the video links
with open("links_video.txt", "r") as file:
    lines = file.readlines()

# Create or append to the m3u file
with open("lista1.m3u", "a") as output_file:
    for i in range(0, len(lines), 2):  # Video title and link are stored in pairs
        title = lines[i].strip()
        link = lines[i+1].strip()
        
        if not link:
            continue
        
        print(f"Processando link: {link}")
        
        try:
            title, m3u8_url, logo_url = extract_m3u8_url_and_title(driver, link)
            if m3u8_url:
                # Write in IPTV format
                output_file.write(f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="GLOBO AO VIVO", {title}\n')
                output_file.write(f"{m3u8_url}\n")
                print(f"M3U8 link encontrado: {m3u8_url}")
            else:
                print(f"Link .m3u8 não encontrado para {link}")
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Close the driver after completion
driver.quit()






