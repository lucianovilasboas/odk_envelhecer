import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from util import obter_token, aplicar_mapeamentos, plot_mapa, plot_pergunta, mapa_perguntas, lista_perguntas
from util import plot_ranking
from util import calcular_metricas, exibe_metricas, calcular_semana, calcular_metricas_gerais, exibe_metricas_gerais
from util import fn_ajusta_nome

st.set_page_config(layout="wide")

_, image_col, _ = st.columns([1,4,1])

with image_col:
    # st.image("Envelhecer_nos_territrios.png", width=200)
    st.image("ENVELHECER - IFMG - PONTE NOVA_.png")
        
st.html("""<h1 style='text-align: center; font-size:35px; margin: 0px'>Dashboard - Projeto Envelhecer Nos Territórios</h1>""")

st.markdown("""___""")

odk_token = obter_token(st)

if odk_token:
    headers = {"Authorization": f"Bearer {odk_token}"}
    url_dados = st.secrets.odk["url_dados"]
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

    df["__system.submitterName"] = df["__system.submitterName"].apply(fn_ajusta_nome)

    df = aplicar_mapeamentos(df)

    perguntas_vinculadas = {
        'aspectos_sociodemograficos.povo_tradicional':'aspectos_sociodemograficos.tipo_comunidade',
        'moradia_acesso_transporte.dispositivos_eletronicos': 'moradia_acesso_transporte.tipo_dispositivo',
        'apoio_social.cadastro_cras': 'apoio_social.tipo_servico_cras',
        'condicao_geral_saude.pcd': 'condicao_geral_saude.tipo_deficiencia',
        'trabalho_renda.trabalho_nao_remunerado': 'trabalho_renda.tipo_trabalho_nao_remunerado',
    }

    # Progresso
    semana = calcular_semana(days=5)
    st.subheader(f"Semana: {semana["inicio_semana"].strftime('%d/%m/%Y')} à {semana["fim_semana"].strftime('%d/%m/%Y')}.")

    metricas_gerais = calcular_metricas_gerais(st, df, semana)
    exibe_metricas_gerais(st, metricas_gerais) 

    # col0 = st.container()
    # col0.metric(
    #     "Total de Questionários Aplicados",
    #     f"{df.shape[0]}"
    # )
    # col0.markdown("""___""")
    # st.subheader("Total de Respostas por Município")
    
    municipios = st.selectbox("Municipio(s)", df["Municipio"].unique(), index=0)
    metricas = calcular_metricas(st, df,semana, municipios)
    exibe_metricas(st, metricas) 

    # Layout principal
    col1, col2 = st.columns([2, 5])
    with col1:
        st.subheader("1. Total de Questionários por Município")
        df_municipio = df.groupby("Municipio").size().reset_index(name='Total_Respostas')
        fig_total = px.bar(df_municipio, x="Municipio", y="Total_Respostas", text_auto=True)
        fig_total.update_layout(yaxis_title="Total de Respostas", xaxis_title="Município")
        st.plotly_chart(fig_total, use_container_width=True)

    with col2:
        # st.subheader("2. Evolução dos Questionários ao Longo do Tempo")
        # df_grouped = df.groupby(["Municipio", "data"]).size().reset_index(name="Total_Respostas")
        # fig_evolucao = px.line(df_grouped, x="data", y="Total_Respostas", color="Municipio", markers=True)
        # fig_evolucao.update_layout(xaxis_title="Data", yaxis_title="Número de Respostas")
        # st.plotly_chart(fig_evolucao, use_container_width=True)

        st.subheader("2. Evolução Acumulada dos Questionários ao Longo do Tempo")
        # Agrupamento por Município e Data
        df_grouped = df.groupby(["Municipio", "data"]).size().reset_index(name="Total_Respostas")
        # Ordenando por data dentro de cada município para garantir o acumulado correto
        df_grouped = df_grouped.sort_values(by=["Municipio", "data"])
        # Calculando o acumulado por município
        df_grouped["Respostas_Acumuladas"] = df_grouped.groupby("Municipio")["Total_Respostas"].cumsum()
        # Plotando o gráfico
        fig_evolucao = px.line(
            df_grouped, 
            x="data", 
            y="Respostas_Acumuladas", 
            color="Municipio", 
            markers=True,
            # title="Evolução Acumulada dos Questionários ao Longo do Tempo"
        )
        fig_evolucao.update_layout(
            xaxis_title="Data", 
            yaxis_title="Respostas Acumuladas"
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)



    # Graficos de rancking por agente 
    st.subheader("3. Questionários Aplicados por Agente")
    plot_ranking(st, px, df, '__system.submitterName') 

    # Streamlit App
    st.subheader("4. Questionários Aplicados por Localização Geográfica")
    plot_mapa(st, px, df, 'localizacao.coordinates')


    # Gráfico da pergunta principal
    st.header("Respostas por Município")

    pergunta = st.selectbox("Pergunta", lista_perguntas, format_func=lambda x: x[1])

    coluna, titulo = pergunta

    st.subheader(f"5. Visualização: {titulo}")
    # Pergunta principal
    plot_pergunta(st, px, df, coluna, None)

    # Verifica se há pergunta vinculada
    pergunta_vinculada = perguntas_vinculadas.get(coluna)
    if pergunta_vinculada:
        st.info("Apresetamos a seguir a distribuição das respostas para quem disse sim à pergunta acima.")
        st.subheader(f"5.1 Visualização: {mapa_perguntas.get(pergunta_vinculada,pergunta_vinculada)}")
        plot_pergunta(st, px, df, pergunta_vinculada, valor_excluir="Não")


    # st.markdown("""___""")
    # st.subheader("6. Dataframe e download dos dados")
    # st.dataframe(df)
    # csv = df.to_csv(index=False).encode('utf-8')
    # st.download_button(
    #     label="Download CSV",
    #     data=csv,
    #     file_name='dados_envelhecer.csv',
    #     mime='text/csv',
    # )

    st.markdown("""___""")
    st.caption("Desenvolvido com ❤️ por [Luciano Espiridiao](luciano.espiridiao@ifmg.edu.br). 2025 - Todos os direitos reservados.")
else:
    st.error("Erro ao obter o token de autenticação. Verifique suas credenciais.")
