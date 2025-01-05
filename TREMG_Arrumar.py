import os
import time
import pdfplumber
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib

# Configuração do Selenium
options = webdriver.ChromeOptions()

# Definir preferências para o download de PDF
download_dir = "C:/Users/0167814/Downloads"  # Substitua pelo caminho correto no seu sistema
prefs = {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True,  # Forçar download do PDF
    "download.prompt_for_download": False,  # Não mostrar o prompt de download
}
options.add_experimental_option("prefs", prefs)

# Inicializa o navegador
driver = webdriver.Chrome(options=options)

try:
    print("Navegando para a página do TREMG...")
    driver.get('https://www.tre-mg.jus.br/servicos-judiciais/dje-janela')

    print("Aguardando o carregamento da página...")

    # Aguarda o botão "Concordar e Fechar" e clica nele
    try:
        concordar_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Concordar e fechar')]"))
        )
        print("Clicando no botão 'Concordar e Fechar'...")
        concordar_button.click()
    except Exception as e:
        print("Botão 'Concordar e Fechar' não encontrado ou já fechado:", e)

    # Agora continua com o restante do script após a confirmação do pop-up
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))

    print("Esperando o botão para download do PDF ser clicável...")
    try:
        # Aumentando o tempo de espera e verificando a presença do botão
        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//mat-icon[text()='get_app']"))
        )
        print("Clicando no botão para download do PDF...")
        button.click()

    except Exception as e:
        print("Erro ao encontrar o botão de download:", e)
        driver.quit()

    print("Aguardando o download do PDF...")
    download_completed = False
    pdf_file = ""
    while not download_completed:
        time.sleep(1)
        for filename in os.listdir(download_dir):
            if filename.endswith(".pdf") and not filename.endswith(".crdownload"):
                download_completed = True
                pdf_file = os.path.join(download_dir, filename)
                break

    print(f"PDF baixado com sucesso: {pdf_file}")

    # Função para extrair a data do PDF
    def extrair_data_pdf(caminho_pdf):
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                texto = page.extract_text()
                # Procurar o texto "Disponibilização: [dia da semana], DD de mês de YYYY"
                match = re.search(r"Disponibilização: [\w\-]+, (\d{2}) de ([\w\-]+) de (\d{4})", texto)
                if match:
                    dia, mes_nome, ano = match.groups()
                    # Mapeamento de meses para números
                    meses = {
                        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                        "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                        "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
                    }
                    mes = meses[mes_nome.lower()]
                    data_formatada = f"{ano}{mes}{dia}"  # Formato YYYYMMDD
                    return data_formatada
        return None

    # Extrair a data do PDF
    data_pdf = extrair_data_pdf(pdf_file)
    if data_pdf:
        novo_nome = f"DOTREMG_{data_pdf}.pdf"
        novo_caminho = os.path.join(download_dir, novo_nome)
        os.rename(pdf_file, novo_caminho)
        print(f"PDF renomeado para: {novo_nome}")

        # Função para enviar o PDF por e-mail
        def enviar_email(destinatario, assunto, corpo, anexo):
            remetente = "seuemail@gmail.com"
            senha = "sua_senha"

            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = destinatario
            msg['Subject'] = assunto

            msg.attach(MIMEText(corpo, 'plain'))

            attachment = open(anexo, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(anexo)}")
            msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(remetente, senha)
            text = msg.as_string()
            server.sendmail(remetente, destinatario, text)
            server.quit()

        # Enviar o e-mail com o PDF
        enviar_email(
            destinatario="destinatario@exemplo.com",
            assunto="PDF Baixado",
            corpo="Segue em anexo o PDF baixado e renomeado.",
            anexo=novo_caminho
        )
    else:
        print("Data de disponibilização não encontrada no PDF.")

finally:
    print("Fechando o navegador após as ações...")
    time.sleep(5)
    driver.quit()
