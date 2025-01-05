import os
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configurações do Chrome
options = webdriver.ChromeOptions()
download_dir = "C:/Users/0167814/Downloads"
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)

# Inicializando o WebDriver
service = Service('C:/Users/0167814/OneDrive - Thomson Reuters Incorporated/Documents/selenium/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

try:
    # Acessando o site
    driver.get("https://www.doe.sp.gov.br/sumario")

    # Clicando no botão "Executivo"
    executive_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Executivo')]"))
    )
    executive_button.click()
    print("Botão Executivo clicado")
    time.sleep(2)  # Espera para carregar

    # Clicando no botão "1 Atos Normativos"
    atos_normativos_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Atos Normativos')]"))
    )
    atos_normativos_button.click()
    print("Botão 1 Atos Normativos clicado")
    time.sleep(2)  # Espera para carregar

    # Clicando no botão "Diário completo certificado" e obtendo o link
    diario_completo_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Diário completo certificado']"))
    )
    diario_completo_button.click()
    print("Botão Diário completo certificado clicado")
    
    # Aguardar o carregamento e capturar o link do PDF
    pdf_link = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.pdf')]"))
    ).get_attribute("href")

    if pdf_link:
        print(f"Link do PDF capturado: {pdf_link}")
        driver.quit()

        # Tentando baixar o PDF usando requests
        response = requests.get(pdf_link)
        if response.status_code == 200:
            date_obj = datetime.now()
            file_name = f"doesp_exec1_{date_obj.strftime('%Y%m%d')}.pdf"
            file_path = os.path.join(download_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"PDF baixado com sucesso: {file_path}")
        else:
            print(f"Erro ao tentar baixar o PDF. Status code: {response.status_code}")
    else:
        print("Não foi possível capturar o link do PDF.")

except TimeoutException:
    print("Tempo esgotado para carregar algum elemento da página.")
finally:
    driver.quit()
