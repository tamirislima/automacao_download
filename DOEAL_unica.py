from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import datetime
import pandas as pd
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime
import locale  # Adicionado para definir o idioma


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

try:
    # Navegar para o site
    driver.get("https://diario.imprensaoficial.al.gov.br/")
    
    # Esperar até que o botão de busca de edições esteja visível e clicável
    wait = WebDriverWait(driver, 30)
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Ver Edição']")))
    
    # Encontrar o link para a última edição
    pdf_url = search_button.get_attribute("href")
    print(f"URL do PDF: {pdf_url}")

    # Baixar o PDF
    response = requests.get(pdf_url)
    if response.status_code == 200:
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        temp_filename = "temp_arquivo.pdf"
        file_path = os.path.join(download_dir, temp_filename)
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Arquivo salvo em: {file_path}")

        # Verificar se o arquivo foi baixado corretamente
        if os.path.exists(file_path):
            # Abrir o PDF para extrair a data
            doc = fitz.open(file_path)
            first_page_text = doc[0].get_text()
            doc.close()

            # Encontrar a data no formato "22 de Agosto de 2024"
            date_match = re.search(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', first_page_text)
            if date_match:
                date_str = date_match.group(0)
                print(f"Data extraída do PDF: '{date_str}'")
                
                # Definir o local como português
                locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

                try:
                    # Converter a data para o formato YYYYMMDD
                    date_obj = datetime.strptime(date_str, "%d de %B de %Y")
                    new_filename = f"DOEALUnica_{date_obj.strftime('%Y%m%d')}.pdf"
                    new_file_path = os.path.join(download_dir, new_filename)
                    os.rename(file_path, new_file_path)
                    print(f"Arquivo renomeado para: {new_filename}")
                except ValueError as e:
                    print(f"Erro ao converter a data: {e}")
            else:
                print("Erro: Data de disponibilização não encontrada no PDF.")
        else:
            print("Erro: O arquivo não foi baixado corretamente.")
    else:
        print(f"Falha no download. Status code: {response.status_code}")

finally:
    driver.quit()
