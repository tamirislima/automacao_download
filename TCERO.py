import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re
from PyPDF2 import PdfReader

# Função para calcular o dia útil anterior
def dia_util_anterior(data_atual):
    dia_anterior = data_atual - timedelta(days=1)
    while dia_anterior.weekday() >= 5:  # Se for sábado (5) ou domingo (6), volta um dia
        dia_anterior -= timedelta(days=1)
    return dia_anterior

# Função para extrair a data do PDF
def extrair_data_do_pdf(caminho_pdf):
    try:
        with open(caminho_pdf, 'rb') as f:
            reader = PdfReader(f)
            num_paginas = len(reader.pages)
            texto = ""
            for i in range(min(num_paginas, 2)):  # Limita a leitura às 2 primeiras páginas
                texto += reader.pages[i].extract_text()
            # Procura o padrão de data no formato "segunda-feira, 21 de outubro de 2024"
            match = re.search(r'\b(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})\b', texto, re.IGNORECASE)
            if match:
                dia = int(match.group(1))
                mes = match.group(2)
                ano = int(match.group(3))
                meses = {
                    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                }
                return datetime(ano, meses[mes.lower()], dia)
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")
    return None

# Data de hoje e dia útil anterior
hoje = datetime.now()
dia_util = dia_util_anterior(hoje)
data_formatada = dia_util.strftime('%Y%m%d')

# URL do site principal do TCERO
url_site = 'https://tcero.tc.br/diario-oficial-tce-ro/'

# Realiza a requisição HTTP para acessar o site
response = requests.get(url_site)
if response.status_code == 200:
    # Faz o parsing do HTML da página
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tenta encontrar todos os links da página e verifica se algum contém "Diario" no href
    link_pdf = None
    for link in soup.find_all('a', href=True):
        if 'Diario' in link['href']:  # Procura "Diario" no link
            link_pdf = link['href']
            break  # Para no primeiro link que corresponder
    
    if link_pdf:
        print(f'Link do PDF encontrado: {link_pdf}')
        
        # Nome do arquivo
        nome_arquivo = f'tcero_{data_formatada}.pdf'

        # Caminho para a pasta de downloads do sistema
        pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')

        # Caminho completo do arquivo na pasta de downloads
        caminho_arquivo = os.path.join(pasta_download, nome_arquivo)

        # Baixa o arquivo PDF
        pdf_response = requests.get(link_pdf)
        if pdf_response.status_code == 200:
            with open(caminho_arquivo, 'wb') as f:
                f.write(pdf_response.content)
            print(f'PDF baixado e salvo como {nome_arquivo} na pasta Downloads')

            # Agora vamos verificar a data dentro do PDF
            data_pdf = extrair_data_do_pdf(caminho_arquivo)
            if data_pdf and data_pdf.date() == dia_util.date():
                print(f'A data no PDF ({data_pdf.strftime("%d/%m/%Y")}) corresponde ao dia útil anterior.')
            else:
                print(f'A data no PDF ({data_pdf.strftime("%d/%m/%Y") if data_pdf else "N/A"}) não corresponde ao dia útil anterior.')
                os.remove(caminho_arquivo)  # Remove o arquivo se a data não corresponder
                print('Arquivo PDF removido.')
        else:
            print(f'Erro ao baixar o PDF. Status code: {pdf_response.status_code}')
    else:
        print('Link do PDF não encontrado no site.')
else:
    print(f'Erro ao acessar o site. Status code: {response.status_code}')
