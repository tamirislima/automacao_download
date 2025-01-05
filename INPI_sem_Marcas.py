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
from webdriver_manager.chrome import ChromeDriverManager  # Para gerenciar o ChromeDriver

# Diretório para salvar os PDFs
download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

# Configurando o ChromeOptions para evitar erros de permissões e configurar preferências de download
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-permissions-api")
prefs = {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True,
    "download.prompt_for_download": False,
}
chrome_options.add_experimental_option("prefs", prefs)

# Inicializando o WebDriver com o ChromeDriverManager para garantir a versão correta do driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Dicionário atualizado com as seções e seus prefixos
secoes = {
    "Comunicados": "dorpicomuni",
    "Contratos_de_Tecnologia": "dorpictrtec",
    "Desenhos_Industriais": "dorpidesind",
    "Indicacoes_Geograficas": "dorpiindgeo",  # Ajustado
    "Patentes": "dorpipatentes",
    "Programa_de_computador": "dorpiprocomp",  # Ajustado
    "Topografia_de_circuto_Integrado": "dorpitopci",  # Ajustado
}

# Função para extrair a data do PDF
def extrair_data_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            match = re.search(r"(\d{2}) de ([\w\-]+) de (\d{4})", texto)
            if match:
                dia, mes_nome, ano = match.groups()
                meses = {
                    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                    "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                    "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12",
                }
                mes = meses[mes_nome.lower()]
                return f"{ano}{mes}{dia}"
    return None

try:
    print("Acessando o site principal...")
    driver.get('https://revistas.inpi.gov.br/rpi/')
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))

    # Fechar o popup "Concordar e Fechar", se existir
    try:
        concordar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Concordar e Fechar')]"))
        )
        concordar_btn.click()
    except:
        print("Nenhum popup encontrado para fechar.")

    for secao, prefixo in secoes.items():
        print(f"\nProcessando seção: {secao}...")
        links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{secao}') and contains(text(), 'PDF')]")
        if links:
            latest_link = sorted(links, key=lambda x: x.get_attribute('href'), reverse=True)[0].get_attribute('href')
            print(f"Link encontrado: {latest_link}")

            # Baixar o PDF temporariamente
            response = requests.get(latest_link)
            temp_pdf_path = os.path.join(download_dir, "temp.pdf")
            with open(temp_pdf_path, 'wb') as f:
                f.write(response.content)

            # Extrair a data do PDF
            data_pdf = extrair_data_pdf(temp_pdf_path)
            if data_pdf:
                novo_nome = f"{prefixo}_{data_pdf}.pdf"
                novo_caminho = os.path.join(download_dir, novo_nome)
                try:
                    os.rename(temp_pdf_path, novo_caminho)
                    print(f"PDF renomeado para: {novo_nome}")
                except Exception as e:
                    print(f"Erro ao renomear o PDF: {e}")
            else:
                print(f"Não foi possível extrair a data do PDF para a seção: {secao}")
        else:
            print(f"Nenhum link encontrado para a seção: {secao}")

finally:
    print("\nFechando o navegador...")
    time.sleep(5)
    driver.quit()
