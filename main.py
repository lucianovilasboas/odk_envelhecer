import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from util import obter_token, aplicar_mapeamentos, plot_mapa, plot_pergunta, mapa_perguntas, lista_perguntas
from util import plot_ranking

st.set_page_config(layout="wide")

_, image_col, _ = st.columns([1,4,1])

with image_col:
    # st.image("Envelhecer_nos_territrios.png", width=200)
    st.image("ENVELHECER - IFMG - PONTE NOVA.png")
        
st.html("""<h1 style='text-align: center; color: #FFF; font-size:38px'>Dashboard - Projeto Envelhecer Nos Territórios</h1>""")

odk_token = obter_token(st)

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
        "Iphone Andriele": "Andriele (B. Longa)",
        "Iphone Maria Clara Barra Longa": "Maria Clara (B. Longa)",
        "iPhone João Barra Longa": "João (B. Longa)",
        "Priscila Lopes Ferreira (Amparo Serra)": "Priscila Lopes Ferreira (A. Serra)",
        "Iphone Gleysimara": "Gleysimara (A. Serra)",
    }

    df["__system.submitterName"] = df["__system.submitterName"].replace(nomes_map)
    df["timestamp"] = pd.to_datetime(df["__system.submissionDate"])
    df["data"] = df['timestamp'].dt.date
    df["Municipio"] = df["__system.submitterName"].apply(lambda n: n.replace(")", "").split("(")[-1])

    df = aplicar_mapeamentos(df)

    perguntas_vinculadas = {
        'aspectos_sociodemograficos.povo_tradicional':'aspectos_sociodemograficos.tipo_comunidade',
        'moradia_acesso_transporte.dispositivos_eletronicos': 'moradia_acesso_transporte.tipo_dispositivo',
        'apoio_social.cadastro_cras': 'apoio_social.tipo_servico_cras',
        'condicao_geral_saude.pcd': 'condicao_geral_saude.tipo_deficiencia',
        'trabalho_renda.trabalho_nao_remunerado': 'trabalho_renda.tipo_trabalho_nao_remunerado',
    }

    st.sidebar.header("Selecione uma...")
    pergunta = st.sidebar.selectbox("Pergunta", lista_perguntas, format_func=lambda x: x[1])

    coluna, titulo = pergunta
    st.subheader(f"Total Geral de Respostas: {len(df)}")

    # Layout principal
    col1, col2 = st.columns([2, 5])
    with col1:
        st.subheader("1. Total de Respostas por Município")
        df_municipio = df.groupby("Municipio").size().reset_index(name='Total_Respostas')
        fig_total = px.bar(df_municipio, x="Municipio", y="Total_Respostas", text_auto=True)
        fig_total.update_layout(yaxis_title="Total de Respostas", xaxis_title="Município")
        st.plotly_chart(fig_total, use_container_width=True)

    with col2:
        st.subheader("2. Evolução das Respostas ao Longo do Tempo")
        df_grouped = df.groupby(["Municipio", "data"]).size().reset_index(name="Total_Respostas")
        fig_evolucao = px.line(df_grouped, x="data", y="Total_Respostas", color="Municipio", markers=True)
        fig_evolucao.update_layout(xaxis_title="Data", yaxis_title="Número de Respostas")
        st.plotly_chart(fig_evolucao, use_container_width=True)


    # Graficos de rancking por agente 
    st.subheader("3. Ranking de Respostas por Agente")
    plot_ranking(st, px, df, '__system.submitterName') 

    # Streamlit App
    st.subheader("4. Localizações Geográficas")
    plot_mapa(st, px, df, 'localizacao.coordinates')


    # Gráfico da pergunta principal
    st.header("Distribuição das Respostas por Município")
    st.subheader(f"5. Visualização: {titulo}")
    # Pergunta principal
    plot_pergunta(st, px, df, coluna, None)

    # Verifica se há pergunta vinculada
    pergunta_vinculada = perguntas_vinculadas.get(coluna)
    if pergunta_vinculada:
        st.info("Apresetamos a seguir a distribuição das respostas para quem disse sim à pergunta acima.")
        st.subheader(f"5.1 Visualização: {mapa_perguntas.get(pergunta_vinculada,pergunta_vinculada)}")
        plot_pergunta(st, px, df, pergunta_vinculada, valor_excluir="Não")


else:
    st.error("Erro ao obter o token de autenticação. Verifique suas credenciais.")
