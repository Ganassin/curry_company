import streamlit as st
from PIL import Image

# =========================================================================================
# SIDEBAR =================================================================================
# =========================================================================================

# Função que junta as páginas, o streamlit entrende que tem que buscas os arquivos (páginas) dentro de uma pasta chamada pages
st.set_page_config(
    page_title="Home",
    page_icon="🎲"
)

image_path = 'logo.png' # Logo, deve estar na mesma pasta que o arquivo .py
image = Image.open( image_path )
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company') # Título da sidebar
st.sidebar.markdown('## Fastesd Delivery in Town!') # Subtítulo da sidebar
st.sidebar.markdown(""" --- """) # Divider
st.sidebar.markdown('### Criado por Gabriel Ganassin')
st.sidebar.link_button("Saiba Mais", "https://resumo-gabriel-ganassin.notion.site/Resumo-Gabriel-Ganassin-363e4a3b1a7340ce97470be588a8bdcd")
#==========================================================================================


#==========================================================================================
# PÁG PRINCIPAL ===========================================================================
# =========================================================================================
st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard fori construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar o Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de crescimento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão geográfica: Insights de geolocalização.
    - Visão entregadores:
        - Acompanhamento de indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ajuda
    - Gabriel Ganassin: www.linkedin.com/in/gabriel-ganassin
    """
)
#==========================================================================================