import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import time

# Configurações
download_folder = 'C:/Users/0167814/Downloads/'  
chromedriver_path = 'C:/Users/0167814/OneDrive - Thomson Reuters Incorporated/Documents/selenium/chromedriver.exe'

def baixar_diario_oficial():
    """Baixa o PDF capturando a URL diretamente da rede."""
    chrome_options = Options()
    chrome_options.add_argument("--auto-open-devtools-for-tabs")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    service = Service(chromedriver_path)
    navegador = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Configuração para monitorar a rede e capturar requisições do Chrome DevTools Protocol (CDP)
        navegador.execute_cdp_cmd("Network.enable", {})
        
        pdf_link = None

        def capturar_pdf(request):
            nonlocal pdf_link
            url = request.get("request", {}).get("url", "")
            if ".pdf" in url:
                pdf_link = url
                print(f"URL do PDF capturada: {pdf_link}")

        navegador.request_interceptor = capturar_pdf

        navegador.get('https://ioes.dio.es.gov.br/portal/visualizacoes/diario_oficial')

        # Aguarda a imagem estar presente e clica nela
        imagem_diario = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.ID, 'imagemCapa'))
        )
        print("Imagem localizada com sucesso.")
        imagem_diario.click()

        # Aguardar alguns segundos para captura da URL do PDF na rede
        time.sleep(5)

        # Verifica se a URL do PDF foi capturada
        if pdf_link:
            response = requests.get(pdf_link)
            if response.status_code == 200:
                data_atual = datetime.now().strftime("%Y%m%d")
                pdf_path = os.path.join(download_folder, f'doees_unica_{data_atual}.pdf')
                with open(pdf_path, 'wb') as file:
                    file.write(response.content)
                print(f'PDF baixado e salvo como: {pdf_path}')
            else:
                print("Erro no download do PDF.")
        else:
            print("URL do PDF não encontrada ou inválida.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    finally:
        navegador.quit()

if __name__ == "__main__":
    baixar_diario_oficial()
