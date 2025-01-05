import logging
import os
import re
import time
import sys
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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



try:
    # Inicializando o webdriver
    driver = webdriver.Chrome(options=chrome_options)
    logging.info('Driver do Chrome inicializado com sucesso.')

    # Acessar o site do Diário Eletrônico
    driver.get('https://www1.tce.pr.gov.br/conteudo/lista/diario-eletronico/1436')
    logging.info('Site acessado com sucesso.')

    # Pausa para garantir que a página carregue completamente
    time.sleep(5)
    logging.debug('Pausa de 5 segundos concluída.')

    # Esperar pelo primeiro link
    logging.debug('Esperando pelo primeiro link...')
    primeiro_link = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'diario-eletronico')]"))
    )
    
    texto_link = primeiro_link.text
    logging.info(f"Link encontrado: {texto_link}")

    # Usar regex para capturar a data no formato DD de Mês de YYYY
    data_match = re.search(r'(\d{1,2}) de (\w+) de (\d{4})', texto_link)
    if data_match:
        dia = data_match.group(1).zfill(2)
        mes_extenso = data_match.group(2).lower()
        ano = data_match.group(3)

        meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04', 
            'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08', 
            'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }

        mes = meses.get(mes_extenso)
        if mes:
            data_formatada = f"{ano}{mes}{dia}"
            logging.info(f"Data extraída: {data_formatada}")
        else:
            raise ValueError("Mês não encontrado no dicionário.")
    else:
        raise ValueError("Data não encontrada no link.")

    # Clica no link
    logging.debug('Clicando no primeiro link...')
    primeiro_link.click()

    # Espera a nova página carregar
    logging.debug('Esperando pelo link do PDF...')
    pdf_link = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.pdf']"))
    ).get_attribute('href')
    logging.info(f"Link do PDF encontrado: {pdf_link}")

except Exception as e:
    logging.error(f"Erro: {e}")
    driver.quit()
    sys.exit()

finally:
    # Fecha o navegador independentemente do resultado
    logging.debug('Fechando o navegador...')
    driver.quit()

# Nome do arquivo PDF
nome_arquivo = f"TCEPR Unica {data_formatada}.pdf"
caminho_arquivo = os.path.join(download_dir, nome_arquivo)

# Baixa o PDF
try:
    logging.debug(f'Baixando o PDF do link: {pdf_link}')
    response = requests.get(pdf_link)
    response.raise_for_status()  # Gera exceção se o status não for 200
    with open(caminho_arquivo, 'wb') as file:
        file.write(response.content)
    logging.info(f"Arquivo baixado e renomeado para {nome_arquivo}")
except Exception as e:
    logging.error(f"Erro ao baixar o PDF: {e}")
