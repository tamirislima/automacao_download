from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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


# Função para baixar o PDF do TCEBA
def baixar_pdf_tceba():
    try:
        # Acessa a página do TCEBA
        url = 'https://www.tce.ba.gov.br/servicos/doe'
        print("Acessando a página:", url)
        driver.get(url)

        # Espera 5 segundos para garantir que a página carregue completamente
        time.sleep(5)

        # Procurando pelo link do PDF
        wait = WebDriverWait(driver, 20)  # Aumenta o tempo de espera para 20 segundos
        print("Procurando pelo elemento do PDF...")

        pdf_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'diarioOficial/download')]"))
        )

        # Verifica se encontrou algum link e baixa o primeiro encontrado
        if pdf_elements:
            print("Elemento do PDF encontrado!")
            url_pdf = pdf_elements[0].get_attribute('href')
            print("URL do PDF:", url_pdf)
            if url_pdf:
                # Diretório de downloads
                caminho_download = os.path.join(os.path.expanduser("~"), "Downloads")

                # Nome do arquivo com data invertida (YYYYMMDD)
                hoje = datetime.now()
                nome_arquivo = f"TCEBA_unica_{hoje.strftime('%Y%m%d')}.pdf"
                caminho_completo = os.path.join(caminho_download, nome_arquivo)

                # Faz o download do PDF
                response = requests.get(url_pdf)
                if response.status_code == 200:
                    with open(caminho_completo, 'wb') as f:
                        f.write(response.content)
                    print(f"Download concluído: {caminho_completo}")
                else:
                    print(f"Erro ao baixar o PDF. Código de status: {response.status_code}")
            else:
                print("Link do PDF não encontrado.")
        else:
            print("Elemento do PDF não encontrado na página.")

    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
    
    finally:
        driver.quit()

# Executando a função
baixar_pdf_tceba()