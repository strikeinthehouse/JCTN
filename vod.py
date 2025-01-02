from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import youtube_dl
import concurrent.futures

# Configure Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-infobars")


# Create the webdriver instance
driver = webdriver.Chrome(options=options)

# URL of the desired page
url_archive = "https://archive.org/details/tvarchive?query=trump&sort=-date"

# Open the desired page
driver.get(url_archive)

# Wait for the page to load
time.sleep(5)

# Scroll to the bottom of the page
#for _ in range(1):
#    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#    time.sleep(2)

# Find all elements with the specified <a> tags
elements = driver.find_elements(By.CSS_SELECTOR, 'a[title][data-event-click-tracking="GenericNonCollection|ItemTile"]')

# Create a list to store the video URLs and thumbnails
video_infos = []

# Print the href attributes, thumbnails, and add them to video_infos
for element in elements:
    href = element.get_attribute("href")
    if href:
        # Extract the thumbnail URL
        img_element = element.find_element(By.XPATH, './/img')
        thumbnail_src = img_element.get_attribute('src') if img_element else ''
        # Ensure the thumbnail URL is absolute
        if thumbnail_src and not thumbnail_src.startswith('http'):
            thumbnail_src = 'https://archive.org' + thumbnail_src
        video_infos.append((href, thumbnail_src))
        print("Adicionando URL:", href)
        print("Thumbnail:", thumbnail_src)

# Close the webdriver
driver.quit()


# Function to get the direct stream URL and title with error handling
def get_stream_info(url):
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'noplaylist': True,
        'outtmpl': '/dev/null',
        'geturl': True
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'Video Desconhecido')
            stream_url = info_dict.get('url', '')
            return video_title, stream_url
    except Exception as e:
        print(f"Error fetching info for {url}: {e}")
        return None, None  # Return None for failed entries

# Generate the EXTINF lines with tvg-logo and URLs
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(lambda info: get_stream_info(info[0]), video_infos))

# Write the EXTINF formatted lines to a file
with open('lista1.m3u', 'w') as file:
    file.write('#EXTM3U\n')  # Add the EXT3MU header
    for (url, thumbnail), (title, stream_url) in zip(video_infos, results):
        if stream_url:
            tvg_logo = f'tvg-logo="{thumbnail}"' if thumbnail else ''
            file.write(f'#EXTINF:-1 tvg-group="VOD TRUMP" {tvg_logo},{title}\n{stream_url}\n')

print("A playlist M3U foi gerada com sucesso.")
