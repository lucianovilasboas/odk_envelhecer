import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from util import calcular_semana_domingo
from util import plot_mapa, plot_pergunta
from util import plot_ranking
from util import calcular_metricas, exibe_metricas, calcular_metricas_gerais, exibe_metricas_gerais
from util import ober_dados_odk, gerar_descricao_por_ia_gpt, gerar_descricao_por_ia_gmini
from util import mapa_perguntas, lista_perguntas, perguntas_vinculadas
from util import plot_violin

st.set_page_config(layout="wide")

_, image_col, _ = st.columns([1,4,1])

with image_col:
    # st.image("Envelhecer_nos_territrios.png", width=200)
    st.image("ENVELHECER - IFMG - PONTE NOVA_.png")
        
st.html("""<h1 style='text-align: center; font-size:33px; margin: 0px'>Dashboard</h1>""")
# st.markdown("""___""")

df = ober_dados_odk()

if df is not None:

    # Progresso
    semana = calcular_semana_domingo()
    st.subheader(f"Semana: {semana["inicio_semana"].strftime('%d/%m/%Y')} à {semana["fim_semana"].strftime('%d/%m/%Y')}.")

    metricas_gerais = calcular_metricas_gerais(st, df, semana)
    exibe_metricas_gerais(st, metricas_gerais) 

    
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


    if coluna == "aspectos_sociodemograficos.idade":
        plot_violin(st, px, df, coluna)
    
    # Verifica se há pergunta vinculada
    pergunta_vinculada = perguntas_vinculadas.get(coluna)
    if pergunta_vinculada:
        st.info("Apresetamos a seguir a distribuição das respostas para quem disse sim à pergunta acima.")
        st.subheader(f"5.1 Visualização: {mapa_perguntas.get(pergunta_vinculada,pergunta_vinculada)}")
        plot_pergunta(st, px, df, pergunta_vinculada, valor_excluir="Não")

    # if st.button(f"🤖 Forneça-me uma breve análise sobre essa questão: **{titulo}**"):
    #     with st.spinner("🤖 Analisando os dados com IA..."):    
    #         analise = gerar_descricao_por_ia_gmini(coluna, df)
    #         st.markdown("""___\n### 🤖 Análise gerada""")
    #         st.info(f"{analise}")


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
