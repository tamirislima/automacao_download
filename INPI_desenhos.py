import os
import re
import time
import requests
from bs4 import BeautifulSoup
import pdfplumber
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Caminho para o Chromedriver
chromedriver_path = 'C:/Users/0167814/OneDrive - Thomson Reuters Incorporated/Documents/selenium/chromedriver.exe'  # Atualize este caminho

# Configuração do Selenium
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": "C:/Users/0167814/Downloads",  # Substitua pelo caminho correto no seu sistema
    "plugins.always_open_pdf_externally": True,
    "download.prompt_for_download": False
})
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Navegando para a página de Desenhos Industriais...")
    driver.get('https://revistas.inpi.gov.br/rpi/')

    print("Aguardando o carregamento da página...")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))

    print("Clicando no botão 'Concordar e Fechar', se necessário...")
    try:
        concordar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Concordar e Fechar')]"))
        )
        concordar_btn.click()
        print("Botão 'Concordar e Fechar' clicado.")
    except:
        print("Botão 'Concordar e Fechar' não encontrado ou não era necessário.")

    print("Encontrando o link mais recente para 'Seção III Desenhos Industriais'...")
    # Encontrar todos os links que contêm "Desenhos Industriais"
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Desenhos_Industriais') and contains(text(), 'PDF')]")

    if links:
        # Ordenar os links com base no texto do link para garantir que o mais recente seja encontrado
        sorted_links = sorted(links, key=lambda x: x.get_attribute('href'), reverse=True)
        latest_link = sorted_links[0].get_attribute('href')

        print(f"Baixando o PDF mais recente para 'Seção III Desenhos Industriais': {latest_link}")
        response = requests.get(latest_link)
        pdf_path = "C:/Users/0167814/Downloads/temp.pdf"  # Caminho temporário para o PDF baixado

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        print("PDF baixado com sucesso.")

        # Função para extrair a data do PDF
        def extrair_data_pdf(caminho_pdf):
            with pdfplumber.open(caminho_pdf) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    # Procurar a data no formato "03 de Setembro de 2024"
                    match = re.search(r"(\d{2}) de ([\w\-]+) de (\d{4})", texto)
                    if match:
                        dia, mes_nome, ano = match.groups()
                        # Mapeamento de meses para números
                        meses = {
                            "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                            "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                            "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
                        }
                        mes = meses[mes_nome.lower()]
                        data_formatada = f"{ano}{mes}{dia}"  # Formato YYYYMMDD
                        return data_formatada
            return None

        # Extrair a data do PDF
        data_pdf = extrair_data_pdf(pdf_path)
        if data_pdf:
            novo_nome = f"dorpidesind {data_pdf}.pdf"
            novo_caminho = os.path.join("C:/Users/0167814/Downloads", novo_nome)
            os.rename(pdf_path, novo_caminho)
            print(f"PDF renomeado para: {novo_nome}")
        else:
            print("Data de disponibilização não encontrada no PDF.")
    else:
        print("Nenhum link para 'Seção III Desenhos Industriais' encontrado.")

finally:
    print("Fechando o navegador após as ações...")
    time.sleep(10)  # Adiciona mais tempo para observar a saída
    driver.quit()
