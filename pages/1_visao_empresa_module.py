# libraries

import folium
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from datetime import datetime
from haversine import haversine
from streamlit_folium import folium_static 

st.set_page_config( page_title='Visão Empresa', page_icon='📊', layout='wide' )

# ----------------------------------------------
# Funções
# ----------------------------------------------
def country_maps( df1 ):
    columns = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']

    data_plot = ( df1.loc[:, columns]
                     .groupby( ['City', 'Road_traffic_density'] )
                     .median()
                     .reset_index() )
    
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )

    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                location_info['Delivery_location_longitude']],
                popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    folium_static( map_, width=1024 , height=600 )
        
    return None

def order_share_by_week( df1 ):
    # Quantidade de pedidos por entregador por Semana
    # Quantas entregas na semana / Quantos entregadores únicos por semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux1 = ( df1.loc[:, ['ID', 'week_of_year']]
                   .groupby( 'week_of_year' )
                   .count()
                   .reset_index() )
    df_aux2 = ( df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby( 'week_of_year')
                   .nunique()
                   .reset_index() )

    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig


def order_by_week( df1 ):
    # Quantidade de pedidos por Semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = ( df1.loc[:, ['ID', 'week_of_year']]
                  .groupby( 'week_of_year' )
                  .count()
                  .reset_index() )

    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig


def traffic_order_city( df1 ):
    df_aux = ( df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .count()
                  .reset_index() )

    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig


def traffic_order_share( df1 ):
    df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density']]
                  .groupby( 'Road_traffic_density' )
                  .count()
                  .reset_index() )
    
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )

    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
                
    return fig

def order_metric( df1 ):
    # Quantidade de pedidos por dia
    df_aux = ( df1.loc[:, ['ID', 'Order_Date']]
                  .groupby( 'Order_Date' )
                  .count()
                  .reset_index() )
    df_aux.columns = ['order_date', 'qtde_entregas']

    # gráfico
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    
    return fig

            
def clean_code( df1 ):
    """ Está funcao tem a responsabilidade de limpar o dataframe 
        
        Tipos de limpeza: 
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    """
    
    # 1. convertendo a coluna Age de texto para número
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2. convertendo a coluna Ratings de texto para número decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. convertendo a coluna Order_Date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4. convertendo a coluna multiple_deliveries de texto para número
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5. removendo os espaços dentro de string/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # 6. removendo dados faltantes
    linhas_selecionadas = df1['Delivery_person_Ratings'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Weatherconditions'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 7. limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

# ===================================================================================================
# --------------------------------- Inicio da Estrutura lógica do código ----------------------------
# ===================================================================================================
# -----------------------
# import dataset
# -----------------------
df = pd.read_csv('dataset/train.csv')


# Limpando dados
df1 = clean_code( df )


# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Cliente' )

#image_path = '/home/rafael/Documentos/repos/ftc_analisando_dados_com_python/images/flecha_no_alvo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=280 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value=datetime( 2022, 4, 13),
    min_value=datetime( 2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# =======================================
# Layout no Streamlit
# =======================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    
    with st.container():
        # Order metric
        fig = order_metric( df1 )
        st.markdown( '# Orders by Day' )
        st.plotly_chart( fig, use_container_width=True )
        

    with st.container():
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.header ( 'Traffic Order Share' )
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            st.header ( 'Traffic Order City' )
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig, use_container_width=True)

           
with tab2:
    
    with st.container():
        st.markdown( '# Order by Week' )
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )

                
    with st.container():
        st.markdown( '# Order Share by Week' )
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

        
    
with tab3:
    st.markdown( '# Country Maps' )
    country_maps( df1 )
