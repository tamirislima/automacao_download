from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import fitz  # PyMuPDF
import re
import datetime

# Configurações do WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executar o Chrome em modo headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
service = Service('C:/Users/0167814/OneDrive - Thomson Reuters Incorporated/Documents/selenium/chromedriver.exe')

# Inicializar o WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get('https://dje.tjmt.jus.br/dje')

# Aguardar o carregamento da página
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//mat-icon[contains(@class, "fa-cloud-download-alt")]')))

# Localizar todos os ícones de download
download_icons = driver.find_elements(By.XPATH, '//mat-icon[contains(@class, "fa-cloud-download-alt")]')

print(f'Encontrados {len(download_icons)} ícones de download.')

if download_icons:
    # Localizar o primeiro ícone de download
    primeiro_download_icon = download_icons[0]

    try:
        # Tentar localizar o botão ancestral usando um seletor mais direto
        button = primeiro_download_icon.find_element(By.XPATH, './ancestor::button')
        button.click()
        print('Botão de download clicado com sucesso.')

        # Aguardar o download concluir
        time.sleep(10)  # Ajuste o tempo se necessário

        # Identificar o arquivo baixado (assumindo padrão de nome e diretório de downloads padrão)
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        downloaded_files = os.listdir(downloads_folder)
        pdf_files = [f for f in downloaded_files if f.endswith('.pdf')]

        if pdf_files:
            pdf_file_path = os.path.join(downloads_folder, pdf_files[0])

            # Função para extrair a data do PDF
            def extrair_data_pdf(pdf_content):
                doc = fitz.open(stream=pdf_content, filetype="pdf")
                data_texto = ""
                for page in doc:
                    data_texto += page.get_text()

                # Expressão regular para encontrar datas no formato "04 de setembro de 2024"
                padrao_data = r'\b\d{1,2} de [a-zA-Z]+ de \d{4}\b'
                correspondencias = re.findall(padrao_data, data_texto, re.IGNORECASE)

                if correspondencias:
                    return correspondencias[0].lower()  # Converter para minúsculas para facilitar o parsing
                else:
                    raise ValueError("Data de disponibilização não encontrada no PDF.")

            # Ler o conteúdo do PDF para extrair a data
            with open(pdf_file_path, 'rb') as f:
                pdf_content = f.read()

            try:
                data_disponibilizacao = extrair_data_pdf(pdf_content)
                print(f"Data extraída: {data_disponibilizacao}")

                # Converter a data para o formato YYYYMMDD
                def converter_data(data_str):
                    meses = {
                        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
                        "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
                    }
                    try:
                        dia, mes, ano = re.split(r' de ', data_str)
                        mes_num = meses[mes]
                        data_formatada = datetime.datetime.strptime(f"{dia} {mes_num} {ano}", "%d %m %Y").strftime("%Y%m%d")
                        return data_formatada
                    except KeyError as e:
                        raise ValueError(f"Nome do mês inválido encontrado: {e}")
                    except ValueError as e:
                        raise ValueError(f"Erro ao converter a data: {e}")

                data_formatada = converter_data(data_disponibilizacao)

                # Nome do arquivo com a data extraída
                novo_nome_arquivo = f"djmt_Unica_{data_formatada}.pdf"
                novo_caminho_arquivo = os.path.join(downloads_folder, novo_nome_arquivo)

                # Renomear o arquivo
                os.rename(pdf_file_path, novo_caminho_arquivo)

                print(f"Arquivo salvo e renomeado para: {novo_nome_arquivo}")

            except Exception as e:
                print(f"Erro ao processar o PDF: {e}")
        else:
            print("Nenhum arquivo PDF encontrado na pasta de Downloads.")
    except Exception as e:
        print(f'Erro ao clicar no ícone de download: {e}')
else:
    print("Nenhum ícone de download encontrado.")

# Fechar o WebDriver
driver.quit()
