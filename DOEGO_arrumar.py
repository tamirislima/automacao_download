import os
import datetime
import requests
import PyPDF2
import re
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configurações
chromedriver_path = 'C:/Users/0167814/OneDrive - Thomson Reuters Incorporated/Documents/selenium/chromedriver.exe'
download_folder = 'C:/Users/0167814/Downloads/'  # Caminho de download atualizado

# Função para gerar os nomes dos arquivos
def gerar_nome_arquivo(data, tipo):
    data_formatada = data.strftime('%Y%m%d')
    if tipo == 'unica':
        return f'doego_unica{data_formatada}.pdf'
    elif tipo == 'suplemento':
        return f'doego_doegosup-{data_formatada}.pdf'

# Função para configurar o navegador com pasta de download automática
def configurar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o navegador em modo "headless"
    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

# Função para calcular o dia útil anterior
def calcular_dia_util_anterior(data):
    if data.weekday() == 0:  # Segunda-feira
        return data - datetime.timedelta(days=3)  # Volta para sexta-feira
    else:
        return data - datetime.timedelta(days=1)  # Volta um dia útil

# Função para encontrar os links mais recentes
def obter_links_mais_recentes():
    navegador = configurar_navegador()
    navegador.get('https://diariooficial.abc.go.gov.br/')
    time.sleep(5)  # Espera a página carregar

    edicoes = navegador.find_elements(By.XPATH, "//optgroup")
    
    links = {}
    ano_atual = datetime.datetime.now().year
    mes_atual = datetime.datetime.now().month
    for edicao in edicoes:
        label = edicao.get_attribute('label')  # Exemplo: '04/10/2024'
        if str(ano_atual) in label and str(mes_atual).zfill(2) in label:
            options = edicao.find_elements(By.TAG_NAME, 'option')
            for option in options:
                texto = option.text
                valor = option.get_attribute('value')
                if 'SUPLEMENTO' in texto:
                    links['suplemento'] = f'https://diariooficial.abc.go.gov.br/portal/edicoes/download/{valor}'
                else:
                    links['caderno'] = f'https://diariooficial.abc.go.gov.br/portal/edicoes/download/{valor}'

    navegador.quit()
    return links

# Função para baixar o arquivo PDF e salvar no diretório
def baixar_pdf(url, nome_arquivo):
    try:
        print(f"Baixando {nome_arquivo} de {url}...")
        resposta = requests.get(url)
        if resposta.status_code == 200:
            caminho_completo = os.path.join(download_folder, nome_arquivo)
            with open(caminho_completo, 'wb') as f:
                f.write(resposta.content)
            print(f"Arquivo {nome_arquivo} baixado com sucesso.")
            return caminho_completo
        else:
            print(f"Falha ao baixar {nome_arquivo}. Status: {resposta.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return None

# Função para extrair a data do PDF e comparar com a data esperada
def extrair_data_pdf(caminho_pdf):
    try:
        with open(caminho_pdf, 'rb') as f:
            leitor_pdf = PyPDF2.PdfReader(f)
            conteudo_completo = ""
            for pagina in leitor_pdf.pages:
                conteudo_completo += pagina.extract_text()

            # Procurar pela data no formato "DD DE MÊS DE AAAA"
            match = re.search(r'(\d{2}) DE ([A-Z]+) DE (\d{4})', conteudo_completo)
            if match:
                dia, mes_extenso, ano = match.groups()
                mes_numero = mes_extenso_to_numero(mes_extenso)  # Converte o mês extenso para número
                return datetime.datetime(int(ano), mes_numero, int(dia))
            else:
                print("Data não encontrada no PDF.")
                return None
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")
        return None

# Função auxiliar para converter o mês extenso para número
def mes_extenso_to_numero(mes_extenso):
    meses = {
        "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4,
        "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8,
        "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12
    }
    return meses.get(mes_extenso.upper(), None)

# Função principal para baixar e verificar os diários
def baixar_e_verificar_diarios():
    # Definir datas
    data_hoje = datetime.datetime.now().date()
    data_ontem = calcular_dia_util_anterior(data_hoje)

    # Obter os links mais recentes
    links = obter_links_mais_recentes()

    # Baixar o caderno do dia
    nome_caderno = gerar_nome_arquivo(data_hoje, 'unica')
    caminho_caderno = baixar_pdf(links.get('caderno'), nome_caderno)
    
    if caminho_caderno:
        # Extrair a data do PDF e comparar
        print("Verificando a data no caderno do dia...")
        data_pdf_caderno = extrair_data_pdf(caminho_caderno)
        if data_pdf_caderno and data_pdf_caderno.date() == data_hoje:
            print(f"A data no PDF está correta: {data_pdf_caderno.strftime('%d/%m/%Y')}.")
        else:
            print(f"A data no PDF está incorreta ou não foi encontrada. Esperada: {data_hoje.strftime('%d/%m/%Y')}.")

    # Baixar o suplemento do dia útil anterior
    nome_suplemento = gerar_nome_arquivo(data_ontem, 'suplemento')
    caminho_suplemento = baixar_pdf(links.get('suplemento'), nome_suplemento)
    
    if caminho_suplemento:
        # Extrair a data do PDF e comparar
        print("Verificando a data no suplemento...")
        data_pdf_suplemento = extrair_data_pdf(caminho_suplemento)
        if data_pdf_suplemento and data_pdf_suplemento.date() == data_ontem:
            print(f"A data no PDF está correta: {data_pdf_suplemento.strftime('%d/%m/%Y')}.")
        else:
            print(f"A data no PDF está incorreta ou não foi encontrada. Esperada: {data_ontem.strftime('%d/%m/%Y')}.")

if __name__ == "__main__":
    baixar_e_verificar_diarios()
