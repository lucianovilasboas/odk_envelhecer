import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from util import obter_token

st.set_page_config(layout="wide")

_, image_col, _ = st.columns([2,1,2])

with image_col:
    st.image("Envelhecer_nos_territrios.png", width=200)
st.title("Dashboard - Projeto Envelhecer Nos Territórios")

odk_token = obter_token()

if odk_token:
    headers = {"Authorization": f"Bearer {odk_token}"}
    url_dados = "https://odk.envelhecer.online/v1/projects/1/forms/Formul%C3%A1rio%20Inicial.svc/Submissions"
    response = requests.get(url_dados, headers=headers)
    data = response.json()

    df = pd.json_normalize(data['value'])

    nomes_map = {
        "Iphone Leandro Santa Cruz": "Leandro (SC. Escalvado)",
        "Iphone Camila Santa Cruz": "Camila (SC. Escalvado)",
        "Iphone Giovanna Barra Longa": "Giovanna (B. Longa)",
        "Iphone Andriele": "Andriele ()",
        "Iphone Maria Clara Barra Longa": "Maria Clara (B. Longa)",
        "iPhone João Barra Longa": "João (B. Longa)",
        "Priscila Lopes Ferreira (Amparo Serra)": "Priscila Lopes Ferreira (A. Serra)"
    }

    sim_nao_map = {'1': 'Sim', '2': 'Não', '3': 'NS/NR'}

    df["__system.submitterName"] = df["__system.submitterName"].replace(nomes_map)
    df["timestamp"] = pd.to_datetime(df["__system.submissionDate"])
    df["data"] = df['timestamp'].dt.date
    df["Municipio"] = df["__system.submitterName"].apply(lambda n: n.replace(")", "").split("(")[-1])

    df['moradia_acesso_transporte.acesso_internet'] = df['moradia_acesso_transporte.acesso_internet'].replace(sim_nao_map)
    df['condicao_geral_saude.pcd'] = df['condicao_geral_saude.pcd'].replace(sim_nao_map)
    df['condicao_geral_saude.agente_saude_visita'] = df['condicao_geral_saude.agente_saude_visita'].replace(sim_nao_map)

    # --- Filtro de pergunta ---
    st.sidebar.header("Selecione uma...")
    pergunta = st.sidebar.selectbox("Pergunta", [
        ("moradia_acesso_transporte.acesso_internet", "Possui acesso à Internet?"),
        ("moradia_acesso_transporte.horas_internet", "Quantas horas de Internet por dia?"),
        ("condicao_geral_saude.pcd", "Você se considera uma Pessoa com Deficiência (PcD)?"),
        ("condicao_geral_saude.agente_saude_visita", "Algum agente de saúde te visita?"),
        ("condicao_geral_saude.frequencia_visita", "Qual a frequência de visitas do ACS?")
        
    ], format_func=lambda x: x[1])

    coluna, titulo = pergunta

    st.header(f"Total Geral de Respostas: {len(df)}")

    # --- Layout principal ---
    col1, col2 = st.columns(2)

    # 1. Gráfico: Total de Respostas por Município
    with col1:
        st.subheader("1. Total de Respostas por Município")
        df_municipio = df.groupby("Municipio").size().reset_index(name='Total_Respostas')
        fig_total = px.bar(df_municipio, x="Municipio", y="Total_Respostas", text_auto=True)
        fig_total.update_layout(yaxis_title="Total de Respostas", xaxis_title="Município")
        st.plotly_chart(fig_total, use_container_width=True)

    # 2. Gráfico: Evolução das Respostas ao Longo do Tempo
    with col2:
        st.subheader("2. Evolução das Respostas ao Longo do Tempo")
        df_grouped = df.groupby(["Municipio", "data"]).size().reset_index(name="Total_Respostas")
        fig_evolucao = px.line(df_grouped, x="data", y="Total_Respostas", color="Municipio", markers=True)
        fig_evolucao.update_layout(xaxis_title="Data", yaxis_title="Número de Respostas")
        st.plotly_chart(fig_evolucao, use_container_width=True)

    # 3. Gráfico: Distribuição por Município da Pergunta Selecionada
    st.header(f"Visualização: {titulo}")
    st.subheader("3. Distribuição das Respostas por Município")
    df_bar = df.groupby(["Municipio", coluna]).size().reset_index(name="count")
    df_bar["percentual"] = df_bar.groupby("Municipio")["count"].transform(lambda x: x / x.sum()) * 100

    # Cores personalizadas para Sim/Não/NSNR
    cores_personalizadas = {
        "Sim": "green",
        "Não": "red",
        "NS/NR": "gray"
    }

    fig_bar = px.bar(
        df_bar, x="Municipio", y="percentual", color=coluna,
        color_discrete_map=cores_personalizadas,
        barmode="stack",
        labels={"percentual": "Proporção"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.error("Erro ao obter o token de autenticação. Verifique suas credenciais.")
