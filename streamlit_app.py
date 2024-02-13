import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
class var():
    #ID.IMP	NOME_IMP	LAT_X_E	LONG_Y_N	ID.ELEM	TIPOLOGIA	FOTO 1	FOTO 2	SOSTEGNO	LANT_BASSE	LANT_ALTE	LANT_PEDO	PRESENZA_L	PRESENZA_P	PRESENZA_1	PRESENZA_2	PRESENZA_D	CENTRALINA	MODELLO	CENTRALIZZ	USCITE	FUNZIONAME	TIPO_SENSO	tipologia_x_ric
    #GG='C:\\Users\\gianni\\Desktop\\Appunti0123.jpg'
    OPZIONI = {"ATT-": "ATT-",
               "DIS-": "DIS-",
               "LAM-": "LAM-",
               "PMW-": "PMW-",
               "RLA-": "12345",
               "SEM-": "SEM-"}
    INDEX={'ID.IMP':'ID.IMP',
           'NOME_IMP':'NOME_IMP',
           'LAT_X_E':'LAT_X_E',
           'LONG_Y_N':'LONG_Y_N',
           'ID.ELEM':'ID.ELEM',
           'TIPOLOGIA':'TIPOLOGIA',
           'FOTO 1':'FOTO 1',
           'FOTO 2':'FOTO 2',
           'SOSTEGNO':'SOSTEGNO',
           'LANT_BASSE':'LANT_BASSE',
           'LANT_ALTE':'LANT_ALTE',
           'LANT_ PEDONALE':'LANT_ PEDONALE',
           'PRESENZA_LANT_BICI':'PRESENZA_LANT_BICI',
           'PRESENZA_PULSANTE':'PRESENZA_PULSANTE',
           'PRESENZA_LANT_TRAM':'PRESENZA_LANT_TRAM',
           'PRESENZA_LANT_C_DOWN':'PRESENZA_LANT_C_DOWN',
           'PRESENZA_DISP_ACUSTICO':'PRESENZA_DISP_ACUSTICO',
           'CENTRALINA':'CENTRALINA',
           'MODELLO':'MODELLO',
           'CENTRALIZZ':'CENTRALIZZ',
           'USCITE':'USCITE',
           'FUNZIONAME':'FUNZIONAME',
           'TIPO_SENSO':'TIPO_SENSO'}
#nomeric='000'
dictionary = var.OPZIONI
Aggiornamento=('Versione ','Archivio ','2.03 ')
def fun_df():
    import pandas as pd
    path='/catsem/'
    #path='C:\\Users\\gianni\\Desktop\\Nuova cartella\\Streamlit\\'
    file='ARCHIVIO_2.00.xlsx' 
    df = pd.read_excel(path+file)
    return df    
    
def fun_filtro_risul(df,selected_section,nomeric):
    RISUL =(df[df['ID.IMP']==selected_section+nomeric])
    return RISUL

def gg1(RISUL):
    kk=(RISUL.filter(items=['ID.IMP']))
    return kk

def fun_num_totali(df):
    count_total=df.shape[0]
    return count_total

def fun_num_filtrati(RISUL):
    count_filter=RISUL.shape[0]
    return count_filter

def fun_nome_incrocio(RISUL):
    nome_incrocio=RISUL.iloc[1][1]
    return nome_incrocio

def fun_nome_foto1(RISUL):
    nome_foto1=RISUL.iloc[1][1]
    return nome_foto1

def fun_nome_LAT_X_E(RISUL):
    nome_foto1=RISUL.iloc[1][2]
    return nome_foto1
def fun_nome_LONG_Y_N(RISUL):
    nome_foto1=RISUL.iloc[1][3]
    return nome_foto1

#-----------------------------------------------
st.markdown("<h2 style='text-align: center; color: grey;'>CATASTO SEMAFORI</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: grey;'>CITTA' DI BARI</h3>", unsafe_allow_html=True)
selected_section = st.sidebar.selectbox("Seleziona tipologia incrocio:", sorted(dictionary.keys()))
nomeric=st.sidebar.text_input("inserire **numero** dell'incrocio:",value='000')
selected_page = st.sidebar.radio("Choose page:", sorted(dictionary[selected_section])) #-----------------------------------------------
#-----------------------------------------------
col1, col2, col3, = st.columns(3)
with col1:
    st.caption('Elem. Analizzati:')

with col2:
    st.caption('Cod. Incrocio Selezionato:')

with col3:
    st.caption('Cod. Incrocio Selezionato:')
    
#st.caption(':blue[_cod. incrocio selezionato:_]')
#st.write('Elem. Analizzati:', fun_num_totali(fun_df()))

#-----------------------------------------------


# streamlit run streamlit_app.py
