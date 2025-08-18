import argparse
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd

# Configurações
BASE_URL = "https://odk.envelhecer.online"
PROJECT_ID = 1
FORM_PAI = "Formul%C3%A1rio%20Inicial"
FORM_FILHO = "Formul%C3%A1rio%20Parte%20II"

USERNAME = "lucianovilasboas@gmail.com"
PASSWORD = "9419131773"

CSV_TEMP_FILE = "submissions.csv"
CSV_FILE = "parte1.csv"



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Script para atualizar formulários ODK")
    parser.add_argument("--anexo", "-a", type=str, default=CSV_FILE, help="Nome do arquivo anexo")
    parser.add_argument("--publicar", "-p", action="store_true", default=False, help="Publicar o rascunho após o upload")
    
    args = parser.parse_args()


    # --- Download do Formulário 1

    # Endpoint para exportar CSV
    url_csv = f"{BASE_URL}/v1/projects/{PROJECT_ID}/forms/{FORM_PAI}/submissions.csv"

    # Baixar CSV
    response = requests.get(url_csv, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        with open(CSV_TEMP_FILE, "wb") as f:
            f.write(response.content)
        print("✅ CSV exportado com sucesso!")
    else:
        print("❌ Erro ao exportar CSV:", response.text)


    # --- Processamento e geração dos ids (identificador_unico)
    ANEXO = args.anexo

    df = pd.read_csv(CSV_TEMP_FILE, sep=",")
    colunas = ['identificador_unico','nome_agente', 'bairro', 'nome', 'cpf', 'endereco','telefone']
    df['identificador_unico'] = df.index+1
    df.rename(columns={'nome_pessoa_idosa': 'nome'}, inplace=True)
    df[colunas].to_csv(ANEXO, index=False)
    print(f"✅ CSV {ANEXO} com identificador_unico gerado com sucesso!")


    # --- Upload do anexo do Formulário Parte II

    # Endpoint para upload de anexo
    # POST                   /v1/projects/{projectId}/forms/{xmlFormId}/draft/attachments/{filename}
    url_upload = f"{BASE_URL}/v1/projects/{PROJECT_ID}/forms/{FORM_FILHO}/draft/attachments/{ANEXO}"

    # Enviar o CSV
    with open(ANEXO, "rb") as f:
        response = requests.post(
            url_upload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers={"Content-Type": "text/csv"},
            data=f.read()
        )


    if response.status_code == 200:
        print(f"✅ CSV atualizado no formulário {FORM_FILHO}!")
    else:
        print("❌ Erro ao enviar CSV:", response.text)


    # (Opcional) Publicar o rascunho do formulário para disponibilizar aos usuários
    # Fazer essa parte manualmente
    if args.publicar:
        url_publish = f"{BASE_URL}/v1/projects/{PROJECT_ID}/forms/{FORM_FILHO}/draft/publish"
        response = requests.post(url_publish, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            print("📢 Novo CSV publicado e disponível no Collect!")
        else:
            print("⚠ Erro ao publicar:", response.text)
