import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import PyPDF2

def verificar_data_pdf(caminho_arquivo, data_formatada):
    # Verificar se a data formatada está no PDF
    with open(caminho_arquivo, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        # Limitar a verificação às duas primeiras páginas
        for page_num in range(min(2, len(reader.pages))):
            text = reader.pages[page_num].extract_text()
            if text:
                # Verifica se a data está no formato "dd de mês de aaaa" ou "dd/mm/aaaa"
                if (data_formatada in text or
                    datetime.strptime(data_formatada, '%d/%m/%Y').strftime('%d de %B de %Y') in text):
                    return True
    return False

def baixar_pdfs():
    # Data de hoje
    hoje = datetime.now()
    data_formatada = hoje.strftime('%d/%m/%Y')  # Formato da data
    data_formatada_yyyymmdd = hoje.strftime('%Y%m%d')  # Para o nome do arquivo

    # URL do site do TCERS
    url = "https://tcers.tc.br/diario-eletronico/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Erro ao acessar o site: {response.status_code}')
        return

    # Analisando o HTML da página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar a linha com a data atual
    linha_data = soup.find('p', class_='card_list__diaries-title', string=f'Edições disponibilizadas em {data_formatada}')
    
    if not linha_data:
        print(f"Edição do dia {data_formatada} não encontrada.")
        return

    # Encontrar todos os itens de PDFs a partir da linha de data
    div_pdfs = linha_data.find_next_sibling('div')
    
    pdf_links = []

    # Iterar sobre todos os irmãos do div_pdfs até encontrar um separador
    for item in div_pdfs.find_all_next('div', class_='card_list__item'):
        # Se encontrarmos o separador, saímos do loop
        if item.get('class') == ['card_list__diaries-separator']:
            break
        
        link_tag = item.find('a', href=True)
        if link_tag:
            pdf_links.append(link_tag['href'])

    if not pdf_links:
        print("Nenhum PDF encontrado para o dia de hoje.")
        return

    # Adicionar uma verificação dos links encontrados
    print(f"Links encontrados: {pdf_links}")

    # Nomes dos arquivos
    nomes_arquivos = [
        f'TCERS unicatcerssup {data_formatada_yyyymmdd}.pdf',
        f'TCERS unicatcerssup2 {data_formatada_yyyymmdd}.pdf',
        f'TCERS unicatcerssup3 {data_formatada_yyyymmdd}.pdf'  # Nome único
    ]

    # Baixar os PDFs
    pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')

    for i, link in enumerate(pdf_links):
        # Verificar se temos um nome correspondente para o PDF
        if i < len(nomes_arquivos):
            nome_arquivo = nomes_arquivos[i]
        else:
            nome_arquivo = f'TCERS extra {data_formatada_yyyymmdd}.pdf'

        # Caminho completo do arquivo na pasta de downloads
        caminho_arquivo = os.path.join(pasta_download, nome_arquivo)

        # Baixar o arquivo PDF
        response = requests.get(link)
        if response.status_code == 200:
            with open(caminho_arquivo, 'wb') as f:
                f.write(response.content)
            print(f'PDF baixado e salvo como {nome_arquivo} na pasta Downloads')

            # Verificar a data no PDF
            if not verificar_data_pdf(caminho_arquivo, data_formatada):
                print(f"A data no PDF {nome_arquivo} não corresponde a {data_formatada}.")
                # Opcional: Remover o PDF se a data não corresponder
                os.remove(caminho_arquivo)
                print(f'O PDF {nome_arquivo} foi removido.')
        else:
            print(f'Erro ao baixar o PDF: {link} - Status code: {response.status_code}')

# Chamar a função para baixar os PDFs
baixar_pdfs()
