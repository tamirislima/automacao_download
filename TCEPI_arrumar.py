import requests
from bs4 import BeautifulSoup
import datetime
import os
import PyPDF2
import re

# Função para extrair a data do PDF
def extrair_data_pdf(caminho_pdf):
    with open(caminho_pdf, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text()
            if "Disponibilização:" in texto:
                break  # Para assim que a informação for encontrada

    print("Texto extraído do PDF:")
    print(texto)  # Mostra o texto extraído do PDF

    # Regex para encontrar a data
    padrao = r'Disponibilização:\s*(.*?-\s*\d{1,2}\s*de\s*\w+\s*de\s*\d{4})'
    resultado = re.search(padrao, texto)
    
    if resultado:
        data_disponibilizacao = resultado.group(1)
        # Converter a data para o formato desejado
        return datetime.datetime.strptime(data_disponibilizacao, '%A, %d de %B de %Y').strftime('%Y%m%d')
    return None

# URL principal do TCEPI
url_principal = "https://www.tcepi.tc.br/cidadao/diario-oficial/"
hoje = datetime.date.today()
data_ontem = hoje - datetime.timedelta(days=1)

# Acessando o site
response = requests.get(url_principal)
soup = BeautifulSoup(response.text, 'html.parser')

# Encontra o link do PDF para o dia atual
link_pdf = None
for link in soup.find_all('a'):
    href = link.get('href')
    if href and 'publicacao' in href:
        link_pdf = f"https://www.tcepi.tc.br{href}"  # Monta o URL completo
        break

if link_pdf:
    print(f"Link do PDF encontrado: {link_pdf}")
    
    # Baixa o PDF
    pdf_response = requests.get(link_pdf)
    nome_arquivo = f"TCEPI_unica_{data_ontem.strftime('%Y%m%d')}.pdf"
    caminho_arquivo = os.path.join(os.path.expanduser("~"), "Downloads", nome_arquivo)

    with open(caminho_arquivo, 'wb') as f:
        f.write(pdf_response.content)
    
    print(f"PDF baixado e salvo como {nome_arquivo} na pasta Downloads")

    # Verifica a data dentro do PDF
    data_extraida = extrair_data_pdf(caminho_arquivo)
    if data_extraida == data_ontem.strftime('%Y%m%d'):
        print("O PDF é do dia correto.")
    else:
        print(f"A data no PDF ({data_extraida}) não corresponde ao dia útil anterior.")
        os.remove(caminho_arquivo)  # Remove o PDF se a data não corresponder
else:
    print("Link do PDF não encontrado no site.")
