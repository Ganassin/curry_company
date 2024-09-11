# Para executar: No terminal, entrar na pasta onde esse arquivo está e usar o comando "streamlit run nome_do_arquivo"

import pandas as pd
import datetime

# Importar biblioteca para criação de gráficos: plotly
import plotly.express as px
# Importando a biblioteca para desenhar o mapa
import folium
# Para calcular a distancia 
from geopy.distance import great_circle

import plotly.graph_objects as go

import numpy as np


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
st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

# =========================================================================================
# SIDEBAR =================================================================================
# =========================================================================================
image = Image.open('logo.png')
st.sidebar.image( image, width=120 ) # Mostra a imagem de LOGO
st.sidebar.markdown('# Curry Company - Restaurantes') # Título da sidebar
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
st.markdown('# Visão Restaurantes')

tab1 = st.tabs( ['Visão Gerencial'] )

with st.container(): # Cria uma "subdivisão" ============================================================
    st.markdown('# Métricas Gerais')
    
    col1, col2= st.columns(2)   
    with col1: # -------------- Entregadores Únicos
        entregadores_unicos = len(df['Delivery_person_ID'].unique())
        st.metric('Entregadores Únicos', entregadores_unicos)
    
    with col2: # -------------- Distância Média
        from geopy.distance import great_circle
        # Função para calcular a distância usando great_circle
        def calcular_distancia(row):
            coord_restaurante = (row['Restaurant_latitude'], row['Restaurant_longitude'])
            coord_entrega = (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
            return great_circle(coord_restaurante, coord_entrega).kilometers
        # Aplicar a função ao DataFrame
        df['distancia_km'] = df.apply(calcular_distancia, axis=1)
        # Exibir a distancia media entre os restaurantes e locais de entrega em km
        distancia_media = df['distancia_km'].mean()
        st.metric('Distância Média', f'{round(distancia_media, 2)} Km') # Mostra o resultado
    
        
with st.container(): # Cria uma "subdivisão" ============================================================
    col1, col2, col3, col4 = st.columns(4)   
    with col1: # --------------
        df_festival_time_mean = (df.loc[:, ['Time_taken(min)', 'Festival']]
                                 .groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']} ))
        df_festival_time_mean.columns=['Time_taken_mean', 'Time_taken_std']
        df_festival_time_mean = df_festival_time_mean.reset_index()
        avg_festival = round(df_festival_time_mean.loc[df_festival_time_mean['Festival'] == 'Yes', 'Time_taken_mean'],2)
        st.metric('Tempo médio com festival (min.)', avg_festival)
    with col2: # --------------
        std_festival = round(df_festival_time_mean.loc[df_festival_time_mean['Festival'] == 'Yes', 'Time_taken_std'],2)
        st.metric('STD com festival (min.)', std_festival)
    with col3: # --------------
        avg_festival = round(df_festival_time_mean.loc[df_festival_time_mean['Festival'] == 'No', 'Time_taken_mean'],2)
        st.metric('Tempo médio sem festival (min.)', avg_festival)
        
    with col4: # --------------
        std_festival = round(df_festival_time_mean.loc[df_festival_time_mean['Festival'] == 'No', 'Time_taken_std'],2)
        st.metric('STD sem festival (min.)', std_festival)
        
    st.markdown(""" --- """)

with st.container(): # Cria uma "subdivisão" ============================================================
    st.markdown('# Tempo médio e o desvio padrão de entrega por cidade')
    df_time_city = (df.loc[:, ['Time_taken(min)', 'City']]
                    .groupby('City').agg( {'Time_taken(min)': ['mean', 'std']} ))
    df_time_city.columns = ['Time_taken_mean', 'Time_taken_std']
    df_time_city = df_time_city.reset_index()
        
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',
                            x=df_time_city['City'],
                            y=df_time_city['Time_taken_mean'],
                            error_y=dict (type='data', array=df_time_city['Time_taken_std'])) )
        
    fig.update_layout(barmode='group')
    st.plotly_chart( fig, use_container_width=True) # Mostra o gráfico


with st.container(): # Cria uma "subdivisão" ============================================================
    st.markdown('# Distribuição do Tempo')
    
    col1, col2 = st.columns(2)   
    with col1: # --------------
        st.markdown('#### Tempo Médio de Entrega por Cidade')
        # Distância média por cidade
        avg_distance = df.loc[:, ['City', 'distancia_km']].groupby('City').mean().reset_index()
    
        fig = (go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distancia_km'], 
                                        pull=[0.02, 0.02, 0.02])]))
        st.plotly_chart( fig, use_container_width=True) # Mostra o gráfico
        
    with col2: # --------------
        st.markdown('#### Tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego')
        df_time_city_tytrafic = (df.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                                 .groupby(['City', 'Road_traffic_density'])
                                 .agg( {'Time_taken(min)': ['mean', 'std']} ))
        df_time_city_tytrafic.columns = ['Time_taken_mean', 'Time_taken_std']
        df_time_city_tytrafic = df_time_city_tytrafic.reset_index()
        # Verifique e calcule a média
        midpoint = np.average(df_time_city_tytrafic['Time_taken_std'])
        # Crie o gráfico Sunburst
        fig = px.sunburst(
            df_time_city_tytrafic,
            path=['City', 'Road_traffic_density'],
            values='Time_taken_mean',
            color='Time_taken_std',
            color_continuous_scale='bluered',
            color_continuous_midpoint=midpoint
        )
        # Exiba o gráfico
        st.plotly_chart( fig, use_container_width=True) # Mostra o gráfico

    st.markdown(""" --- """)


with st.container(): # Cria uma "subdivisão" ============================================================
    st.markdown('# O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido')
    # Cria um novo df com o tempo médio
    df_time_city_tyorder = (df.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                            .groupby(['City', 'Type_of_order']).mean().reset_index())
    # Muda o nome da coluna
    df_time_city_tyorder = df_time_city_tyorder.rename(columns={'Time_taken(min)': 'Média'})
    # Cria um novo df com o desvio padrão
    df_aux = (df.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
              .groupby(['City', 'Type_of_order']).std().reset_index())
    # Muda o nome da coluna
    df_aux = df_aux.rename(columns={'Time_taken(min)': 'Desvio Padrão'})
    # Junta o segundo df criado no primeiro df criado
    df_time_city_tyorder = pd.merge(df_time_city_tyorder, df_aux, on=['City', 'Type_of_order'])
    st.dataframe(df_time_city_tyorder, width=1000)
    
    st.markdown(""" --- """)



