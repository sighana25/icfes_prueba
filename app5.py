import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import plotly.express as px
import geopandas as gpd
import json
from PIL import Image
import plotly.graph_objects as go
import plotly.figure_factory as ff
#npm install streamlit-component-lib

st.set_page_config(
     page_title="icfes", #nombre en el buscador
     layout="wide", #o centered
     initial_sidebar_state="expanded", #auto: en mobile la esconde, expanded o collapsed
)





ANO = st.sidebar.selectbox(
    "Qué año desea analizar?",
    (2014,2015,2016,2017,2018,2019)
)

st.title('AVANCE DEL PROCESO TECNOLÓGICO EN LAS ESCUELAS DE COLOMBIA') #titulo

st.text('OBJETIVO:')

st.header('Estadísticos')

DF = pd.read_csv("/Users/luzadrianamejiacastano/Dropbox/materias/dataviz/Data_Base_1419.csv")


st.text("promedios de conexión a internet, computador, y pertenencia a etnia")

df_ano = DF[DF['Ano']==ANO]

col1, col2, col3 = st.columns(3)
col1.metric("internet","{:.0%}".format(df_ano['FAMI_TIENEINTERNET'].mean()), "1.2 °F")
col2.metric("computador", "{:.0%}".format(df_ano['FAMI_TIENECOMPUTADOR'].mean()), "-8%")
col3.metric("etnia", "{:.0%}".format(df_ano['ESTU_TIENEETNIA'].mean()), "4%")


st.markdown('Análisis multivariado :heavy_exclamation_mark:') #soporta emojis y latex


col1, col2 = st.columns([3,1])
col1.subheader("por departamentos")
col1.write(px.scatter(df_ano, x="ConexMilHab", y="PUNT_GLOBAL",color="FAMI_TIENECOMPUTADOR", hover_data=DF.columns,
                 color_continuous_scale='thermal'))

#poner info relevante unicamente en le hover

col2.subheader("peores")
col2.write((px.scatter_ternary(df_ano, a="ConexMilHab", b="FAMI_TIENECOMPUTADOR", color="ESTU_TIENEETNIA",c="Indice_Rural",
                 color_continuous_scale='thermal')))


T=df_ano.groupby(["DEPARTAMENTO"]).mean().reset_index()

st.write(px.pie(T, values='PUNT_GLOBAL', names='DEPARTAMENTO', title='MEDIA DE PUNTAJE POR DEPARTAMENTOS'))


depto=st.selectbox(
    "Qué departamento desea analizar?",
    ("CHOCÓ","VAUPÉS","AMAZONAS","GUAINÍA")
)

T1=df_ano.groupby(["DEPARTAMENTO","MUNICIPIO"]).mean().reset_index()
T2=T1[T1["DEPARTAMENTO"]==depto]
st.write(px.sunburst(T2, path=['DEPARTAMENTO', 'MUNICIPIO'], values='PUNT_GLOBAL'))#,color='lifeExp', hover_data=['ConexMilHab']))


df=DF[DF['Ano']==ANO]

FIG=go.Figure(data=go.Heatmap(
        z=df.PUNT_GLOBAL,
        x=df.Ano,
        y=df.DEPARTAMENTO,
)#,height=1500
)
FIG.update_layout(
    title='DISTRIBUCIÓN DE PUNTAJES',hoverlabel=dict(
        bgcolor="white",
        font_size=8,
        font_family="Rockwell"
    ),height=1000, width=300)
st.plotly_chart(FIG)



#cambiar pie a lollipop!

DEPARTAMENTO = st.slider("elegir un rango de puntajes", 100, 400, (150,250) )


x = DF[DF['Ano']==ANO].PUNT_GLOBAL

FIG=ff.create_distplot([x], ['PUNTAJE'], bin_size=.2)
FIG.update_xaxes(range=DEPARTAMENTO)

st.plotly_chart(FIG)

#DEBERIAMOS PONER ESE SLIDER AL LADO DERECHO?
#ponerlos en columna

st.header('Mapa interactivo')

st.caption('Mapa de Colombia con división política con puntajes')

#data para hacer el mapa

data_geo = gpd.read_file("/Users/luzadrianamejiacastano/Dropbox/materias/dataviz/MunicipiosVeredas19MB.json")
data_geo.index=map(lambda p : str(p),data_geo.index)
#f = open("/Users/luzadrianamejiacastano/Dropbox/materias/dataviz/MunicipiosVeredas19MB.json")
#geojson = json.load(f)

DF['COLE_COD_MCPIO_UBICACION'] = DF['COLE_COD_MCPIO_UBICACION'].apply(lambda x: '{0:0>5}'.format(x))

#st.write(geojson)

geo_datadf = data_geo.join(DF.set_index('COLE_COD_MCPIO_UBICACION'), how = 'left', on = 'MPIO_CCNCT').set_index("MPIO_CCNCT")
geo_datadf.fillna(0, inplace = True)


data15=geo_datadf[geo_datadf['Ano']==ANO]
#data15=DF[DF['Ano']==2019]


st.write(px.choropleth_mapbox(data15,
                           geojson=data15.geometry,
                           locations=data15.DPTOMPIO,
                           color="PUNT_GLOBAL",
                           color_continuous_scale="thermal",
                           #range_color=(0, 12),
                           center={"lat": 4.57086, "lon": -74.29733},
                           mapbox_style="carto-positron",#"open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor" yield maps co
                           zoom=5,
                           hover_data={'MUNICIPIO':True,'DEPARTAMENTO':True,'FAMI_TIENEINTERNET':True,'DPTOMPIO':False}
                           )
 )

with st.expander("ver explicación"):
    st.write(""" en el anterior mapa apreciamos...""")


#ALGUNA OTRA INFORMACION RELEVANTE POR AÑO ?

st.balloons()

st.header('Priorización de los municipios')