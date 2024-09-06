import re
import PyPDF2
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Mapeamento de meses em português para inglês
month_translation = {
    'janeiro': 'January',
    'fevereiro': 'February',
    'março': 'March',
    'abril': 'April',
    'maio': 'May',
    'junho': 'June',
    'julho': 'July',
    'agosto': 'August',
    'setembro': 'September',
    'outubro': 'October',
    'novembro': 'November',
    'dezembro': 'December'
}

# Função para traduzir o nome do mês
def translate_month(month_name):
    return month_translation.get(month_name.lower(), month_name)

# Função para extrair e formatar a data de disponibilização do PDF
def extract_date_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if "Disponibilização:" in text:
                # Procurar o padrão de data no formato "21 de Agosto de 2024"
                match = re.search(r'\d{1,2} de \w+ de \d{4}', text)
                if match:
                    date_str = match.group(0)
                    try:
                        # Traduzir o nome do mês para o inglês
                        day, month, year = date_str.split(' de ')
                        month = translate_month(month)
                        date_str_english = f'{day} {month} {year}'
                        # Converter a data para o formato YYYYMMDD
                        date_obj = datetime.datetime.strptime(date_str_english, '%d %B %Y')
                        return date_obj.strftime('%Y%m%d')
                    except ValueError as e:
                        print(f"Erro ao converter a data: {date_str}. Detalhes: {e}")
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
driver.get("https://transparencia.tjpi.jus.br/diarios")

# Esperar até que o botão "Pesquisar" esteja presente e clicar nele
wait = WebDriverWait(driver, 20)
search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Pesquisar']")))
search_button.click()

# Esperar alguns segundos para a página carregar os resultados
time.sleep(5)

# Encontrar o link do PDF
pdf_link_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'diarioeletronico/public')]")))
pdf_url = pdf_link_element.get_attribute("href")
print(f"URL do PDF: {pdf_url}")

# Listar os arquivos existentes na pasta de downloads antes do download
before_download = set(os.listdir(download_dir))

# Navegar até o URL do PDF para iniciar o download
driver.get(pdf_url)

# Adicionando um delay para manter o navegador aberto por um tempo (ajuste conforme necessário)
time.sleep(8)

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

    # Extrair a data do PDF
    original_file = os.path.join(download_dir, downloaded_file)
    extracted_date = extract_date_from_pdf(original_file)
    
    if extracted_date:
        # Nome do novo arquivo com a data extraída
        new_filename = f"dodjpi unica {extracted_date}.pdf"
        new_file = os.path.join(download_dir, new_filename)

        # Renomear o arquivo baixado
        os.rename(original_file, new_file)
        print(f"Arquivo renomeado para: {new_filename}")
    else:
        print("Erro: Data de disponibilização não encontrada no PDF.")
