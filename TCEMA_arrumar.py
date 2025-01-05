import requests
from datetime import datetime, timedelta
import os
from PyPDF2 import PdfReader

# Função para calcular o dia útil anterior
def dia_util_anterior(data_atual):
    dia_anterior = data_atual - timedelta(days=1)
    while dia_anterior.weekday() >= 5:  # Se for sábado (5) ou domingo (6), volta um dia
        dia_anterior -= timedelta(days=1)
    return dia_anterior

# Data de hoje e dia útil anterior
hoje = datetime.now()
dia_util = dia_util_anterior(hoje)
data_formatada = dia_util.strftime('%Y%m%d')

# Aqui você deve colocar a lógica para obter o último número do PDF automaticamente.
# Para fins de exemplo, usamos um link fixo que você pode substituir mais tarde:
url_pdf = 'https://app.tcema.tc.br/diario/publicacao/pdf/9142'  # Substitua pelo link correto

# Nome do arquivo
nome_arquivo = f'tcema_{data_formatada}.pdf'

# Caminho para a pasta de downloads do sistema
pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')

# Caminho completo do arquivo na pasta de downloads
caminho_arquivo = os.path.join(pasta_download, nome_arquivo)

# Baixa o arquivo PDF
response = requests.get(url_pdf)
if response.status_code == 200:
    with open(caminho_arquivo, 'wb') as f:
        f.write(response.content)
    print(f'PDF baixado e salvo como {nome_arquivo} na pasta Downloads')
    
    # Verifica a data dentro do PDF
    with open(caminho_arquivo, 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        first_page = reader.pages[0]
        text = first_page.extract_text()

    # Verifica se a data correta está no texto
    if "01 de novembro de 2024" in text:
        print("O PDF contém a data correta: 01 de novembro de 2024.")
    else:
        print("A data no PDF está incorreta.")
else:
    print(f'Erro ao baixar o arquivo. Status code: {response.status_code}')
