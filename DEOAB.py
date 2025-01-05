from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import requests
import os
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

# Acessar o site
driver.get('https://deoab.oab.org.br/pages/visualizacao?pagina=1')

# Pausa para garantir que a página carregue
time.sleep(5)

# Espera até que o botão "Edição atual em PDF" esteja disponível e captura o link
try:
    botao_pdf = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Edição atual em PDF"))
    )
    link_pdf = botao_pdf.get_attribute('href')  # Captura o link do PDF
    print(f"Link do PDF capturado: {link_pdf}")
except Exception as e:
    print(f"Erro ao capturar o link: {e}")
    driver.quit()
    exit()

# Fecha o navegador, pois não será mais necessário
driver.quit()

# Data atual para nomear o arquivo
data_atual = datetime.now().strftime('%Y%m%d')
nome_arquivo = f'DEOAB unica {data_atual}.pdf'
caminho_arquivo = os.path.join(download_dir, nome_arquivo)

# Baixa o PDF diretamente do link capturado
try:
    response = requests.get(link_pdf)
    with open(caminho_arquivo, 'wb') as file:
        file.write(response.content)
    print(f"Arquivo baixado e renomeado para {nome_arquivo}")
except Exception as e:
    print(f"Erro ao baixar o PDF: {e}")
