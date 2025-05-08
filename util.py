import requests
import matplotlib.pyplot as plt

# --- Autenticação Automática ---
def obter_token():
    url = "https://odk.envelhecer.online/v1/sessions"
    dados = {
        "email": "lucianovilasboas@gmail.com",
        "password": "9419131773"
    }
    resposta = requests.post(url, json=dados)
    if resposta.status_code == 200:
        return resposta.json()["token"]
    else:
        return None
    

def graficos_2x2(df, coluna, municipios, pergunta): 
    fig, axs = plt.subplots(2, 2, figsize=(8, 6))
    axs = axs.flatten()

    for i, municipio in enumerate(municipios):
        df_ = df[df["Municipio"] == municipio]
        dados = df_[coluna].value_counts()

        axs[i].pie(
            dados,
            labels=dados.index,
            autopct='%1.1f%%',
            startangle=90
        )
        axs[i].set_title(municipio)
        axs[i].axis('equal')

    plt.suptitle(pergunta, fontsize=16, fontweight='bold', y=1.03)
    plt.tight_layout()
    plt.show()