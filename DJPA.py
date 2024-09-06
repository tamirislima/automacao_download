from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import datetime
import pandas as pd

# Diretório para salvar o PDF baixado
download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

# Configurando o ChromeOptions para evitar erros de políticas de permissões
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-permissions-api")

# Configurando preferências de download
prefs = {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Inicializando o webdriver
driver = webdriver.Chrome(options=chrome_options)

# Navegando até a URL desejada
driver.get("https://dje.tjpa.jus.br/ClientDJEletronico/app/home.html")

# Esperar até que o link esteja presente
wait = WebDriverWait(driver, 20)
link_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'btn btn-primary') and contains(text(), 'VERSÃO EM PDF')]")))

# Obter o URL do link
pdf_url = link_element.get_attribute("href")
print(f"URL do PDF: {pdf_url}")

# Navegar até o URL do PDF para iniciar o download
driver.get(pdf_url)

# Adicionando um delay para manter o navegador aberto por um tempo (ajuste conforme necessário)
time.sleep(8)  # Espera 8 segundos

# Fechando o navegador
driver.quit()

# Função para obter o dia útil anterior
def get_previous_business_day(date):
    business_day = pd.bdate_range(end=date, periods=2)[0]
    return business_day

# Obter a data atual e o dia útil anterior no formato desejado
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
previous_business_day = get_previous_business_day(current_date).strftime("%Y%m%d")

# Nome do novo arquivo com a data do dia útil anterior
new_filename = f"djpa_Unica_{previous_business_day}.pdf"

# Localizar o arquivo baixado na pasta de downloads
time.sleep(5)  # Espera alguns segundos para garantir que o download foi concluído
files = os.listdir(download_dir)
pdf_files = [f for f in files if f.endswith(".pdf")]

# Se houver apenas um arquivo PDF na pasta de downloads, renomeá-lo
if pdf_files:
    # Presumindo que o arquivo baixado é o mais recente na pasta
    original_file = os.path.join(download_dir, max(pdf_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f))))
    new_file = os.path.join(download_dir, new_filename)
    os.rename(original_file, new_file)
    print(f"Arquivo renomeado para: {new_filename}")
else:
    print("Nenhum arquivo PDF encontrado na pasta de downloads.")