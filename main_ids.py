import streamlit as st
import pandas as pd
from util import ober_dados_odk

st.set_page_config("🆔entificador Único  🔑",layout="wide")


df = ober_dados_odk()
df['identificador_unico'] = df.index+1

# iniciar com um emoji de uma chave 🔑
st.subheader("🆔entificador Único  🔑")
st.markdown("---")

cols = st.columns([2,3])

with cols[0]:
    submitter_name = st.selectbox('Agente', sorted(df['__system.submitterName'].unique()))

with cols[1]:
    nome_pessoa_idosa = st.selectbox('Pessoa Idosa', sorted(df[df['__system.submitterName'] == submitter_name]['nome_pessoa_idosa'].unique()))


df_filter = df[(df['__system.submitterName'] == submitter_name) & (df['nome_pessoa_idosa'] == nome_pessoa_idosa)]

cols = st.columns([2,8])

cols[0].metric(
    "Identificador Único",
    f"{df_filter['identificador_unico'].values[0]}",
    help="Use este identificador para o proximo questionário.",
    border=True
)

cols[1].metric(
    f"{df_filter['bairro'].values[0]}",
    f"{df_filter['endereco'].values[0]}",
    help="Endereco onde a pessoa idosa reside.",
    border=True
)

st.dataframe(df_filter[[
               'identificador_unico',
               'Municipio',
               'nome_pessoa_idosa', 
               'bairro',
               'endereco',
               'nome_agente',
            #    '__system.submitterName' 
               ]], hide_index=True, use_container_width=True)


st.markdown("---")
bairros = sorted(df[df['__system.submitterName'] == submitter_name]['bairro'].unique())
bairros = ['Todos'] + bairros
bairro = st.selectbox('Bairro', bairros)

if bairro == 'Todos':
    df_bairro = df[df['__system.submitterName'] == submitter_name]
else:
    df_bairro = df[(df['bairro'] == bairro) & (df['__system.submitterName'] == submitter_name)]

st.write(f"{bairro}/{df_bairro['Municipio'].values[0]}")
st.dataframe(df_bairro[[
               'identificador_unico',
               'Municipio',
               'nome_pessoa_idosa', 
               'bairro',
               'endereco',
               'nome_agente',
            #    '__system.submitterName' 
               ]], hide_index=True, use_container_width=True)