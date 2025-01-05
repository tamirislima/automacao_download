from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from PyPDF2 import PdfReader
from datetime import datetime, timedelta
import os
import re
import requests

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


# Função para calcular a data anterior
def calcular_dia_anterior(data):
    return data - timedelta(days=1)

# Função para extrair a data do PDF
def extrair_data_do_pdf(caminho_pdf):
    try:
        with open(caminho_pdf, 'rb') as f:
            reader = PdfReader(f)
            num_paginas = len(reader.pages)
            texto = ""
            for i in range(min(num_paginas, 2)):  # Limita a leitura às 2 primeiras páginas
                texto += reader.pages[i].extract_text()
            # Procura o padrão de data no formato "21 de Outubro de 2024"
            match = re.search(r'\b(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})\b', texto, re.IGNORECASE)
            if match:
                dia = int(match.group(1))
                mes = match.group(2)
                ano = int(match.group(3))
                meses = {
                    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                }
                return datetime(ano, meses[mes.lower()], dia)
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")
    return None

# URL principal do TCEAL
url_principal = 'https://doe.tceal.tc.br/'

# Caminho para a pasta de downloads
pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')

try:
    # Acessa a página principal
    driver.get(url_principal)
    time.sleep(5)  # Aguarda o carregamento da página

    # Encontra o link do PDF mais recente
    pdf_element = driver.find_element(By.XPATH, "//a[contains(@href, 'api/editions/downloadPdf')]")
    pdf_url = pdf_element.get_attribute('href')

    if pdf_url:
        # Nome temporário do arquivo PDF
        nome_temporario = 'tceal_temp.pdf'
        caminho_arquivo_temp = os.path.join(pasta_download, nome_temporario)

        # Baixa o arquivo PDF
        pdf_response = requests.get(pdf_url)
        if pdf_response.status_code == 200:
            with open(caminho_arquivo_temp, 'wb') as f:
                f.write(pdf_response.content)
            print(f'PDF baixado e salvo como {nome_temporario} na pasta Downloads')

            # Extrai a data do PDF
            data_pdf = extrair_data_do_pdf(caminho_arquivo_temp)
            if data_pdf:
                # Calcula o dia anterior
                data_anterior = calcular_dia_anterior(data_pdf)
                data_formatada = data_anterior.strftime('%Y%m%d')

                # Nome final do arquivo
                nome_final = f'TCEAL_unica_{data_formatada}.pdf'
                caminho_arquivo_final = os.path.join(pasta_download, nome_final)

                # Renomeia o arquivo
                os.rename(caminho_arquivo_temp, caminho_arquivo_final)
                print(f'Arquivo renomeado para {nome_final}')
            else:
                print("Não foi possível extrair a data do PDF.")
                os.remove(caminho_arquivo_temp)  # Remove o arquivo temporário se falhar na leitura
        else:
            print(f'Erro ao baixar o PDF. Status code: {pdf_response.status_code}')
    else:
        print("Não foi possível encontrar o link do PDF mais recente.")
finally:
    driver.quit()
