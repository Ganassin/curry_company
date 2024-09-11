# Para executar: No terminal, entrar na pasta onde esse arquivo está e usar o comando "streamlit run nome_do_arquivo"

import pandas as pd
import datetime

# Importar biblioteca para criação de gráficos: plotly
import plotly.express as px
# Importando a biblioteca para desenhar o mapa
import folium

# Importando dados e criando o dataframe (JÁ com o .csv LIMPO)
df = pd.read_csv('datasets/train_limpo.csv')
# Muda tipo da coluna Order_Date para Datetime
df['Order_Date'] = pd.to_datetime(df['Order_Date'])


# ============================================================================================================================
# LAYOUT DO STREAMLIT
# ============================================================================================================================
# Importa o STREAMLIT, que é uma biblioteca. Antes de importar tive que instalar com o pip install no terminal
import streamlit as st
# Importando biblioteca para mostrar imagem
from PIL import Image

# Configura as informações da página, é a barrinha que aparece na parte de cima do navegador 
st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')

# =========================================================================================
# SIDEBAR =================================================================================
# =========================================================================================
image = Image.open('logo.png')
st.sidebar.image( image, width=120 ) # Mostra a imagem de LOGO
st.sidebar.markdown('# Curry Company - Entregadores') # Título da sidebar
st.sidebar.markdown('## Fastesd Delivery in Town!') # Subtítulo da sidebar
st.sidebar.markdown(""" --- """) # Divider


# Cria um filtro de BARRA DE SELEÇÃO de data
st.sidebar.markdown('## Selecione uma data limíte')
date_slider = st.sidebar.slider(
    'Data',
    value=datetime.datetime(2022, 4, 6), # É o DEFAUlT, o padrão
    min_value = df['Order_Date'].min(),
    max_value = df['Order_Date'].max(),
    format = 'DD-MM-YYYY'
)
st.sidebar.markdown(""" --- """) # Divider


# Cria um filtro de CAIXA DE SELEÇÃO, aceitando multipla escolha
st.sidebar.markdown('## Selecione')
traffic_option = st.sidebar.multiselect(
    'Condições de Trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam']
)

climatic_option = st.sidebar.multiselect(
    'Condições climáticas',
    ['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'],
    default = ['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy']
)

city_option = st.sidebar.multiselect(
    'Tipo de Cidade',
    ['Metropolitian', 'Semi-Urban', 'Urban'],
    default = ['Metropolitian', 'Semi-Urban', 'Urban']
)
st.sidebar.markdown(""" --- """) # Divider
st.sidebar.markdown('### Criado por Gabriel Ganassin')

# ******************** Vinculando os filtros ao DF ****************
linhas_filtradas = ((df['Order_Date'] < date_slider) 
                    & (df['Road_traffic_density'].isin(traffic_option)) 
                    & (df['City'].isin(city_option)))
df = df.loc[linhas_filtradas, :]

#==========================================================================================
# PÁG PRINCIPAL ===========================================================================
# =========================================================================================
st.markdown('# Visão Entregadores')

tab1 = st.tabs( ['Visão Gerencial'] )
with st.container(): # Cria uma "subdivisão" ============================================================
    st.markdown('# Métricas Gerais')
    
    col1, col2, col3, col4 = st.columns(4, gap='medium')   
    with col1:
        qnt_entregadores = df['Delivery_person_ID'].nunique() # Pega a quantidade de entregadores
        st.metric('Qnt. Entregadores', qnt_entregadores) # Mostra na tela
    
    with col2:
        media_entregas_entregador = round((df['ID'].nunique())/(df['Delivery_person_ID'].nunique()), 0)
        st.metric('Média de entregas', int(media_entregas_entregador))
    
    with col3:
        maior_idade = df['Delivery_person_Age'].max() # Pega a maior idade da coluna Delivery_person_Age
        st.metric('Maior idade', maior_idade) # Mostra na tela
    
    with col4:
        menor_idade = df['Delivery_person_Age'].min() # Pega a menor idade da coluna Delivery_person_Age
        st.metric('Menor idade', menor_idade) # Mostra na tela

with st.container(): # Cria outra "subdivisão" ============================================================
    st.markdown(""" --- """)
    st.markdown('# Avaliações')
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Avaliação média por entregador') # -------------------
        df_av_entregador = (df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                            .groupby('Delivery_person_ID').mean().reset_index())
        df_av_entregador = df_av_entregador.rename(columns={'Delivery_person_Ratings': 'Avaliação média',
                                                            'Delivery_person_ID': 'ID_entregador'})
        st.dataframe(df_av_entregador, height=500)

    with col2:
        st.markdown('#### Avaliação média por transito') # ---------------------
        # Faz a média
        df_type_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                           .groupby('Road_traffic_density').mean().reset_index())
        # Muda nome da coluna
        df_type_traffic = df_type_traffic.rename( columns={ 'Delivery_person_Ratings': 'Avaliação média'})
        # Faz o desvio padrão em um df auxiliar
        df_aux = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                  .groupby('Road_traffic_density').std().reset_index())
        # Muda nome da coluna
        df_aux = df_aux.rename( columns={'Delivery_person_Ratings': 'Desvio Padrão'})
        # Junta dos dois dfs criados
        df_type_traffic = pd.merge(df_type_traffic, df_aux, on='Road_traffic_density')
        st.dataframe(df_type_traffic)

        st.markdown('#### Avaliação média por clima') # -----------------------
        # Faz a média
        df_Weatherconditions = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                .groupby('Weatherconditions').mean().reset_index())
          # Muda nome da coluna
        df_Weatherconditions = df_Weatherconditions.rename( columns={ 'Delivery_person_Ratings': 'Media_avaliacao'})
        # Faz o desvio padrão em um df auxiliar
        df_aux = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                  .groupby('Weatherconditions').std().reset_index())
        # Muda nome da coluna
        df_aux = df_aux.rename( columns={ 'Delivery_person_Ratings': 'Desvio_pad_avaliacao'})
        # Junta dos dois dfs criados
        df_Weatherconditions = pd.merge(df_Weatherconditions, df_aux, on='Weatherconditions')
        st.dataframe(df_Weatherconditions)
        

with st.container(): # Cria outra "subdivisão" ============================================================
    st.markdown(""" --- """)
    st.markdown('# Ranking')
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Entregadores mais rápidos por cidade')
        df_aux = (df.loc[: , ['City', 'Delivery_person_ID', 'Time_taken(min)']]
                  .sort_values(by=['City', 'Time_taken(min)']).reset_index(drop=True))
        # Agrupar por cidade e pegar os 10 primeiros entregadores mais rápidos de cada cidade
        top_10_entregadores = df_aux.groupby('City').head(10).reset_index(drop=True)
        st.dataframe(top_10_entregadores)
    
    with col2:
        st.markdown('#### Entregadores mais lentos por cidade')
        df_aux = (df.loc[: , ['City', 'Delivery_person_ID', 'Time_taken(min)']]
                  .sort_values(by=['City', 'Time_taken(min)'], ascending=False).reset_index(drop=True))
        # (os mais lentos são pegos devido ao "ascending=False", que ordena em ordem decrescente)
        # Agrupar por cidade e pegar os 10 primeiros entregadores mais lentos de cada cidade
        top_10_entregadores = df_aux.groupby('City').head(10).reset_index(drop=True)
        top_10_entregadores
