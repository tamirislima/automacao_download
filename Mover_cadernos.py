import os
import shutil

def move_file(file_path, base_dir):
    # Verificar se o arquivo existe
    if not os.path.isfile(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return

    # Extrair o nome do arquivo sem extensão
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]

    # Extrair a data do nome do arquivo
    date_str = file_name_without_ext[-8:]
    year = date_str[:4]
    month = 'novembro'
    day = date_str[6:]

    # Nome da pasta
    folder_name = 'dorpicomuni'

    # Criar o caminho do diretório de destino
    target_dir = os.path.join(base_dir, 'Diarios', 'DF', 'Diário Oficial do INPI', 'Secoes', year, month, folder_name, date_str)

    # Criar o diretório de destino se ele não existir
    os.makedirs(target_dir, exist_ok=True)

    # Mover o arquivo para o diretório de destino
    shutil.move(file_path, os.path.join(target_dir, file_name))
    print(f"Arquivo movido para {os.path.join(target_dir, file_name)}")

# Exemplo de uso
file_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'dorpicomuni_20241119')
base_dir = 'F:\\Work'
move_file(file_path, base_dir)
