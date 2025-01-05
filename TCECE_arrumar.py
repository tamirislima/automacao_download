import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do driver e download
download_dir = "C:/Users/0167814/Downloads/"
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

# Ignorar erros de SSL
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-running-insecure-content")

# Iniciar o driver
service = Service('C:/Users/0167814/OneDrive - Thomson Reuters Incorporated/Documents/selenium/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

try:
    # Acessar o site
    driver.get("https://www.tce.ce.gov.br/diario-oficial/consulta-por-data-de-edicao")

    # Esperar até que a página esteja completamente carregada
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Pegar a data do dia útil anterior
    previous_business_day = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")

    # Aguardar e preencher a data
    date_input = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "formConsultaEdicoes:dtConsulta"))
    )
    date_input.clear()
    date_input.send_keys(previous_business_day)

    # Clicar no botão "Visualizar Edição"
    visualize_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, "formUltimasEdicoes:consultaAvancadaDataTable:0:j_idt32"))
    )
    visualize_button.click()

    # Esperar o PDF carregar e baixar
    time.sleep(10)  # Aumente se necessário, dependendo da velocidade da conexão

    # Renomear o arquivo baixado
    download_file = os.path.join(download_dir, "doe.pdf")  # Nome padrão do PDF baixado
    if os.path.exists(download_file):
        new_file_name = f"TCECE Unica {datetime.now().strftime('%Y%m%d')}.pdf"
        new_file_path = os.path.join(download_dir, new_file_name)
        os.rename(download_file, new_file_path)
        print(f"Arquivo baixado e renomeado para: {new_file_name}")
    else:
        print("Arquivo não encontrado!")

finally:
    driver.quit()
