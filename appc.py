# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 19:32:50 2022

@author: pc
"""
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import mysql.connector
import plotly.graph_objects as go
import plotly.figure_factory as ff
import seaborn as sns
import hydralit_components as hc



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title=" Dashboard", page_icon=":bar_chart:", layout="wide")

r=st.experimental_get_query_params()
if r['province']:
    all=False
    selectedProvince=r['province']
else:
    all=True









# ---- READ EXCEL ----
@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
def run_query(query):
    cursor = conn.cursor()
    cursor.execute(query)
























@st.cache
def get_data_from_excel():
    df = pd.read_csv('DonnesPourGraph.csv',encoding = "ISO-8859-1")
    # Add 'hour' column to dataframe
    datad=df.drop(['Index','bureauAvis','amileoration'],axis=1)
    print(datad.head())
    return datad

@st.cache
def get_data_from_excelnum():
    dffNum = pd.read_csv('projetCommuneN.csv',encoding = "ISO-8859-1")
    # Add 'hour' column to dataframe
    print(dffNum.head())
    return dffNum

dfNN = get_data_from_excelnum()
print(dfNN.head())
df = get_data_from_excel()

#df = df.query(
   # "province == @selectedProvince"
#)

# ---- SIDEBAR ----
st.sidebar.header("voir les grpahes avec les filtres suivants:")
add_selectbox = st.sidebar.selectbox(
    "la page ?",
    ("dashbord de population", "analyse de  taux de satisfait", "comparaison entre Arrendissement"))
prov = st.sidebar.multiselect(
    "choisé l'arrondissement' :",
    options=df["arrondissement"].unique(),
    default=df["arrondissement"].unique()
)
city = st.sidebar.multiselect(
    "choisé le bureau :",
    options=df["bureau"].unique(),
    default=df["bureau"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select la categorie d'age:",
    options=df["age"].unique(),
    default=df["age"].unique(),
)

gender = st.sidebar.multiselect(
    "Select le sexe:",
    options=df["sexe"].unique(),
    default=df["sexe"].unique()
)
print(city)
df_selection = df.query(
    "arrondissement == @prov & bureau == @city & age ==@customer_type & sexe == @gender"
)
df_selectionNN = dfNN.query(
    "arrondissement == @prov & bureau == @city      "
)

# ---- MAINPAGE ----
st.title(":bar_chart: page des statistics ")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["satisfait_score"].count())
average_rating = round(df_selection["satisfait_score"].mean()*2.5, 1)
star_rating = ":star:" * int(round(average_rating, 0))


left_column, middle_column = st.columns(2)
with left_column:
    st.subheader("la taille de population :")
    st.subheader(f" {total_sales:,}")
with middle_column:
    st.subheader("le moyen de taux de satisfait sur 10:")
    st.subheader(f"{average_rating} {star_rating}")


st.markdown("""---""")

# SALES BY PRODUCT LINE [BAR CHART]
def provinceGraphe():
    
    sales_by_product_line = (
        df_selection.groupby(by=["arrondissement"]).sum()[["satisfait_score"]].sort_values(by="satisfait_score")
    )
    fig_product_sales = px.bar(
        sales_by_product_line,
        x="satisfait_score",
        y=sales_by_product_line.index,
        orientation="h",
        color='satisfait_score',
        template="plotly_white",
    )
    fig_product_sales.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    return fig_product_sales

# SALES BY HOUR [BAR CHART]
def jourFouleGraph():
    sales_by_hour = df_selectionNN.groupby(by=["jourFoule"]).sum()[["la foule"]]
    fig_hourly_sales = px.bar(
        sales_by_hour,
        x=sales_by_hour.index,
        y="la foule",
        color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
        template="plotly_white",
    )
    fig_hourly_sales.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    return fig_hourly_sales

def visiteGraph():
    
    satisfaitFunction =df_selection.groupby(['visite_score']).mean()['satisfait_score']
    
    fig_satisfait = px.bar(
        satisfaitFunction,
        template="plotly_white",
    )
    fig_satisfait.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    return fig_satisfait
def problemesGraph():
    deProblemes=df_selection.drop(['sexe','arrondissement','bureau','visite_score','satisfait_score'
    ,'les_horaires','jourFoule','bureauAvis','amileoration'],axis=1)
    problemFunction =deProblemes.groupby(['age']).count()
    fig_probleme = px.bar(
        problemFunction,
        color='la foule',
        template="plotly_white",
    )
    fig_probleme.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )

# SALES BY HOUR [BAR CHART]
def graphProblemes():
    data=df_selectionNN.groupby(['arrondissement'])['la foule','Manque des employé','mauvaise maniere Traitement'].sum()
    st.bar_chart(data)
def graphJourFoule():

  data=df_selection["jourFoule"].value_counts()
 # test.groupby(['jourFoule']).mean().plot.bar()

  st.bar_chart(data)

def graphheurFoule():

  data=df_selection["les_horaires"].value_counts()
 # test.groupby(['jourFoule']).mean().plot.bar()

  st.bar_chart(data)


def bar_chart():
    #Creating the dataset
  fig, ax = plt.subplots()
  data=df_selection.groupby(['jourFoule']).mean()
 # test.groupby(['jourFoule']).mean().plot.bar()

  st.bar_chart(data)
  
def bar_chartBureau():
    #Creating the dataset
  fig, ax = plt.subplots()

  data=df_selection.groupby(['bureau'])['satisfait_score'].mean() # test.groupby(['jourFoule']).mean().plot.bar()

  st.bar_chart(data)
def bar_chartTest():
    #Creating the dataset
    
  s=0
  donneee=df_selection.drop(['bureau'],axis=1)
  for col in donneee :
    s=s+1
    data=donneee[col].value_counts()
   # st.pie_chart(data)
    
    fig = go.Figure(
    go.Pie(
    labels = data.index ,
    values = data.values ,
    hoverinfo = "label+percent",
    textinfo = "value"
))
    if s>3:
            s=s-3
        

    

    if s==1:
            
            left_column, middle_column, right_column = st.columns(3)
            with left_column:
                st.write(" le percentage de  "+ col +" l'echantillon")
            
                st.plotly_chart(fig, use_container_width=True)
    if s==2:
            
            with middle_column:
                st.write(" le percentage de  "+ col +" l'echantillon")
            
                st.plotly_chart(fig, use_container_width=True)
    if s==3:

            with right_column:
                st.write(" le percentage de  "+ col +" l'echantillon")
            
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""---""")

