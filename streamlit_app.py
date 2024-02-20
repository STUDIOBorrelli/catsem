import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
st.set_page_config(page_title="My App")
class var():

    OPZIONI1 = ["ATTRAVERSAMENTO","DISSUASORE",
               "SEMAFORO-"]
    OPZIONI = {"ATT-": "ATT-",
               "DIS-": "DIS-",
               "LAM-": "LAM-",
               "PMW-": "PMW-",
               "RLA-": "12345",
               "SEM-": "SEM-"}

#dictionary = var.OPZIONI
Aggiornamento='2.02 '
def fun_df():
    import pandas as pd
    path='C:\\Users\\gianni\\Desktop\\Nuova cartella\\semafori\\'
    file='ARCHIVIO_2.00.xlsx' 
    df = pd.read_excel(path+file)
    return df    


def fun_num_totali(df):
    count_total=df.shape[0]
    return count_total


def fun_maps():
        df=fun_df()
        num_prov=df.shape[0]
        #print(num_prov)
        LAT=(16.853946431342074)
        LONG=(41.10924724693509)
        m = folium.Map(location=[LONG,LAT], zoom_start=12)
        for i in range(num_prov):
            coordx=(df.iloc[i,2])
            coordy=(df.iloc[i,3])
            incr=(df.iloc[i,0])
            nome=(df.iloc[i,1])
            iden=str((df.iloc[i,4]))
            tip=(df.iloc[i,8])#tipologia elemento
            iden6=(iden[6]) #num elemento
            #messaggio = f"Ciao, lidentificativo è {iden6} le coordx sono {LAT} mentre le coordx sono {LONG} anni."
            folium.Marker(
            location=[coordy,coordx],popup=(nome,tip,iden6),icon=folium.DivIcon(html=f"""<div style="font: arial; font-size: 60px; color: red">{'.'}</div>""")
            ).add_to(m)
        st_folium(m, width=725,height=400 , returned_objects=[])    #width=725,height=400 
        return
def fun_maps_dett():
        LAT=(fun_nome_LAT_X_E(fun_filtro_risul(fun_df(),selected_section,nomeric))) #41.10924724693509
        LONG=(fun_nome_LONG_Y_N(fun_filtro_risul(fun_df(),selected_section,nomeric))) #16.853946431342074
        m = folium.Map(location=[LONG,LAT], zoom_start=30)
        folium.Marker([LONG,LAT], popup=nome_incrocio, tooltip=nome_incrocio).add_to(m)
        st_folium(m, width=725,height=400, returned_objects=[])#defoult= width=725 width=500,height=500,location=[40, -99], zoom_start=4)
        
        return
#-----------------------------------------------

nomeric='000'
#-----------------------------------------------
#-----------------------------------------------
#st.markdown("<h3 style='text-align: center; color: grey;'>CITTA' DI BARI</h3>", unsafe_allow_html=True)
col1, col2, col3, = st.columns(3)
with col1:
    st.caption('Elem. Analizzati:')
    st.code(fun_num_totali(fun_df()))
with col2:
    st.write("")
    st.markdown("<h3 style='text-align: center; color: grey;'>CITTA' DI BARI</h3>", unsafe_allow_html=True)
    #st.caption('Cod. Incrocio Selezionato:')
    #st.code(selected_section+nomeric)
with col3:
    st.caption('Versione '+'Archivio: ')
    st.code(Aggiornamento)
    
#st.caption(':blue[_cod. incrocio selezionato:_]')
#st.write('Elem. Analizzati:', fun_num_totali(fun_df()))

#-----------------------------------------------

if nomeric=='000':
    fun_maps()       
else:
    fun_maps_dett()

       

# streamlit run strim.py
