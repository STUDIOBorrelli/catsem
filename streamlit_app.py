import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
class var():
    #ID.IMP	NOME_IMP	LAT_X_E	LONG_Y_N	ID.ELEM	TIPOLOGIA	FOTO 1	FOTO 2	SOSTEGNO	LANT_BASSE	LANT_ALTE	LANT_PEDO	PRESENZA_L	PRESENZA_P	PRESENZA_1	PRESENZA_2	PRESENZA_D	CENTRALINA	MODELLO	CENTRALIZZ	USCITE	FUNZIONAME	TIPO_SENSO	tipologia_x_ric
    GG='C:\\Users\\gianni\\Desktop\\Appunti0123.jpg'
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
    path='C:\\Users\\gianni\\Desktop\\Nuova cartella\\Streamlit\\'
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
    st.code(fun_num_totali(fun_df()))
with col2:
    st.caption('Cod. Incrocio Selezionato:')
    st.code(selected_section+nomeric)
with col3:
    st.caption(Aggiornamento[0]+Aggiornamento[1])
    st.code(Aggiornamento[2])
    
#st.caption(':blue[_cod. incrocio selezionato:_]')
#st.write('Elem. Analizzati:', fun_num_totali(fun_df()))

#-----------------------------------------------

tab1, tab2, tab3, tab4, tab5,= st.tabs(["HOME", "MAPPA", "DETTAGLI", "MAPPA", "STAMPA PDF"])
with tab1:
    
    col1, col2, = st.columns(2)
    #st.text_input(label)
    with col1:
        #nomeric=st.text_input("inserire **numero** dell'incrocio:",value='000')
        col21, col22, = st.columns(2)
        with col21:
            st.caption(':blue[_Elem. Analizzati:_]')
            st.code(fun_num_totali(fun_df()))
            st.caption('A caption with _italics_ :blue[colors] and emojis :sunglasses:')
        with col22:
            st.caption(':blue[_Cod. Incrocio Selezionato:_]')
            st.code(selected_section+nomeric)
            #st.write(r"$\textsf{\normalsize ",selected_section+nomeric,"}$")
            #st.write('Totali Elementi Filtrati:', r"$\textsf{\normalsize ",fun_num_filtrati(fun_filtro_risul(fun_df(),selected_section,nomeric)),"}$" )
            #st.write('Tot. Elem. Filtrati:', fun_num_filtrati(fun_filtro_risul(fun_df(),selected_section,nomeric)))
            st.caption(':blue[_Tot. Elem. Filtrati:_]', )
            st.code(fun_num_filtrati(fun_filtro_risul(fun_df(),selected_section,nomeric)))
            
    
    with col2:
        #st.header("An owl")
        image =selected_section+nomeric+'.jpg'
        st.image(image)
        st.caption(':blue[_Nome Incrocio_]')
        st.write(fun_nome_incrocio(fun_filtro_risul(fun_df(),selected_section,nomeric)))
        #st.write(fun_nome_incrocio(fun_filtro_risul(fun_df(),selected_section,nomeric)))
    col31, col32, col33, = st.columns(3)
    with col31:
        st.caption('A **caption** with _italics_ :blue[colors] and emojis :sunglasses:')
    with col32:
        st.caption('A caption with _italics_ :blue[colors] and emojis :sunglasses:')
    with col33:
        st.link_button("Foto 1", fun_nome_foto1((fun_filtro_risul(fun_df(),selected_section,nomeric))))
    
with tab2:

    LAT=(fun_nome_LAT_X_E(fun_filtro_risul(fun_df(),selected_section,nomeric))) #41.10924724693509
    LONG=(fun_nome_LONG_Y_N(fun_filtro_risul(fun_df(),selected_section,nomeric))) #16.853946431342074
    # center on Liberty Bell, add marker
    m = folium.Map(location=[LONG,LAT], zoom_start=16)
    folium.Marker(
        [LONG,LAT], popup="", tooltip=""
    ).add_to(m)

    # call to render Folium map in Streamlit, but don't get any data back
    # from the map (so that it won't rerun the app when the user interacts)
    st_folium(m, width=725, returned_objects=[])
    
    col1, col2, col3 = st.columns([1,6,1])
    with col1:
        st.write("")
    with col2:
        st.write("")
        
    with col3:
        st.write("")
    st.markdown("This is **bold** text in markdown")
    st.write('CATASTO_prova.xlsx')
with tab3:
    st.caption("Dettagli sull'incrocio selezionato")
    options = ['ID.ELEM',
'TIPOLOGIA',
'SOSTEGNO',
'LANT_BASSE',
'LANT_ALTE',
'LANT_PEDO',
] 
    st.dataframe(fun_df()[fun_df()['ID.IMP']==selected_section+nomeric][options])
with tab4:
    st.caption("Dettagli sull'incrocio selezionato")
    options = st.multiselect(
        'Scelta OPZIONI',
        var.INDEX,
        ['ID.IMP', 'ID.ELEM', 'TIPOLOGIA','SOSTEGNO'],
        help='SELEZIONA LE OPZIONI DA VISUALIZZARE')
    st.dataframe(fun_df()[fun_df()['ID.IMP']==selected_section+nomeric][options])   
    
with tab5:
   
    st.title(selected_section+nomeric)
    st.subheader(fun_nome_incrocio(fun_filtro_risul(fun_df(),selected_section,nomeric)))
   

# streamlit run strim.py
