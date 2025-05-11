import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from util import obter_token, aplicar_mapeamentos, plot_pergunta, mapa_perguntas

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
    pergunta = st.sidebar.selectbox("Pergunta", [
        ('aspectos_sociodemograficos.idade', 'Qual a idade?'),
        ('aspectos_sociodemograficos.genero', 'Qual o seu gênero?'),
        ('aspectos_sociodemograficos.cor_etnia', 'Qual a sua cor ou etnia?'),
        ('aspectos_sociodemograficos.escolaridade', 'Qual o seu nível de escolaridade?'),
        ('aspectos_sociodemograficos.estado_civil', 'Qual o seu estado civil?'),
        ('aspectos_sociodemograficos.mora_conjuge', 'Mora com cônjuge ou parceiro(a)?'),
        ('aspectos_sociodemograficos.povo_tradicional', 'Pertence a povo ou comunidade tradicional?'),
        ('aspectos_sociodemograficos.tipo_comunidade', 'Qual o tipo de comunidade?'),
        ('trabalho_renda.trabalho_remunerado', 'Tem trabalho remunerado?'),
        ('trabalho_renda.trabalho_nao_remunerado', 'Faz trabalho não remunerado?'),
        ('trabalho_renda.tipo_trabalho_nao_remunerado', 'Qual o tipo de trabalho não remunerado?'),
        ('trabalho_renda.renda_familiar_mensal', 'Qual a renda familiar mensal?'),
        ('trabalho_renda.renda_individual_mensal', 'Qual a sua renda mensal individual?'),
        ('trabalho_renda.fonte_renda', 'Qual a principal fonte de renda?'),
        ('trabalho_renda.dependentes_renda', 'Quantas pessoas dependem da sua renda?'),
        ('moradia_acesso_transporte.material_paredes', 'Qual o material das paredes da casa?'),
        ('moradia_acesso_transporte.outro_material_text', 'Qual outro material (se houver)?'),
        ('moradia_acesso_transporte.pessoas_moradia', 'Quantas pessoas moram com você?'),
        ('moradia_acesso_transporte.quantidade_comodos', 'Quantos cômodos tem a residência?'),
        ('moradia_acesso_transporte.locomocao_diaria', 'Qual o meio de locomoção mais usado no dia a dia?'),
        ('moradia_acesso_transporte.outros_qual', 'Qual outro meio de locomoção (se houver)?'),
        ('moradia_acesso_transporte.acesso_internet', 'Tem acesso à internet?'),
        ('moradia_acesso_transporte.horas_internet', 'Quantas horas usa internet por dia?'),
        ('moradia_acesso_transporte.dispositivos_eletronicos', 'Tem dispositivos eletrônicos em casa?'),
        ('moradia_acesso_transporte.tipo_dispositivo', 'Quais dispositivos possui?'),
        ('apoio_social.apoio_proximo', 'Recebe apoio de alguém próximo?'),
        ('apoio_social.apoio_proximo_quem', 'Quem oferece esse apoio?'),
        ('apoio_social.cuidador_pago', 'Tem cuidador pago?'),
        ('apoio_social.cuidador_pago_quem', 'Quem é o cuidador pago?'),
        ('apoio_social.cuidador_nao_pago', 'Tem cuidador não pago?'),
        ('apoio_social.cuidador_nao_pago_quem', 'Quem é o cuidador não pago?'),
        ('apoio_social.cadastro_cras', 'Está cadastrado no CRAS?'),
        ('apoio_social.tipo_servico_cras', 'Quais serviços utiliza no CRAS?'),
        ('condicao_geral_saude.avaliacao_saude', 'Como avalia sua saúde?'),
        ('condicao_geral_saude.agente_saude_visita', 'Recebe visita de agente de saúde?'),
        ('condicao_geral_saude.frequencia_visita', 'Com que frequência o agente visita?'),
        ('condicao_geral_saude.pcd', 'É pessoa com deficiência (PCD)?'),
        ('condicao_geral_saude.tipo_deficiencia', 'Qual o tipo de deficiência?'),
        ('condicao_geral_saude.inseguranca_alimentar', 'Vivencia insegurança alimentar?'),
        ('condicao_geral_saude.avaliacao_saude_mental', 'Como avalia sua saúde mental?')
    ], format_func=lambda x: x[1])

    coluna, titulo = pergunta
    st.header(f"Total Geral de Respostas: {len(df)}")

    # Layout principal
    col1, col2 = st.columns(2)
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

    # Gráfico da pergunta principal
    st.header("3. Distribuição das Respostas por Município")
    st.subheader(f"Visualização: {titulo}")


    # Pergunta principal
    plot_pergunta(st, px, df, coluna, None)

    # Verifica se há pergunta vinculada
    pergunta_vinculada = perguntas_vinculadas.get(coluna)
    if pergunta_vinculada:
        st.subheader(f"Visualização: {mapa_perguntas.get(pergunta_vinculada,pergunta_vinculada)}")
        plot_pergunta(st, px, df, pergunta_vinculada, valor_excluir="Não")
else:
    st.error("Erro ao obter o token de autenticação. Verifique suas credenciais.")