#def bar_chartTest3():
    #    df = df_selection[['la foule','Manque des employé','mauvaise maniere Traitement']].value_counts()
     #   group_labels = ['la foule','Manque des employé','mauvaise maniere Traitement']
      #  fig = ff.create_distplot(
       # df.index,df.values)
        #st.plotly_chart(fig)

satisfait=df_selection[df_selection['satisfait_score']>2]
insatisfait=df_selection[df_selection['satisfait_score']<3]
def bar_chartTest2():
    #Creating the dataset
  st.header("etude sur les variable qui impact le taux de satisfaction")
  for col in df_selection :
      if col=='satisfait_score':
          n=1
      else:
              
        st.write("la relation entre   "+ col +" et le teux de satisfaction")
    

    

        data=df_selection.groupby([col])['satisfait_score'].mean()
        st.bar_chart(data)
        
   # st.bar_chart(df)
def communeRapport():
    
    data=df_selection.groupby('arrondissement').mean()
    st.bar_chart(data)
def bar_chartcommunication():
    #Creating the dataset
    fig = plt.figure(figsize=(10, 4))
    sns.histplot(x='age',hue='sexe',data=df_selection,linewidth=1)
    sns.set_style("dark")
    st.pyplot(fig)
def bar_chartAgeFoule():
    #Creating the dataset
    fig = plt.figure(figsize=(10, 4))
    sns.countplot(x='age',hue='la foule',data=df_selection,linewidth=1)
    sns.set_style("dark")
    st.pyplot(fig)
    
def provinceGraphs():
    jnan_el_ward=df_selection[df_selection['arrondissement']=='JNAN EL WARD']
    AGDAL=df_selection[df_selection['arrondissement']=='AGDAL']
    t=0
    for col in df_selection:
        t=t+1
        fig = plt.figure(figsize=(10,6))
        colors = sns.color_palette('bright') 
        
        sns.histplot(AGDAL[col], kde=True, stat="probability",label='ZOUGHA',linewidth=0, color='red')
        sns.histplot(jnan_el_ward[col], kde=True, stat="probability",label='JNAN EL WARD',linewidth=0,color='blue')
    
        sns.set_palette("Paired")
        plt.legend()
    #Creating the dataset

       
        if t>3:
            t=t-3
        if t==1:
            
            left, middle, right = st.columns(3)
        
            with left:
                st.subheader(f"la relation entre l'arrondissement et  {col}")

                st.pyplot(fig)
        if t==2:
            
            with middle:
                    st.subheader(f"la relation entre l'arrondissement et  {col}")
                    st.pyplot(fig)

        if t==3:
             
             with right:
                     st.subheader(f"la relation entre l'arrondissement et  {col}")
                     st.pyplot(fig)
              



def ageGraph():
      #Creating the dataset
    fig, ax = plt.subplots()
    data=df_selection.groupby(['age']).mean()['satisfait_score']
   # test.groupby(['jourFoule']).mean().plot.bar()

    st.bar_chart(data,use_container_width=True)
  
def tableDescribe():
    #Creating the dataset
  
  fig, ax = plt.subplots()
  data=df_selection.describe()
 # test.groupby(['jourFoule']).mean().plot.bar()
  st.table(data)



def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)

    return base64.b64encode(img.getvalue())

#encoded = fig_to_base64(fig)
#my_html = '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))

if add_selectbox=="dashbord de population":
        
    left_column, right_column = st.columns(2)
    colometrois,colomneQuatre = st.columns(2)
            
    
    
  
    bar_chartBureau()

    

    left_column.plotly_chart(provinceGraphe(), use_container_width=True)
    right_column.plotly_chart( visiteGraph(), use_container_width=True)
    
    colometrois.plotly_chart(jourFouleGraph(), use_container_width=True)

           
    
    st.write("chart de population par les problemes les plus connu ")
    graphProblemes()
    st.write("chart de les heures plus frequence ")
    graphheurFoule() 
    bar_chartTest()
    

        


if add_selectbox=="analyse de  taux de satisfait":
    bar_chartcommunication()
    bar_chartTest2()
    ageGraph()

if add_selectbox=="comparaison entre Arrendissement":
        communeRapport()
        provinceGraphs()
    
    













#bar_chart()
#graphheurFoule()
#bar_chartTest()
#bar_chartTest3()
#bar_chartAgeFoule()
#provinceGraphs()
# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)