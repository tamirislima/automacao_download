import datetime
import PyPDF2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

# Sua função para extrair a data do PDF
def extract_date_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if "Disponibilização :" in text:
                # Procurar o padrão de data completa no formato dd/mm/yyyy
                match = re.search(r'\d{2}/\d{2}/\d{4}', text)
                if match:
                    date_str = match.group(0)
                    try:
                        date_obj = datetime.datetime.strptime(date_str, '%d/%m/%Y')
                        return date_obj.strftime('%Y%m%d')
                    except ValueError:
                        print(f"Erro ao converter a data: {date_str}")
                else:
                    print("Data no formato correto não encontrada.")
                    
    return None

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

# Navegando até a URL desejada
driver.get("http://www.tjma.jus.br/")

# Esperar até que o link "Diário de Justiça" esteja presente e clicável
wait = WebDriverWait(driver, 20)
diario_justica_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Aba de Consulta Diário de Justiça']")))
driver.execute_script("arguments[0].scrollIntoView(true);", diario_justica_link)
time.sleep(1)

# Clicar no link "Diário de Justiça"
diario_justica_link.click()

# Esperar alguns segundos para a página carregar os resultados
time.sleep(5)

# Encontrar o link do último PDF disponível
last_pdf_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@title, 'botão Consulta de Últimos diários de justiça')]")))
pdf_url = last_pdf_link.get_attribute("href")
print(f"URL do PDF: {pdf_url}")

# Listar os arquivos existentes na pasta de downloads antes do download
before_download = set(os.listdir(download_dir))

# Navegar até o URL do PDF para iniciar o download
driver.get(pdf_url)

# Adicionando um delay maior para garantir que o download seja concluído (ajuste conforme necessário)
time.sleep(5) 

# Fechando o navegador
driver.quit()

# Listar os arquivos existentes na pasta de downloads após o download
after_download = set(os.listdir(download_dir))

# Encontrar o novo arquivo baixado
new_files = after_download - before_download
if len(new_files) != 1:
    print("Erro: Nenhum ou múltiplos arquivos novos encontrados na pasta de downloads.")
else:
    downloaded_file = new_files.pop()

    # Nome do novo arquivo com a data extraída do PDF
    original_file = os.path.join(download_dir, downloaded_file)
    extracted_date = extract_date_from_pdf(original_file)
    
    if extracted_date:
        new_filename = f"djma_Unica_{extracted_date}.pdf"
        new_file = os.path.join(download_dir, new_filename)

        # Renomear o arquivo baixado
        os.rename(original_file, new_file)
        print(f"Arquivo renomeado para: {new_filename}")
    else:
        print("Erro: Data de disponibilização não encontrada no PDF.")
