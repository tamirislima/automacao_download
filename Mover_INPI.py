import os
import shutil
import locale
from datetime import datetime

# Define o locale para português
locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

def mover_arquivo_para_diretorio(origem_dir, base_dir):
    # Lista todos os arquivos no diretório de origem
    arquivos = [f for f in os.listdir(origem_dir) if f.endswith(".pdf")]
    
    if not arquivos:
        print(f"Erro: Nenhum arquivo PDF encontrado no diretório '{origem_dir}'.")
        return
    
    for file_name in arquivos:
        file_path = os.path.join(origem_dir, file_name)
        
        # Extrai o nome do arquivo sem a extensão
        file_name_without_ext, _ = os.path.splitext(file_name)
        
        # Tenta extrair a data do nome do arquivo
        try:
            date_str = file_name_without_ext[-8:]  # Assume que a data está no formato YYYYMMDD no final do nome
            date_obj = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            print(f"Erro: O arquivo '{file_name}' não possui uma data válida no formato YYYYMMDD no nome.")
            continue
        
        # Monta os diretórios de destino com nomes em português
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%B').capitalize()  # Mês com a primeira letra maiúscula
        subfolder = file_name_without_ext.rsplit('_', 1)[0]  # Parte antes da data no nome do arquivo
        dest_dir = os.path.join(base_dir, year, month, subfolder, date_str)
        
        # Cria os diretórios se não existirem
        os.makedirs(dest_dir, exist_ok=True)
        
        # Move o arquivo
        try:
            shutil.move(file_path, os.path.join(dest_dir, file_name))
            print(f"Arquivo '{file_name}' movido para '{dest_dir}' com sucesso.")
        except Exception as e:
            print(f"Erro ao mover o arquivo '{file_name}': {e}")

# Exemplo de uso
origem_dir = r"C:\Users\0167814\Downloads"  # Diretório de origem dos PDFs
base_dir = r"C:\Work\Diarios\DF\Diário Oficial do INPI\Secoes"  # Diretório base

# Chama a função
mover_arquivo_para_diretorio(origem_dir, base_dir)
