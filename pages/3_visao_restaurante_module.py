# import

import folium
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go

from PIL import Image
from datetime import datetime
from haversine import haversine


st.set_page_config( page_title='Visão Restaurantes', page_icon='🍲', layout='wide' )

# ----------------------------------------------
# Funções
# ----------------------------------------------
def avg_std_time_on_traffic( df1 ):           
    df_aux = ( df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
                              .groupby( ['City', 'Road_traffic_density'] )
                              .agg({'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst( df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                    color='std_time', color_continuous_scale='RdBu',
                                    color_continuous_midpoint=np.average( df_aux['std_time'] ) )
                
    return fig


def avg_std_time_graph( df1 ):
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)']]
                  .groupby('City')
                  .agg({'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',
                                          x=df_aux['City'],
                                          y=df_aux['avg_time'],
                                          error_y=dict( type='data', array=df_aux['std_time'] ) ) )

    fig.update_layout( barmode='group' )
                
    return fig

def avg_std_time_delivery( df1, festival, operation ):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - festival: Filtrar se era ou não festival:
                    'Yes': Para filtrar o dataset nos períodos de festivais
                    'No': Para filtrar o dataset em períodos sem festivais
                - operation: Tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo.
            
            Output:
                - df: Dataframe com 2 colunas e 1 linha.
    """
    df_aux = ( df1.loc[:, ['Festival', 'Time_taken(min)']]
                  .groupby('Festival')
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, operation], 2 )
                
    return df_aux              


def distance( df1, fig ):
    if fig == 'False':
        cols = ['Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = ( df1.loc[:, cols].apply( lambda x:                                  
                                haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),                                                 (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
        axis=1) )

        media_distancia_entrega = np.round( df1.loc[:, 'distance'].mean(), 2 )
        
        return media_distancia_entrega
    
    else:
        cols = ['Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = ( df1.loc[:, cols]
                               .apply( lambda x:                                  
                                haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),                                                 (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
        axis=1) )

        avg_distance = ( df1.loc[:, ['City', 'distance']]
                            .groupby( 'City' )
                            .mean()
                            .reset_index() )

        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0] )] )
        
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

# cleaning code
df1 = clean_code( df )


# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Restaurantes' )

#image_path = '/home/rafael/Documentos/repos/ftc_analisando_dados_com_python/images/flecha_no_alvo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=280 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value=pd.datetime( 2022, 4, 13),
    min_value=pd.datetime( 2022, 2, 11 ),
    max_value=pd.datetime( 2022, 4, 6),
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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '-', '-'] )

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            delivery_unique = df1['Delivery_person_ID'].nunique()
            col1.metric( 'Entregadores únicos', delivery_unique )
                
        with col2:
            media_distancia_entrega = distance( df1, 'False' )
            col2.metric( 'Distância Média', media_distancia_entrega )
            

        with col3:
            df_aux = avg_std_time_delivery( df1, festival='Yes', operation='avg_time' )
            col3.metric( 'Tempo Médio c/ Festival', df_aux )
                        
        with col4:
            df_aux = avg_std_time_delivery( df1, festival='Yes', operation='std_time' )
            col4.metric( 'Std de Entrega c/ Festival', df_aux )
            
        with col5:
            df_aux = avg_std_time_delivery( df1, festival='No', operation='avg_time' )
            col5.metric( 'Tempo Médio s/ Festival', df_aux )
            
        with col6:
            df_aux = avg_std_time_delivery( df1, festival='No', operation='std_time' )
            col6.metric( 'Std de Entrega s/ Festival', df_aux )
            
    with st.container():
        st.markdown( """---""" )
        st.title( 'Tempo Médio de entrega por Cidade' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig, use_container_width=True )
        
        with col2:
            df_aux = ( df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg({'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            st.dataframe( df_aux, use_container_width=True )

    
    with st.container():
        st.markdown( """---""" )
        st.title( 'Distribuição do Tempo' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = distance( df1, 'True' )
            st.plotly_chart( fig, use_container_width=True )
        
        with col2:
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig, use_container_width=True )
            


    