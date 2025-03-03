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
driver_path = '/path/to/chromedriver'

# Inicializa o driver
driver = webdriver.Chrome(executable_path=driver_path, options=options)

# Acessa o site
driver.get("https://www.google.com/search?q=vivo+site%3Aglobo.com&sca_esv=35aba76f9e0fd39c&udm=7&biw=1912&bih=954&ei=OZjFZ9rXDObb1sQP7rSP4Ak&ved=0ahUKEwia2Pvv7O2LAxXmrZUCHW7aA5wQ4dUDCBE&uact=5&oq=vivo+site%3Aglobo.com&gs_lp=EhZnd3Mtd2l6LW1vZGVsZXNzLXZpZGVvIhN2aXZvIHNpdGU6Z2xvYm8uY29tSM0CUABY0AFwAHgBkAEAmAFtoAHXAaoBAzAuMrgBA8gBAPgBAZgCAKACAJgDAJIHAKAHlgE&sclient=gws-wiz-modeless-video#ip=1")

# Espera a página carregar completamente
time.sleep(3)

# Localiza todos os elementos de interesse que possuem o link para o Globoplay
elements = driver.find_elements(By.XPATH, "//div[@jsname='pKB8Bc']//a[@jsname='UWckNb']")

# Interage com os elementos encontrados
for element in elements:
    link = element.get_attribute("href")
    print(f"Link encontrado: {link}")
    
    # Aqui você pode incluir qualquer outra ação, como clicar no link, etc.
    # Exemplo de clique no link:
    # element.click()
    
    time.sleep(2)  # Espera entre as interações

# Fecha o navegador
driver.quit()
