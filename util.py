from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt
import pandas as pd

# --- Autenticação Automática ---
def obter_token(st):
    url = st.secrets["odk"]["url_session"]
    dados = {
        "email": st.secrets["odk"]["email"],
        "password": st.secrets["odk"]["passw"]
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


lista_perguntas = [
        ('aspectos_sociodemograficos.idade', 'Qual a idade?'),
        ('aspectos_sociodemograficos.genero', 'Qual o seu gênero?'),
        ('aspectos_sociodemograficos.cor_etnia', 'Qual a sua cor ou etnia?'),
        ('aspectos_sociodemograficos.escolaridade', 'Qual o seu nível de escolaridade?'),
        ('aspectos_sociodemograficos.estado_civil', 'Qual o seu estado civil?'),
        ('aspectos_sociodemograficos.mora_conjuge', 'Mora com cônjuge ou parceiro(a)?'),
        ('aspectos_sociodemograficos.povo_tradicional', '*Pertence a povo ou comunidade tradicional?'),
        ('aspectos_sociodemograficos.tipo_comunidade', 'Qual o tipo de comunidade?'),
        ('trabalho_renda.trabalho_remunerado', 'Tem trabalho remunerado?'),
        ('trabalho_renda.trabalho_nao_remunerado', '*Faz trabalho não remunerado?'),
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
        ('moradia_acesso_transporte.dispositivos_eletronicos', '*Tem dispositivos eletrônicos em casa?'),
        ('moradia_acesso_transporte.tipo_dispositivo', 'Quais dispositivos possui?'),
        ('apoio_social.apoio_proximo', 'Recebe apoio de alguém próximo?'),
        ('apoio_social.apoio_proximo_quem', 'Quem oferece esse apoio?'),
        ('apoio_social.cuidador_pago', 'Tem cuidador pago?'),
        ('apoio_social.cuidador_pago_quem', 'Quem é o cuidador pago?'),
        ('apoio_social.cuidador_nao_pago', 'Tem cuidador não pago?'),
        ('apoio_social.cuidador_nao_pago_quem', 'Quem é o cuidador não pago?'),
        ('apoio_social.cadastro_cras', '*Está cadastrado no CRAS?'),
        ('apoio_social.tipo_servico_cras', 'Quais serviços utiliza no CRAS?'),
        ('condicao_geral_saude.avaliacao_saude', 'Como avalia sua saúde?'),
        ('condicao_geral_saude.agente_saude_visita', 'Recebe visita de agente de saúde?'),
        ('condicao_geral_saude.frequencia_visita', 'Com que frequência o agente visita?'),
        ('condicao_geral_saude.pcd', '*É pessoa com deficiência (PCD)?'),
        ('condicao_geral_saude.tipo_deficiencia', 'Qual o tipo de deficiência?'),
        ('condicao_geral_saude.inseguranca_alimentar', 'Vivencia insegurança alimentar?'),
        ('condicao_geral_saude.avaliacao_saude_mental', 'Como avalia sua saúde mental?')
]

 
# --- Mapeamentos de Perguntas ---
mapa_perguntas = {
    'aspectos_sociodemograficos.tipo_comunidade': 'Qual o tipo de comunidade?',
    'trabalho_renda.tipo_trabalho_nao_remunerado': 'Qual o tipo de trabalho não remunerado?',
    'moradia_acesso_transporte.tipo_dispositivo': 'Quais dispositivos possui?',
    'apoio_social.tipo_servico_cras': 'Quais serviços utiliza no CRAS?',
    'condicao_geral_saude.tipo_deficiencia': 'Qual o tipo de deficiência?',
}


# --- Mapeamentos de Respostas ---
mapa_sim_nao = {
    '1': 'Sim',
    '2': 'Não',
    '3': 'NS/NR'
}

mapa_genero = {
    '1': 'Masculino',
    '2': 'Feminino',
    '3': 'Não binárie',
    '4': 'Outro',
    '5': 'NS/NR'
}

mapa_etnia = {
    '1': 'Branca',
    '2': 'Amarela',
    '3': 'Parda',
    '4': 'Preta',
    '5': 'Indígena',
    '6': 'NS/NR'
}

mapa_escolaridade = {
    '1': 'Não alfabetizado',
    '2': 'Ensino fundamental incompleto',
    '3': 'Ensino fundamental completo',
    '4': 'Ensino médio incompleto',
    '5': 'Ensino médio completo',
    '6': 'Ensino superior incompleto',
    '7': 'Ensino superior completo',
    '8': 'Pós-graduação completa',
    '9': 'Pós-graduação incompleta',
    '10': 'NS/NR'
}

mapa_estado_civil = {
    '1': 'Solteiro',
    '2': 'Casado',
    '3': 'Viúvo',
    '4': 'Divorciado/separado',
    '5': 'União estável',
    '6': 'NS/NR'
}

mapa_trabalho_nao_remunerado = {
    '1': 'Voluntário',
    '2': 'Reprodutivo/doméstico',
    '3': 'Cuidado com netos, filhos e etc',
    '4': 'Outro',
    'None': 'Não'
}

mapa_renda_familiar_mensal = {
    '1': 'Sem renda',
    '2': 'Até ½ salário mínimo',
    '3': '1 salário mínimo',
    '4': 'Acima de 1 e até 2 salários mínimos',
    '5': 'Acima de 2 até 4 salários mínimos',
    '6': 'Acima de 4 salários mínimos',
    '7': 'NS/NR'
}

mapa_renda_individual_mensal = mapa_renda_familiar_mensal.copy()

mapa_fonte_renda = {
    '1': 'Salário/CLT',
    '2': 'Autônomo',
    '3': 'Aposentadoria',
    '4': 'Pensão alimentícia',
    '5': 'Pensão por viuvez',
    '6': 'Aluguel ou arrendamento',
    '7': 'Seguro-desemprego',
    '8': 'Benefício de Prestação Continuada (BPC/LOAS)',
    '9': 'Bolsa Família',
    '10': 'Outros programas sociais do governo',
    '11': 'Rendimentos de qualquer aplicação financeira',
    '12': 'Dependente da família ou de responsáveis legais',
    '13': 'NS/NR'
}

mapa_material_paredes = {
    '1': 'Alvenaria com revestimento ou taipa revestida',
    '2': 'Alvenaria sem revestimento',
    '3': 'Taipa sem revestimento',
    '4': 'Madeira apropriada para construção (aparelhada)',
    '5': 'Madeira aproveitada',
    '6': 'Outro material',
    '7': 'NS/NR'
}

mapa_locomocao_diaria = {
    '1': 'Ônibus',
    '2': 'Veículo próprio',
    '3': 'Táxi/Aplicativo',
    '4': 'Veículo de conhecidos',
    '5': 'Metrô/Trem',
    '6': 'Motocicleta',
    '7': 'Bicicleta',
    '8': 'A pé',
    '9': 'Outros',
    '10': 'NS/NR'
}

mapa_avaliacao_saude = {
    '1': 'Muito Ruim',
    '2': 'Ruim',
    '3': 'Regular',
    '4': 'Boa',
    '5': 'Muito Boa',
    '6': 'NS/NR'
}

mapa_avaliacao_saude_mental = mapa_avaliacao_saude.copy()

mapa_tipo_comunidade = {
    '1': 'Indígena',
    '2': 'Quilombola',
    '3': 'Ribeirinha/o',
    '4': 'Terreiro/comunidade de matriz africana',
    '5': 'Cigano',
    '6': 'Pescadores artesanais',
    '7': 'Extrativista',
    '8': 'Benzedeiros',
    '9': 'Comunidades de fundos e fechos de pasto',
    '10': 'Outros',
    'None': 'Não'
}

mapa_dispositivos_eletronicos = mapa_sim_nao.copy()

mapa_tipo_dispositivo = {
    '1': 'Celular',
    '2': 'Tablet',
    '3': 'Notebook',
    '4': 'Outros',
    '5': 'NS/NR',
    'None': 'Não'
}

mapa_cadastro_cras = mapa_sim_nao.copy()

mapa_tipo_servico_cras = {
    '1': 'Bolsa Família',
    '2': 'BPC/LOAS',
    '3': 'Serviço de convivência',
    '4': 'Cesta básica',
    '5': 'Vale-gás',
    '6': 'NS/NR',
    'None': 'Não'
}

mapa_tipo_deficiencia = {
    '1': 'Intelectual',
    '2': 'Física',
    '3': 'Auditiva',
    '4': 'Visual',
    '5': 'Múltipla',
    '6': 'TEA (Transtorno do Espectro Autista)',
    '7': 'NS/NR',
    'None': 'Não'
}

mapa_povo_tradicional = mapa_sim_nao.copy()

mapa_frequencia_visita = {
    '1': 'Diária',
    '2': 'Semanal',
    '3': 'Quinzenal',
    '4': 'Mensal',
    '5': 'Irregular',
    '6': 'NS/NR'
}

mapa_respondente = {
    '1': 'A própria pessoa idosa',
    '2': 'Outra pessoa.'
}


def aplicar_mapeamentos(df):
    mapeamentos = {
        'aspectos_sociodemograficos.genero': mapa_genero,
        'aspectos_sociodemograficos.cor_etnia': mapa_etnia,
        'aspectos_sociodemograficos.escolaridade': mapa_escolaridade,
        'aspectos_sociodemograficos.estado_civil': mapa_estado_civil,
        'aspectos_sociodemograficos.mora_conjuge': mapa_sim_nao,
        'aspectos_sociodemograficos.povo_tradicional': mapa_povo_tradicional,
        'aspectos_sociodemograficos.tipo_comunidade': mapa_tipo_comunidade,

        'trabalho_renda.trabalho_remunerado': mapa_sim_nao,
        'trabalho_renda.trabalho_nao_remunerado': mapa_sim_nao,
        'trabalho_renda.tipo_trabalho_nao_remunerado': mapa_trabalho_nao_remunerado,
        'trabalho_renda.renda_familiar_mensal': mapa_renda_familiar_mensal,
        'trabalho_renda.renda_individual_mensal': mapa_renda_individual_mensal,
        'trabalho_renda.fonte_renda': mapa_fonte_renda,

        'moradia_acesso_transporte.material_paredes': mapa_material_paredes,
        'moradia_acesso_transporte.locomocao_diaria': mapa_locomocao_diaria,
        'moradia_acesso_transporte.acesso_internet': mapa_sim_nao,
        'moradia_acesso_transporte.dispositivos_eletronicos': mapa_dispositivos_eletronicos,
#        'moradia_acesso_transporte.tipo_dispositivo': mapa_tipo_dispositivo,

        'apoio_social.apoio_proximo': mapa_sim_nao,
        'apoio_social.cuidador_pago': mapa_sim_nao,
        'apoio_social.cuidador_nao_pago': mapa_sim_nao,
        'apoio_social.cadastro_cras': mapa_cadastro_cras,
#        'apoio_social.tipo_servico_cras': mapa_tipo_servico_cras,

        'condicao_geral_saude.avaliacao_saude': mapa_avaliacao_saude,
        'condicao_geral_saude.agente_saude_visita': mapa_sim_nao,
        'condicao_geral_saude.frequencia_visita': mapa_frequencia_visita,
        'condicao_geral_saude.pcd': mapa_sim_nao,
#        'condicao_geral_saude.tipo_deficiencia': mapa_tipo_deficiencia,
        'condicao_geral_saude.inseguranca_alimentar': mapa_sim_nao,
        'condicao_geral_saude.avaliacao_saude_mental': mapa_avaliacao_saude_mental
    }

    for coluna, mapa in mapeamentos.items():
        if coluna in df.columns:
            df[coluna] = df[coluna].astype(str).replace(mapa)

    df = mapear_respostas_multiplas(df)
    return df



def mapear_respostas_multiplas(df):
    """
    Mapeia as respostas de uma coluna com múltiplas opções de resposta.
    """
    mapeamentos = {
        'moradia_acesso_transporte.tipo_dispositivo': mapa_tipo_dispositivo,
        'apoio_social.tipo_servico_cras': mapa_tipo_servico_cras,
        'condicao_geral_saude.tipo_deficiencia': mapa_tipo_deficiencia,
    }

    for coluna, mapa in mapeamentos.items():
        if coluna in df.columns:
            # Função para aplicar o mapeamento
            def mapear_multiplas_escolhas(valor):
                if pd.isna(valor) or valor == '':
                    return 'NS/NR'
                codigos = valor.strip().split()
                descricoes = [mapa.get(codigo, "Não") for codigo in codigos]
                return ', '.join(descricoes)
            # Aplica ao DataFrame
            df[coluna] = df[coluna].astype(str).apply(mapear_multiplas_escolhas)
        
    return df
    


# def plot_pergunta(st, px,  df, coluna, valor_excluir):
#     df_bar = df.groupby(["Municipio", coluna]).size().reset_index(name="count")
#     if valor_excluir:
#         df_bar = df_bar[df_bar[coluna] != valor_excluir]

#     df_bar["percentual"] = df_bar.groupby("Municipio")["count"].transform(lambda x: x / x.sum()) * 100
#     fig_bar = px.bar(
#         df_bar, x="Municipio", y="percentual", color=coluna,
#         barmode="stack", labels={"percentual": "Proporção"},
#         title=f"{coluna}"
#     )
#     st.plotly_chart(fig_bar, use_container_width=True)


def plot_ranking(st, px, df, coluna):
    df_agente = df.groupby([coluna])['__id'].count().reset_index().sort_values('__id', ascending=True)
    # Cria o gráfico de barras horizontal
    fig = px.bar(
        df_agente,
        x="__id",
        y=coluna,
        orientation="h",
        title="Questionários por Agentes",
        labels={
            coluna: "Nome do Agente",
            "__id": "Número de Questionários Aplicados"
        }
    )

    # Ajusta layout para melhor leitura
    fig.update_layout(
        margin=dict(l=200, r=20, t=50, b=20),
        yaxis=dict(tickfont=dict(size=10))
    )

    # Exibe no Streamlit
    st.plotly_chart(fig, use_container_width=True)     

def idade_para_faixa(idade, idade_min=50, idade_max=110, passo=10):
    """
    Converte uma idade em uma faixa etária.

    Parâmetros:
    - idade: valor da idade.
    - idade_min: idade mínima considerada na faixa (default 60).
    - idade_max: idade máxima considerada na faixa (default 100).
    - passo: intervalo das faixas (default 5).

    Retorna:
    - Uma string com a faixa etária (ex.: '60-64') ou 'Fora da faixa' se estiver fora dos limites.
    """
    if pd.isna(idade):
        return 'Indefinido'
    if idade < idade_min or idade > idade_max:
        return 'Fora da faixa'

    inicio_faixa = idade_min + ((idade - idade_min) // passo) * passo
    fim_faixa = inicio_faixa + passo - 1
    return f'{inicio_faixa}-{fim_faixa}'

def plot_pergunta(st, px, df, coluna, valor_excluir):
    df_bar = df.groupby(["Municipio", coluna]).size().reset_index(name="count")
    if valor_excluir:
        df_bar = df_bar[df_bar[coluna] != valor_excluir]

    if coluna == 'aspectos_sociodemograficos.idade':
        # Converte idades para faixas etárias
        df_bar['Faixa Etaria'] = df_bar[coluna].apply(lambda x: idade_para_faixa(x))
        df_bar = df_bar.groupby(["Municipio", "Faixa Etaria"]).sum().reset_index()
        coluna = 'Faixa Etaria'


    df_bar["percentual"] = df_bar.groupby("Municipio")["count"].transform(lambda x: x / x.sum()) * 100

    totals = df_bar.groupby("Municipio")["count"].sum().reset_index()
    totals_dict = dict(zip(totals['Municipio'], totals['count']))

    # Atualiza os nomes dos municípios com o total
    df_bar["Municipio_total"] = df_bar["Municipio"].apply(lambda x: f"{x} ({totals_dict[x]})")

    # Gerar gráfico com percentual com duas casas decimais e hover personalizado
    fig_bar = px.bar(
        df_bar,
        x="Municipio_total",
        y="percentual",
        color=coluna,
        barmode="stack",
        labels={"percentual": "Proporção (%)", "Municipio_total": "Municipio"},
        title=f"{mapa_perguntas.get(coluna, coluna)}",
        hover_data={
            "Municipio_total": True,
            coluna: True,
            "percentual": ":.2f",
            "count": True
        }
    )

    fig_bar.update_traces(
        hovertemplate= "<b>%{x}</b><br>"
                      + f"N° respostas: %{{customdata[1]}}<br>"
                      + "Percentual: %{y:.1f}%<br>"
    )

    # Ajustar fonte da legenda e dos títulos dos eixos
    fig_bar.update_layout(
        legend=dict(font=dict(size=16)),
        xaxis=dict(title_font=dict(size=15)),
        yaxis=dict(title_font=dict(size=15))
    )

    st.plotly_chart(fig_bar, use_container_width=True)



# Função de plotagem
def plot_mapa(st, px, df, coluna):
    """
    Plota um mapa de coordenadas geográficas com cor por município.

    Parâmetros:
    - st: módulo streamlit
    - px: módulo plotly.express
    - df: dataframe contendo a coluna de coordenadas
    - coluna: nome da coluna que possui as coordenadas no formato [longitude, latitude]
    """

    # Filtra registros com coordenadas não nulas
    df_filtered = df[~df[coluna].isna()].copy()

    if df_filtered.empty:
        st.warning("Não há dados com coordenadas válidas para exibir no mapa.")
        return

    # Extrai Longitude e Latitude
    df_filtered['Longitude'] = df_filtered[coluna].apply(lambda x: x[0])
    df_filtered['Latitude'] = df_filtered[coluna].apply(lambda x: x[1])

    # st.subheader("Dados com Coordenadas")
    # st.dataframe(df_filtered[['Municipio', '__system.submitterName', 'Latitude', 'Longitude']])

    # Cria o mapa com cor por município
    fig = px.scatter_map(
        df_filtered,
        lat="Latitude",
        lon="Longitude",
        # color="Municipio",  # Colore por município
        color="__system.submitterName",  # Colore por agente        
        hover_name="__system.submitterName",
        hover_data={'Municipio': True, 
                    'nome_pessoa_idosa': True,
                    'bairro': True,
                    'Latitude': False, 
                    'Longitude': False,
                     "__system.submitterName": False},
        zoom=10,
        size_max=20,
        height=700
    )


    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        dragmode="zoom"  # Permite zoom com o mouse
    )

    st.plotly_chart(fig, use_container_width=True)



# ===========================
# Função para calcular métricas
# ===========================
def calcular_metricas(st, df):

    df['data_convertida'] = pd.to_datetime(df['__system.submissionDate'],format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce')

    total_cadastros = df.shape[0]

    # Cálculo de cadastros na última semana
    data_limite_semana = datetime.now() - timedelta(days=7)
    cadastros_semana = df[df['data_convertida'] >= data_limite_semana].shape[0]

    st.write(f"Total de cadastros: {datetime.now()} - {timedelta(days=7)} = {data_limite_semana}")

    # Cálculo de cadastros no mês atual
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    cadastros_mes = df[
        (df['data_convertida'].dt.month == mes_atual) &
        (df['data_convertida'].dt.year == ano_atual)
    ].shape[0]

    # Total de agentes
    total_agentes = df['__system.submitterName'].nunique()

    # Meta (ajustável conforme necessidade)
    meta_geral = 5000  # Valor ajustável
    meta_mensal = 1500   # Valor ajustável
    meta_semanal = 200  # Valor ajustável

    meta_geral_percentual = (total_cadastros / meta_geral) * 100
    meta_mensal_percentual = (cadastros_mes / meta_mensal) * 100
    meta_semanal_percentual = (cadastros_semana / meta_semanal) * 100

    return {
        'meta_geral': meta_geral,
        'meta_mensal': meta_mensal,
        'meta_semanal': meta_semanal,
        'total_cadastros': total_cadastros,
        'cadastros_semana': cadastros_semana,
        'cadastros_mes': cadastros_mes,
        'total_agentes': total_agentes,
        'meta_geral_percentual': meta_geral_percentual,
        'meta_mensal_percentual': meta_mensal_percentual,
        'meta_semanal_percentual': meta_semanal_percentual
    }


def calcular_semana(days=4):
    # ============================
    # Cálculo da semana atual (segunda a sexta)
    # ============================
    hoje = datetime.now()
    dia_da_semana = hoje.weekday()  # segunda=0, sexta=4, domingo=6
    # print(f"Hoje: {hoje}, Dia da Semana: {dia_da_semana}")

    # Início da semana = segunda-feira, iniciando às 00:00:00
    inicio_semana = (hoje - timedelta(days=dia_da_semana)).replace(hour=0, minute=0, second=0, microsecond=0)
    # print(f"Início da Semana: {inicio_semana}")

    # Fim da semana = sexta-feira
    fim_semana = inicio_semana + timedelta(days=days)

    return {
        'inicio_semana': inicio_semana,
        'fim_semana': fim_semana,
        'hoje': hoje
    }


def calcular_metricas_fixar_segunda_sexta(st, df,semana, municipios):
    """
    Calcula métricas fixando o período de segunda a sexta-feira da semana atual.
    """
    total_cadastros_geral = df.shape[0]
    # Conversão da data
    df['data_convertida'] = pd.to_datetime(
        df['__system.submissionDate'],
        format='%Y-%m-%dT%H:%M:%S.%fZ',
        errors='coerce'
    ) #.dt.tz_localize(None)  # Remove timezone se houver

    df_ = df[df['Municipio'].isin(municipios)].copy() if municipios else df.copy() 

    # Total de cadastros
    total_cadastros = df_.shape[0]

    hoje = semana['hoje']
    inicio_semana = semana['inicio_semana']
    fim_semana = semana['fim_semana']

    cadastros_semana_geral = df[
        (df['data_convertida'] >= inicio_semana) &
        (df['data_convertida'] <= fim_semana)
    ].shape[0]

    # Filtra cadastros entre segunda e sexta da semana atual
    cadastros_semana = df_[
        (df_['data_convertida'] >= inicio_semana) &
        (df_['data_convertida'] <= fim_semana)
    ].shape[0]


    # ============================
    # Cálculo de cadastros no mês atual
    # ============================
    mes_atual = hoje.month
    ano_atual = hoje.year

    cadastros_mes = df_[
        (df_['data_convertida'].dt.month == mes_atual) &
        (df_['data_convertida'].dt.year == ano_atual)
    ].shape[0]

    # ============================
    # Total de agentes únicos
    # ============================
    total_agentes = df_['__system.submitterName'].nunique()

    # ============================
    # Metas (ajustáveis)
    # ============================
    meta_geral = st.secrets["metas"]["meta_geral"]  # Valor ajustável
    meta_mensal = st.secrets["metas"]["meta_mensal"]  # Valor ajustável
    meta_semanal = st.secrets["metas"]["meta_semanal"]  # Valor ajustável

    meta_geral_percentual = (total_cadastros / meta_geral) * 100
    meta_mensal_percentual = (cadastros_mes / meta_mensal) * 100
    meta_semanal_percentual = (cadastros_semana / meta_semanal) * 100

    return {
        'total_cadastros_geral': total_cadastros_geral,
        'cadastros_semana_geral': cadastros_semana_geral,
        'meta_geral': meta_geral,
        'meta_mensal': meta_mensal,
        'meta_semanal': meta_semanal,
        'total_cadastros': total_cadastros,
        'cadastros_semana': cadastros_semana,
        'cadastros_mes': cadastros_mes,
        'total_agentes': total_agentes,
        'meta_geral_percentual': meta_geral_percentual,
        'meta_mensal_percentual': meta_mensal_percentual,
        'meta_semanal_percentual': meta_semanal_percentual,
        'inicio_semana': inicio_semana.strftime('%d/%m/%Y'),
        'fim_semana': fim_semana.strftime('%d/%m/%Y')
    }



def exibe_metricas(st, metricas):

    col0, col1, col2, col3, col4 = st.columns(5)
    

    col0.metric(
        "Total de Questionários",
        f"{metricas['total_cadastros_geral']}",
        f"+{metricas['cadastros_semana_geral']} na última semana",
        help=f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        border=True
    )

    col1.metric(
        "Por Municipio(s)",
        f"{metricas['total_cadastros']}",
        f"+{metricas['cadastros_semana']} na última semana",
        border=True
    )
    col2.metric(
        "Meta Geral",
        f"{metricas['meta_geral_percentual']:.0f}%",
        f"Meta: {metricas['meta_geral']}",
        border=True
    )
    col3.metric(
        "Meta Mensal",
        f"{metricas['meta_mensal_percentual']:.1f}%",
        f"Meta: {metricas['meta_mensal']}",
        border=True
    )
    col4.metric(
        "Meta Semanal",
        f"{metricas['meta_semanal_percentual']:.1f}%",
        f"Meta: {metricas['meta_semanal']}",
        border=True
    )    



def plot_piramide_etaria(st, go, df, col_idade='aspectos_sociodemograficos.idade', col_sexo='aspectos_sociodemograficos.genero'):
    """
    Plota uma pirâmide etária a partir de um DataFrame no Streamlit.
    
    Parâmetros:
    - df: DataFrame contendo as colunas de idade e sexo.
    - col_idade: Nome da coluna com as idades (padrão: 'aspectos_sociodemograficos.idade').
    - col_sexo: Nome da coluna com os sexos (padrão: 'aspectos_sociodemograficos.genero').
    """

    # Definindo faixas etárias
    bins = [60, 70, 80, 90, 100]
    labels = ['60-69', '70-79', '80-89', '90+']
    df['faixa_etaria'] = pd.cut(df[col_idade], bins=bins, labels=labels, right=False)

    # Agrupar por sexo e faixa etária
    pop = df.groupby(['faixa_etaria', col_sexo],observed=False).size().unstack(fill_value=0)

    # Garantir que ambas as colunas existam, mesmo que vazias
    if 'Masculino' not in pop.columns:
        pop['Masculino'] = 0
    if 'Feminino' not in pop.columns:
        pop['Feminino'] = 0

    # Criar o gráfico
    fig = go.Figure()

    # Masculino (valores negativos)
    fig.add_trace(go.Bar(
        y=pop.index.astype(str),
        x=-pop['Masculino'],  # valores negativos para esquerda
        name='Masculino',
        orientation='h',
        marker=dict(color='blue')
    ))

    # Feminino
    fig.add_trace(go.Bar(
        y=pop.index.astype(str),
        x=pop['Feminino'],  # valores positivos para direita
        name='Feminino',
        orientation='h',
        marker=dict(color='pink')
    ))

    # Layout
    max_pop = max(pop['Masculino'].max(), pop['Feminino'].max()) + 1  # Para ajustar eixo
    fig.update_layout(
        title='Pirâmide Etária',
        xaxis=dict(
            title='População',
            tickvals=[-i for i in range(max_pop)] + [i for i in range(max_pop)],
            ticktext=[i for i in range(max_pop)] + [i for i in range(max_pop)],
            range=[-max_pop, max_pop]
        ),
        yaxis=dict(title='Faixa Etária'),
        barmode='overlay',
        bargap=0.1,
        plot_bgcolor='white',
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)    