import os
import re
import time
import requests
import pdfplumber
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

# Inicializando o webdriver
driver = webdriver.Chrome(options=chrome_options)

def extrair_data_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            # Procurar a data no formato "03 de Setembro de 2024"
            match = re.search(r"(\d{2}) de ([\w\-]+) de (\d{4})", texto)
            if match:
                dia, mes_nome, ano = match.groups()
                meses = {
                    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                    "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                    "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
                }
                mes = meses[mes_nome.lower()]
                data_formatada = f"{ano}{mes}{dia}"  # Formato YYYYMMDD
                return data_formatada
    return None

def baixar_pdf_secao(secao, nome_arquivo_prefixo):
    print(f"Navegando para a página da seção {secao}...")
    driver.get('https://revistas.inpi.gov.br/rpi/')

    print("Aguardando o carregamento da página...")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))

    print("Clicando no botão 'Concordar e Fechar', se necessário...")
    try:
        concordar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Concordar e Fechar')]"))
        )
        concordar_btn.click()
    except:
        pass  # Botão não encontrado ou não era necessário

    print(f"Encontrando o link mais recente para a seção '{secao}'...")
    links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{secao}') and contains(text(), 'PDF')]")

    if links:
        sorted_links = sorted(links, key=lambda x: x.get_attribute('href'), reverse=True)
        latest_link = sorted_links[0].get_attribute('href')

        print(f"Baixando o PDF mais recente para a seção '{secao}': {latest_link}")
        response = requests.get(latest_link)
        pdf_path = "C:/Downloads/temp.pdf"  # Caminho temporário para o PDF baixado

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        print("PDF baixado com sucesso.")
        data_pdf = extrair_data_pdf(pdf_path)
        if data_pdf:
            novo_nome = f"{nome_arquivo_prefixo}_{data_pdf}.pdf"
            novo_caminho = os.path.join("C:/Users/0167814/Downloads", novo_nome)
            os.rename(pdf_path, novo_caminho)
            print(f"PDF renomeado para: {novo_nome}")
        else:
            print("Data de disponibilização não encontrada no PDF.")
    else:
        print(f"Nenhum link para a seção '{secao}' encontrado.")

# Processamento para cada seção
try:
    baixar_pdf_secao("Comunicados", "dorpicomuni")
    baixar_pdf_secao("Contratos_de_Tecnologia", "dorpictrtec")
finally:
    print("Fechando o navegador após as ações...")
    time.sleep(10)  # Tempo para observar a saída
    driver.quit()
