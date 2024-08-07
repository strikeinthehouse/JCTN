import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configuring Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

try:
    # Initialize Chrome webdriver with the configured options
    driver = webdriver.Chrome(options=chrome_options)

    # URL of the Twitch search page
    url_twitch = "https://www.twitch.tv/search?term=GRAN%20HERMANO"

    # Open the desired URL
    driver.get(url_twitch)

    # Wait for the page to load (adjust the sleep time as needed)
    time.sleep(5)

    # Get page source after waiting
    page_source = driver.page_source

    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all search result cards
    cards = soup.find_all('div', class_='InjectLayout-sc-1i43xsx-0 fMQokC search-result-card')

    # Open the file channel_info.txt in append mode
    with open('channel_twitch.txt', 'w', encoding='utf-8') as file:
        # Iterate through the found cards
        for card in cards:
            # Extract channel name
            channel_name = card.find('strong', class_='CoreText-sc-1txzju1-0 fMRfVf').text.strip()
            
            # Extract group name (if available)
            group_name = card.find('p', class_='CoreText-sc-1txzju1-0 exdYde').text.strip()
            
            # Extract logo image URL
            logo_url = card.find('img', class_='search-result-card__img tw-image')['src']
            
            # Extract tvg-id
            tvg_id = card.find('img', class_='search-result-card__img tw-image')['alt']
            
            # Format the output in the desired style
            output_line = f"{channel_name} | Reality Show'S Live | {logo_url}"
            
            # Write to file
            file.write(output_line + " | \n")
            file.write(f"https://www.twitch.tv/{tvg_id}\n\n")   # Write Twitch URL in the next line

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the webdriver regardless of whether there was an exception or not
    if 'driver' in locals():
        driver.quit()
