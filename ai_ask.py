import streamlit as st
import pandas as pd
import sqlite3
from sqlite3 import Connection
from openai import OpenAI
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import re
from dateutil.parser import parse
import traceback

client = OpenAI(api_key=st.secrets.api["openai_key"])

footer_html = """
    <div class="footer">
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f0f2f6;
            padding: 10px 20px;
            text-align: center;
        }
        .footer a {
            color: #4a4a4a;
            text-decoration: none;
        }
        .footer a:hover {
            color: #3d3d3d;
            text-decoration: underline;
        }
    </style>
        Connect with me on <a href="https://twitter.com/alexarsentiev" target="_blank">Twitter</a>. 
        If you like this app, consider <a href="https://www.buymeacoffee.com/arsentiev" target="_blank">buying me a coffee</a> ☕
    </div>
"""

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://i.postimg.cc/4xgNnkfX/Untitled-design.png");
background-size: cover;
background-position: center center;
background-repeat: no-repeat;
background-attachment: local;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
</style>
"""


def create_connection(db_name: str) -> Connection:
    conn = sqlite3.connect(db_name)
    return conn

def run_query(conn: Connection, query: str) -> pd.DataFrame:
    df = pd.read_sql_query(query, conn)
    return df

def create_table(conn: Connection, df: pd.DataFrame, table_name: str):
    df.to_sql(table_name, conn, if_exists="replace", index=False)


def generate_gpt_reponse(gpt_input, max_tokens, temperature=0):
    """function to generate gpt response"""
    completion = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "user", "content": gpt_input},
        ]
    )
    gpt_response = completion.choices[0].message.content.strip()
    return gpt_response


def extract_code(gpt_response):
    """function to extract code and sql query from gpt response"""

    if "```" in gpt_response:
        # extract text between ``` and ```
        pattern = r'```(.*?)```'
        code = re.search(pattern, gpt_response, re.DOTALL)
        extracted_code = code.group(1)

        # remove python from the code (weird bug)
        extracted_code = extracted_code.replace('python', '')
        extracted_code = extracted_code.replace('sql', '')

        return extracted_code
    else:
        return gpt_response


# wide layout
st.set_page_config(page_icon="🤖", page_title="Ask CSV")
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("ASK CSV 🤖 (GPT-powered)")
st.header('Use Natural Language to Query Your Data')

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info(f"""
                👆 Upload a .csv file first. Sample to try: [sample_data.csv](https://docs.google.com/spreadsheets/d/e/2PACX-1vTeB7_jzJtacH3XrFh553m9ahL0e7IIrTxMhbPtQ8Jmp9gCJKkU624Uk1uMbCEN_-9Sf7ikd1a85wIK/pub?gid=0&single=true&output=csv)
            """)

elif uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Apply the custom function and convert date columns
    for col in df.columns:
        # check if a column name contains date substring
        if 'date' in col.lower():
            df[col] = pd.to_datetime(df[col])
            # remove timestamp
            #df[col] = df[col].dt.date

    # reset index
    df = df.reset_index(drop=True)

    # replace space with _ in column names
    df.columns = df.columns.str.replace(' ', '_')

    cols = df.columns
    cols = ", ".join(cols)

    with st.expander("Preview of the uploaded file"):
        st.table(df.head())

    # conn = create_connection(":memory:")
    conn = create_connection("db.sqlite")
    table_name = "my_table"
    create_table(conn, df, table_name)


    selected_mode = st.selectbox("O que você gostaria de fazer?", 
                                 ["Perguntar aos dados?", 
                                  "Criar uma visualização [beta]?",
                                  "Gerar insights sobre os dados?"])
 
    if selected_mode == 'Perguntar aos dados?':

        user_input = st.text_area("Escreva uma pergunta concisa e clara sobre seus dados. Por exemplo: Qual é o total de questionários por agente?", value='Qual é o total de questionários por agente?')
        if st.button("Obter Resposta"):
           with st.spinner("Consultando os dados..."):
            try:
                # create gpt prompt
                gpt_input = 'Escreva uma consulta SQL SQLite com base nesta pergunta: {}. ' \
                            'O nome da tabela é my_table e ela possui as seguintes colunas: {}.' \
                            ' Retorne apenas a consulta SQL e nada mais.'.format(user_input, cols)

                query = generate_gpt_reponse(gpt_input, max_tokens=200)
                query_clean = extract_code(query)
                result = run_query(conn, query_clean)

                with st.expander("SQL query used"):
                    st.code(query_clean)

                # if result df has one row and one column
                if result.shape == (1, 1):
                    # get the value of the first row of the first column
                    val = result.iloc[0, 0]
                    # write one liner response
                    st.subheader('Your response: {}'.format(val))
                else:
                    st.subheader("Your result:")
                    st.table(result)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                # st.error('Oops, there was an error :( Please try again with a different question.')

    elif selected_mode == 'Criar uma visualização [beta]?':
        user_input = st.text_area(
            "Explique brevemente o que você deseja visualizar a partir dos seus dados. " \
            "Por exemplo: Exibir as idades por faixas de 10 em 10 anos", value='Exibir as idades por faixas de 10 em 10 anos')

        if st.button("Criar uma visualização [beta]"): 
          with st.spinner("Criando visualização..."):
            try:
                # create gpt prompt
                gpt_input = 'Escreva um código em Python usando Plotly para atender à seguinte solicitação: {} ' \
                            'Use o df que possui as seguintes colunas: {}. ' \
                            'Não use o argumento animation_group e retorne apenas o código sem declarações de importação, ' \
                            'use fundo transparente, os dados já foram carregados na variável df'.format(user_input, cols)

                gpt_response = generate_gpt_reponse(gpt_input, max_tokens=1500)
                extracted_code = extract_code(gpt_response)
                extracted_code = extracted_code.replace('fig.show()', 'st.plotly_chart(fig)')

                with st.expander("Code used"):
                    st.code(extracted_code)

                # execute code
                exec(extracted_code)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                #st.write(traceback.print_exc())
                #st.error('Oops, there was an error :( Please try again with a different question.')

    elif selected_mode == 'Gerar insights sobre os dados?':
        prompt_base = f"""
            Você é um assistente de dados. Abaixo estão os dados de um DataFrame em formato CSV.
            Gere um resumo inteligente sobre:
                - O que você observa nesses dados.
                - Tendências, padrões, valores discrepantes ou informações importantes.
                - Sugestões de análise que poderiam ser feitas.
                - Se possível, gere perguntas que poderiam ser respondidas com esses dados.
            Aqui está uma amostra aleatória dos dados:
            {df.sample(20).to_csv(index=False)}

            Responda em português, de forma clara e detalhada.
        """
        if st.button("🔮 Gerar Insights"):
            with st.spinner("Analisando os dados com IA..."):
                try:
                    insights = generate_gpt_reponse(prompt_base, max_tokens=1000, temperature=0.2)
                    st.success("✅ Insights gerados com sucesso!")
                    st.markdown(insights)
                except Exception as e:
                    print(e)
                    st.error(f"Erro ao gerar insights: {e}")



# footer
st.markdown(footer_html, unsafe_allow_html=True)