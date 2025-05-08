import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from util import obter_token

st.set_page_config(layout="wide")

st.title("Dashboard - Projeto Envelhecer")

odk_token = obter_token()

if odk_token:
    headers = {"Authorization": f"Bearer {odk_token}"}
    url_dados = "https://odk.envelhecer.online/v1/projects/1/forms/Formul%C3%A1rio%20Inicial.svc/Submissions"
    response = requests.get(url_dados, headers=headers)
    data = response.json()

    # --- Tratamento dos dados ---
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
    df["hora"] = df['timestamp'].dt.strftime('%H:%M')

    df['moradia_acesso_transporte.acesso_internet'] = df['moradia_acesso_transporte.acesso_internet'].replace(sim_nao_map)
    df['condicao_geral_saude.pcd'] = df['condicao_geral_saude.pcd'].replace(sim_nao_map)
    df['condicao_geral_saude.agente_saude_visita'] = df['condicao_geral_saude.agente_saude_visita'].replace(sim_nao_map)

    df["Municipio"] = df["__system.submitterName"].apply(lambda n: n.replace(")", "").split("(")[-1])

    # --- Interface de filtro ---
    st.sidebar.header("Filtros")
    municipios = df["Municipio"].dropna().unique().tolist()
    municipio_sel = st.sidebar.selectbox("Selecione o Município", municipios)

    pergunta = st.sidebar.selectbox("Pergunta", [
        ("moradia_acesso_transporte.acesso_internet", "Possui acesso à Internet?"),
        ("moradia_acesso_transporte.horas_internet", "Quantas horas de Internet por dia?"),
        ("condicao_geral_saude.pcd", "Você se considera uma Pessoa com Deficiência (PcD)?"),
        ("condicao_geral_saude.agente_saude_visita", "Algum agente de saúde te visita?"),
        ("condicao_geral_saude.frequencia_visita", "Qual a frequência de visitas do ACS?")
    ], format_func=lambda x: x[1])

    coluna, titulo = pergunta

    # --- Gráfico de barras vertical com total de respostas por munucipio ignorando as perguntas e destacar o valor de cada barra --- 
    df_municipio = df.groupby("Municipio").size().reset_index(name='Total_Respostas')
    fig_municipio = px.bar(df_municipio, x="Municipio", y="Total_Respostas", 
                            title=f"Total de Respostas: {len(df)}", 
                            labels={"Total_Respostas": "Total de Respostas"})
    fig_municipio.update_traces(texttemplate='%{y}', textfont_size=25)
    fig_municipio.update_layout(yaxis_title="Total de Respostas", xaxis_title="Município")
    st.plotly_chart(fig_municipio, use_container_width=True)
    # --- Gráfico de barras horizontal com total de respostas por munucipio e pergunta ---

   



    # --- Gráfico de pizza por município ---
    st.subheader(f"{municipio_sel}: {titulo}")
    df_m = df[df["Municipio"] == municipio_sel]
    dados = df_m[coluna].value_counts()

    fig, ax = plt.subplots()
    ax.pie(dados, labels=dados.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # --- Gráfico de pizza total ---
    st.subheader(f"Todos os municípios: {titulo}")
    dados_total = df[coluna].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(dados_total, labels=dados_total.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)

    # --- Gráfico interativo de evolução por município ---
    st.subheader("Evolução das respostas por Município")
    df_grouped = df.groupby(["Municipio", "data"])['respondente'].count().reset_index()
    df_grouped = df_grouped.rename(columns={"respondente": "Total_Respostas"})

    fig_line = px.line(df_grouped, x="data", y="Total_Respostas", color="Municipio", markers=True)
    fig_line.update_layout(title="Respostas ao longo do tempo", xaxis_title="Data", yaxis_title="Número de Respostas")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- Gráfico de barras para comparação entre municípios ---
    st.subheader("Distribuição de respostas por Município")
    df_bar = df.groupby("Municipio")[coluna].value_counts(normalize=True).rename("Proporcao").reset_index()
    fig_bar = px.bar(df_bar, x="Municipio", y="Proporcao", color=coluna, barmode="stack", 
                     labels={"Proporcao": "Proporção"}, 
                     title=f"Distribuição por Município - {titulo}")
    st.plotly_chart(fig_bar, use_container_width=True)



else:
    st.error("Erro ao obter o token de autenticação. Verifique suas credenciais.")