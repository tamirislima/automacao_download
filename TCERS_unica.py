from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import requests
from datetime import datetime

# Função para obter o diretório de downloads padrão
def get_download_folder():
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:  # MacOS ou Linux
        return os.path.join(os.path.expanduser('~'), 'Downloads')

# Função para automatizar o download
def download_tcers_pdf():
    # Data do dia
    today = datetime.today().strftime("%d/%m/%Y")
    today_filename = datetime.today().strftime("%Y%m%d")
    
    # Diretório de downloads
    download_dir = get_download_folder()
    
    # Configuração do Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Abrir o site
        driver.get("https://portalnovo.tce.rs.gov.br/diario-eletronico/")
        
        # Localizar a seção com a data do dia
        date_section = driver.find_element(By.XPATH, f"//p[contains(text(), 'Edições disponibilizadas em {today}')]")
        
        # Localizar o primeiro link de PDF após a data
        pdf_link = date_section.find_element(By.XPATH, "./following::a[contains(@href, '.pdf')]")
        pdf_url = pdf_link.get_attribute("href")
        
        # Nome do arquivo final
        output_filename = f"TCERS unica {today_filename}.pdf"
        output_path = os.path.join(download_dir, output_filename)
        
        # Baixar o PDF
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                file.write(response.content)
            print(f"Arquivo baixado e salvo como {output_path}")
        else:
            print(f"Erro ao baixar o PDF. Status: {response.status_code}")
    
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    
    finally:
        driver.quit()

# Executar a função
download_tcers_pdf()
