import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='wide'
)

#image_path = '/home/rafael/Documentos/repos/ftc_analisando_dados_com_python/images/'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=280 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write( '# Curry Company Growth Dashboard' )

st.markdown("""
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utiliza esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos rastaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        -@RafaelPinheiro
""")