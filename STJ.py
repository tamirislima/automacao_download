import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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

def obter_ultimo_dia_util():
    hoje = datetime.now()
    if hoje.weekday() == 0:  # 0 = Segunda-feira
        ultimo_dia_util = hoje - timedelta(days=3)  # Volta 3 dias
    elif hoje.weekday() == 6:  # 6 = Domingo
        ultimo_dia_util = hoje - timedelta(days=2)  # Volta 2 dias
    else:
        ultimo_dia_util = hoje - timedelta(days=1)  # Volta 1 dia

    return ultimo_dia_util.strftime('%Y%m%d')

def baixar_arquivo_zip():
    data_ultimo_dia_util = obter_ultimo_dia_util()
    url_zip = f'https://processo.stj.jus.br/docs_internet/processo/dje/zip/stj_dje_{data_ultimo_dia_util}.zip'
    
    # Defina o diretório de download
    diretorio_download = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Nome do arquivo a ser salvo
    nome_arquivo = f'stj_dje_{data_ultimo_dia_util}.zip'
    caminho_completo = os.path.join(diretorio_download, nome_arquivo)
    
    # Fazendo o download
    response = requests.get(url_zip)
    
    # Verifica se o download foi bem-sucedido
    if response.status_code == 200:
        with open(caminho_completo, 'wb') as arquivo:
            arquivo.write(response.content)
        print(f'Arquivo {caminho_completo} baixado com sucesso.')
    else:
        print(f'Erro ao baixar o arquivo: {response.status_code}')

if __name__ == '__main__':
    baixar_arquivo_zip()