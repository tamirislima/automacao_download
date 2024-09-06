import requests
import os
import datetime

# Função para baixar o PDF
def baixar_pdf(url, caminho_arquivo):
    resposta = requests.get(url)
    if resposta.status_code == 200:
        with open(caminho_arquivo, 'wb') as f:
            f.write(resposta.content)
        print(f"Arquivo baixado para: {caminho_arquivo}")
    else:
        print(f"Falha ao baixar o PDF. Status code: {resposta.status_code}")

# URL do PDF
url_pdf = "https://www.tjro.jus.br/diario_oficial/ultimo-diario.php"

# Diretório para salvar o PDF baixado
download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

# Obter a data atual no formato desejado
current_date = datetime.datetime.now().strftime("%Y%m%d")

# Nome do novo arquivo com a data
novo_nome_arquivo = f"dodjro Unica {current_date}.pdf"
caminho_arquivo = os.path.join(download_dir, novo_nome_arquivo)

# Baixar o PDF
baixar_pdf(url_pdf, caminho_arquivo)

# Não é necessário renomear o arquivo, pois já é salvo com o nome correto
print(f"Arquivo salvo e renomeado para: {novo_nome_arquivo}")
