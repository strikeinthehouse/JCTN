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

# Caminho do driver do Chrome
driver = webdriver.Chrome(options=options)

# Acessa o site
driver.get("https://www.google.com/search?q=vivo+site%3Aglobo.com&sca_esv=35aba76f9e0fd39c&udm=7&biw=1912&bih=954&ei=OZjFZ9rXDObb1sQP7rSP4Ak&ved=0ahUKEwia2Pvv7O2LAxXmrZUCHW7aA5wQ4dUDCBE&uact=5&oq=vivo+site%3Aglobo.com&gs_lp=EhZnd3Mtd2l6LW1vZGVsZXNzLXZpZGVvIhN2aXZvIHNpdGU6Z2xvYm8uY29tSM0CUABY0AFwAHgBkAEAmAFtoAHXAaoBAzAuMrgBA8gBAPgBAZgCAKACAJgDAJIHAKAHlgE&sclient=gws-wiz-modeless-video#ip=1")

# Espera a página carregar completamente
time.sleep(3)

# Localiza todos os elementos de interesse com links para o Globoplay
elements = driver.find_elements(By.XPATH, "//div[@class='g']//a")

# Itera sobre os elementos e verifica se eles contêm ou não a duração
for element in elements:
    link = element.get_attribute("href")
    
    if link and "globoplay.globo.com" in link:
        # Verifica se o link tem a duração associada, como no exemplo "<div class='kSFuOd rkqHyd'>"
        try:
            duration_element = element.find_element(By.XPATH, ".//ancestor::div[contains(@class, 'g')]//div[@class='kSFuOd rkqHyd']")
            # Se encontramos a duração, ignoramos esse link
            if duration_element:
                continue  # Ignora o link com duração
        except:
            # Se não encontrar o elemento de duração, não faz nada
            pass

        # Se não houver duração, exibe o link
        print(f"Link encontrado: {link}")

# Fecha o navegador
driver.quit()
