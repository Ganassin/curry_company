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
# Importando a biblioteca para desenhar o mapa
import folium
from streamlit_folium import folium_static

# Configura as informações da página, é a barrinha que aparece na parte de cima do navegador 
st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

# =========================================================================================
# SIDEBAR =================================================================================
# =========================================================================================
image = Image.open('logo.png')
st.sidebar.image( image, width=120 ) # Mostra a imagem de LOGO
st.sidebar.markdown('# Curry Company - Empresa') # Título da sidebar
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

festival_option = st.sidebar.multiselect(
    'Época de Festival',
    ['Yes', 'No'],
    default = ['Yes', 'No']
)
st.sidebar.markdown(""" --- """) # Divider
st.sidebar.markdown('### Criado por Gabriel Ganassin')

# ******************** Vinculando os filtros ao DF ****************
linhas_filtradas = (df['Order_Date'] < date_slider) & (df['Road_traffic_density'].isin(traffic_option)) & (df['Festival'].isin(festival_option))
df = df.loc[linhas_filtradas, :]

#==========================================================================================
# PÁG PRINCIPAL ===========================================================================
# =========================================================================================
st.markdown('# Marketplace - Visão Cliente') # Título pág. principal

tab1, tab2, tab3 = st.tabs( ['Gerencial', 'Tático', 'Geográfico'] ) # ABAS

with tab1: # Oque ficar dentro desse WITH fica dentro da aba 1 (GERENCIAL) -------------
    with st.container(): # Cria uma "subdivisão dentro da primeira aba"
        st.markdown('## Quantidade de pedidos por dia')
        
        # 1. Quantidade de pedidos por dia:
        df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index() # Cria o df para criar o gráfico
        graf = px.bar(df_aux, x='Order_Date', y='ID') # Cria o gráfico
        st.plotly_chart( graf, use_container_width=True) # Mostra o gráfico

    with st.container(): # Cria outra "subdivisão dentro da primeira aba"
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('### Distribuição dos pedidos por tipo de tráfego. (%)')
            # Cria um df auxiliar, para armazenar a quantidade de pedidos por tipo de tráfego
            df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            # Cria uma coluna com o percentual de cada tipo de tráfego (total de pedido por tipo de tráfego / total de pedidos)
            df_aux['Entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
            
            # Cria o gráfico, biblioteca plotly.express importada no 1.
            graf = px.pie(df_aux, values='Entregas_perc', names='Road_traffic_density')
            st.plotly_chart( graf, use_container_width=True) # Mostra o gráfico
            
        with col2:
            st.markdown('### Comparação do volume de pedidos por cidade e tipo de tráfego.')
            # Cria um df auxiliar com a comparação do volume de pedidos por cidade e tipo de tráfego.
            df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            # Cria o gráfico, biblioteca plotly.express importada no 1.
            graf = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(graf, use_container_width=True)

# -----------------------------------------------------------------------------------

with tab2: # Oque ficar dentro desse WITH fica dentro da aba 2 (TÁTICO) -------------
    with st.container(): # Cria uma "subdivisão dentro da segunda aba"
        st.markdown('## Quantidade de pedidos por semana.')
        # Cria a coluna com a semana do ano (.dt.strftime('%U') retorna o número da semana a qual a data pertence, o U diz que o Domingo é o primeiro dia da semana)
        # o tipo detetime, se converteu para object. (ISSO SÓ ACONTECE COM O DETETIME) 
        df['Semana'] = df['Order_Date'].dt.strftime('%U')
        # Cria um novo df para guardar a quantidade de pedidos por semana.
        df_aux = df.loc[:, ['ID', 'Semana']].groupby('Semana').count().reset_index()
        # Cria o gráfico, biblioteca plotly.express importada no 1.
        graf = px.line(df_aux, x='Semana', y='ID')
        st.plotly_chart(graf, use_container_width=True)

    with st.container(): # Cria outra "subdivisão dentro da segunda aba"
        st.markdown('## A quantidade de pedidos / entregador por semana. (causalidade)')
        
        df_aux = df.loc[:, ['ID', 'Delivery_person_ID', 'Order_Date']]
        df_aux['Semana'] = df_aux['Order_Date'].dt.strftime('%U')
        
        df_aux1 = df_aux.loc[:, ['ID','Semana']].groupby('Semana').count().reset_index()
        df_aux2 = df_aux.loc[:, ['Delivery_person_ID','Semana']].groupby('Semana').nunique().reset_index()
        
        # Junta df_aux1 e df_aux2 com inner (mesmo conceito do SQL)
        df_aux = pd.merge(df_aux1, df_aux2, how='inner')
        
        # Renomeia a coluna
        df_aux = df_aux.rename(columns= {'ID': 'Entregas', 'Delivery_person_ID': 'Entregadores'})
        
        # Cria a coluna Qnt. Entregas / Qnt. Entregadores
        df_aux['Razao'] = df_aux['Entregas']/df_aux['Entregadores']
        
        # Cria o gráfico que mostra a razão de entregas por entregador em cada semana.
        # Se essa razão aumenta, pode significar que o número de entregas aumenta ou o número de entregadores diminui
        graf = px.line(df_aux, x='Semana', y='Razao')
        st.plotly_chart(graf, use_container_width=True)
# -----------------------------------------------------------------------------------

with tab3: # Oque ficar dentro desse WITH fica dentro da aba 3 (GEOGRÁFICO) ---------
    st.markdown('## A localização central de cada cidade por tipo de tráfego.')
    # Cria um df, que mostra a mediana da lat e long, por cidade e densidade de tráfego
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    # cria o mapa
    map = folium.Map()
    # usar o iterrows() para esse caso é melhor pois com ele é possível criar o popup, porém o FOR de cima tbm da certo, só que sem popup
    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static( map, width=1024, height=600)
    
# -----------------------------------------------------------------------------------


# =========================================================================================
# =========================================================================================
# =========================================================================================




