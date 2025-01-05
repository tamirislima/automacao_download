import os
import datetime
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações
chromedriver_path = 'C:/Users/0167814/OneDrive - Thomson Reuters Incorporated/Documents/selenium/chromedriver.exe'
download_folder = 'C:/Users/0167814/Downloads/'  # Caminho de download atualizado

# Função para gerar o nome do arquivo
def gerar_nome_arquivo(data):
    return f'TCETO Unica {data.strftime("%Y%m%d")}.pdf'

# Função para configurar o navegador com a pasta de download automática
def configurar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o navegador em modo "headless"
    prefs = {"download.default_directory": download_folder}
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

# Função para calcular o dia útil anterior
def calcular_dia_util_anterior(data):
    if data.weekday() == 0:  # Segunda-feira
        return data - datetime.timedelta(days=3)  # Volta para sexta-feira
    else:
        return data - datetime.timedelta(days=1)  # Volta um dia útil

# Função para baixar o PDF e verificar a data
def baixar_pdf_do_tce():
    # Definir a data de hoje e a do dia útil anterior
    data_hoje = datetime.datetime.now().date()
    data_ontem = calcular_dia_util_anterior(data_hoje)

    # Configurar o navegador
    navegador = configurar_navegador()
    navegador.get('https://app.tce.to.gov.br/boletim/publico/app/index.php#header')

    try:
        # Aumentar o tempo de espera
        WebDriverWait(navegador, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Tentar localizar o botão de ver mais para abrir a aba do dia
        botao_ver_mais = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btnVerMais')]"))
        )

        # Clicar no botão 'Ver Mais'
        botao_ver_mais.click()
        time.sleep(5)  # Espera a nova aba carregar

        # Trocar para a nova aba
        navegador.switch_to.window(navegador.window_handles[-1])

        # Obter o link do PDF
        link_pdf = "https://app.tce.to.gov.br/boletim/app/controllers/?&c=TCE_Boletim_PublicacoesCtrll&m=abrirHtml&id=12968&print=1"
        navegador.get(link_pdf)
        time.sleep(5)  # Espera a página carregar

        # Verificar a data no PDF antes de baixar
        if verificar_data_no_pdf(navegador):
            nome_arquivo = gerar_nome_arquivo(data_ontem)

            # Clicar no botão de imprimir para baixar
            botao_imprimir = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "cr-button.action-button"))
            )
            botao_imprimir.click()
            time.sleep(5)  # Espera o download iniciar

            # Esperar até o download ser concluído
            while not os.path.exists(os.path.join(download_folder, nome_arquivo)):
                time.sleep(1)  # Aguarda o download

            print(f"Arquivo {nome_arquivo} baixado com sucesso.")
        else:
            print("A data no PDF não corresponde ao esperado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        print("Verifique se o botão de 'Ver Mais' está disponível e se o site está acessível.")

    finally:
        navegador.quit()

# Função para verificar a data dentro do PDF
def verificar_data_no_pdf(navegador):
    # Obter o conteúdo da página que deve ter a data
    conteudo = navegador.page_source

    # Procurar pela data "Disponibilizado em DD/MM/AAAA"
    match = re.search(r'Disponibilizado em (\d{2}/\d{2}/\d{4})', conteudo)
    if match:
        data_disponibilizada = match.group(1)
        data_formatada = datetime.datetime.strptime(data_disponibilizada, '%d/%m/%Y').date()
        data_ontem = calcular_dia_util_anterior(datetime.datetime.now().date())

        # Verifica se a data do PDF corresponde ao dia útil anterior
        return data_formatada == data_ontem

    print("Data não encontrada no PDF.")
    return False

if __name__ == "__main__":
    baixar_pdf_do_tce()
