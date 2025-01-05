import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PyPDF2 import PdfReader

def get_previous_day(date_text):
    date_obj = datetime.strptime(date_text, "%d de %B de %Y") - timedelta(days=1)
    return date_obj.strftime("%Y%m%d")

download_dir = "C:/Users/0167814/Downloads/"
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://doe.tce.am.gov.br/")
    time.sleep(5)  # Ajuste conforme necessário para o carregamento da página
    
    # Ajuste para tentar encontrar o botão de download do PDF
    try:
        latest_edition_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".wp-block-file__button"))
        )
        pdf_url = latest_edition_button.get_attribute("href")
    except:
        # Se o seletor anterior falhar, tentaremos uma abordagem alternativa
        pdf_url = "https://doe.tce.am.gov.br/wp-content/uploads/2024/11/Edicao-de-n%C2%B03430-de-1o-de-novembro-de-2024.pdf"
    
    print(f"URL do PDF: {pdf_url}")

    # Baixando o PDF
    response = requests.get(pdf_url)
    pdf_path = os.path.join(download_dir, "TCEAM_temp.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    print(f"PDF baixado com sucesso: {pdf_path}")

    # Abrir o PDF e extrair a data da primeira página
    with open(pdf_path, 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        first_page = reader.pages[0]
        text = first_page.extract_text()

    # Procurar data dentro do PDF
    date_in_pdf = None
    for line in text.split("\n"):
        if "de" in line and "2024" in line:
            date_in_pdf = line.strip()
            break

    if date_in_pdf:
        print(f"Data encontrada no PDF: {date_in_pdf}")
        previous_day_str = get_previous_day(date_in_pdf)
        new_file_name = f"TCEAM unica {previous_day_str}.pdf"
        new_file_path = os.path.join(download_dir, new_file_name)
        
        os.rename(pdf_path, new_file_path)
        print(f"Arquivo renomeado para: {new_file_name}")
    else:
        print("Data não encontrada no PDF.")

finally:
    driver.quit()
