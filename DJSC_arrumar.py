import fitz  # PyMuPDF
import re
import requests
from io import BytesIO
import datetime
import os
from bs4 import BeautifulSoup

# Função para extrair a data do PDF
def extrair_data_pdf(pdf_content):
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    data_texto = ""
    for page in doc:
        data_texto += page.get_text()
    
    # Expressão regular para encontrar datas no formato "22 de agosto de 2024"
    padrao_data = r'\b\d{1,2} de [a-zA-Z]+ de \d{4}\b'
    correspondencias = re.findall(padrao_data, data_texto, re.IGNORECASE)

    if correspondencias:
        return correspondencias[0].lower()  # Converter para minúsculas para facilitar o parsing
    else:
        raise ValueError("Data de disponibilização não encontrada no PDF.")

# Função para converter a data para o formato YYYYMMDD
def converter_data(data_str):
    meses = {
        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
        "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
    }
    try:
        dia, mes, ano = re.split(r' de ', data_str)
        mes_num = meses[mes]
        data_formatada = datetime.datetime.strptime(f"{dia} {mes_num} {ano}", "%d %m %Y").strftime("%Y%m%d")
        return data_formatada
    except KeyError as e:
        raise ValueError(f"Nome do mês inválido encontrado: {e}")
    except ValueError as e:
        raise ValueError(f"Erro ao converter a data: {e}")

# Função para buscar a última edição do PDF para a data atual
def obter_url_pdf():
    # Obtém a data atual
    data_atual = datetime.datetime.now()
    data_formatada = data_atual.strftime('%d/%m/%Y')

    # URL da página que lista os diários
    url_base = "https://busca.tjsc.jus.br/dje-consulta/#/main"
    resposta = requests.get(url_base)
    
    if resposta.status_code != 200:
        raise ValueError(f"Erro ao acessar a página do DJSC: {resposta.status_code}")

    # Usar BeautifulSoup para analisar o HTML
    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Aqui, precisamos encontrar os links de diários. Isso pode requerer ajustes conforme a estrutura do site.
    # Buscando todos os links que contêm "caderno" e a data formatada
    links = soup.find_all('a', href=True)
    url_pdf = None
    for link in links:
        if 'caderno' in link['href'] and data_formatada in link.text:
            url_pdf = link['href']
            break

    if not url_pdf:
        raise ValueError("Não foi possível encontrar o PDF para a data atual.")

    return url_pdf

# URL do PDF dinâmico
url_pdf = obter_url_pdf()

# Baixar o PDF
resposta = requests.get(url_pdf)
pdf_content = BytesIO(resposta.content)

try:
    # Extrair a data do PDF
    data_disponibilizacao = extrair_data_pdf(pdf_content)
    print(f"Data extraída: {data_disponibilizacao}")

    # Converter a data para o formato YYYYMMDD
    data_formatada = converter_data(data_disponibilizacao)

    # Nome do arquivo com a data extraída
    novo_nome_arquivo = f"DJSC_{data_formatada}.pdf"
    caminho_arquivo = os.path.join(os.path.expanduser("~"), "Downloads", novo_nome_arquivo)
    
    # Salvar o PDF com o novo nome
    with open(caminho_arquivo, 'wb') as f:
        f.write(resposta.content)
    
    print(f"Arquivo salvo e renomeado para: {novo_nome_arquivo}")
except Exception as e:
    print(f"Erro: {e}")
