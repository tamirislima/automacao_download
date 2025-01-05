#driver = webdriver.Chrome(executable_path=r"C:\Users\0167814\OneDrive - Thomson Reuters Incorporated\Documents\selenium")

#driver = selenium.Firefox(executable_path=r"C:\Users\gusta\Documents\driver\....exe)

#driver.get("https://www.google.com.br")



#from selenium import webdriver
#from selenium.webdriver.chrome.service import Service

# Caminho para o novo executável do driver
#chrome_driver_path = r"C:\Users\0167814\OneDrive - Thomson Reuters Incorporated\Documents\selenium\chromedriver.exe"

# Crie um objeto Service
#service = Service(executable_path=chrome_driver_path)

# Inicialize o driver do Chrome com o objeto Service
#driver = webdriver.Chrome(service=service)

#driver.get("https://www.google.com.br")

from selenium import webdriver
import time

# Configurando o ChromeOptions para evitar erros de políticas de permissões
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-permissions-api")

# Inicializando o webdriver
driver = webdriver.Chrome(options=chrome_options)

# Navegando até a URL desejada
driver.get("https://www.google.com.br")

# Adicionando um delay para manter o navegador aberto por um tempo
time.sleep(120)  # Espera 120 segundos

# Fechando o navegador
driver.quit()