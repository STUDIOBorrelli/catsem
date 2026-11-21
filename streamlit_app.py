import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle, PageBreak)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium


def _esc_pdf(v):
    """Escape minimale per Paragraph di reportlab."""
    if pd.isna(v):
        return ""
    s = str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;"))


def genera_pdf(df, selected_section):
    """Costruisce un PDF in memoria con i dati dell'impianto selezionato.
    Ritorna i bytes del PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title=f"Impianto {selected_section} - Città di Bari",
        author="Archivio Semafori Bari",
    )
    styles = getSampleStyleSheet()
    st_title = ParagraphStyle("t", parent=styles["Heading1"],
                              alignment=TA_CENTER, textColor=colors.HexColor("#333333"))
    st_h2 = ParagraphStyle("h2", parent=styles["Heading2"],
                           textColor=colors.HexColor("#444444"), spaceBefore=8)
    st_norm = styles["Normal"]
    st_small = ParagraphStyle("s", parent=styles["Normal"], fontSize=7.5, leading=9)

    story = []

    # --- Intestazione ---
    story.append(Paragraph("CITTÀ DI BARI", st_title))
    story.append(Paragraph("Archivio impianti semaforici", st_h2))
    story.append(Paragraph(
        f"Versione archivio: {Aggiornamento} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}", st_norm))
    story.append(Spacer(1, 6*mm))

    if selected_section == "TUTTI":
        # ---- PDF riepilogativo di tutto l'archivio ----
        story.append(Paragraph("Riepilogo generale archivio", st_h2))
        tipi = df[df.columns[COL_TIPOLOGIA]].astype(str).value_counts()
        dati = [["Tipologia", "N."]] + [[t, str(n)] for t, n in tipi.items()]
        t = Table(dati, colWidths=[120*mm, 30*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e0e0e0")),
            ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ]))
        story.append(t)
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(
            f"<b>Totale impianti:</b> {df[df.columns[COL_ID_IMP]].nunique()} "
            f"&nbsp;&nbsp; <b>Totale elementi:</b> {len(df)}", st_norm))
    else:
        # ---- PDF di dettaglio impianto ----
        df_sel = df[df[df.columns[COL_ID_IMP]] == selected_section].copy()
        nome = str(df_sel.iloc[0, COL_NOME_IMP])
        story.append(Paragraph(f"Impianto: {_esc_pdf(nome)}", st_h2))

        # Info impianto (dalla centralina o prima riga)
        riga_centr = df_sel[df_sel[df_sel.columns[COL_TIPOLOGIA]]
                            .astype(str).str.upper() == "CENTRALINA"]
        riga_rif = riga_centr.iloc[0] if not riga_centr.empty else df_sel.iloc[0]

        campi = [
            ("ID Impianto",      df.columns[COL_ID_IMP]),
            ("Nome",             df.columns[COL_NOME_IMP]),
            ("Modello",          "MODELLO"),
            ("Centralizzazione", "CENTRALIZZ"),
            ("Uscite",           "USCITE"),
            ("Funzionamento",    "FUNZIONAME"),
            ("Tipo senso",       "TIPO_SENSO"),
        ]
        info = []
        for label, col in campi:
            if isinstance(col, int):
                val = riga_rif.iloc[col]
            else:
                match = [c for c in df.columns
                         if str(c).strip().upper() == col.upper()]
                val = riga_rif[match[0]] if match else ""
            if pd.isna(val) or str(val).strip().lower() in ("", "false"):
                continue
            info.append([label, _esc_pdf(val)])

        t = Table(info, colWidths=[45*mm, 105*mm])
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f0f0f0")),
            ("FONTSIZE", (0,0), (-1,-1), 8.5),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(t)

        # Conteggio per tipologia
        story.append(Paragraph("Elementi presenti", st_h2))
        tipi = df_sel[df_sel.columns[COL_TIPOLOGIA]].astype(str).value_counts()
        dati = [["Tipologia", "N."]] + [[t, str(n)] for t, n in tipi.items()]
        t2 = Table(dati, colWidths=[120*mm, 30*mm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e0e0e0")),
            ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ]))
        story.append(t2)

        # Dettaglio elementi
        story.append(Paragraph("Dettaglio elementi", st_h2))
        cols_dett = [df.columns[COL_ID_ELEM], df.columns[COL_TIPOLOGIA],
                     "SOSTEGNO", "LANT_BASSE", "LANT_ALTE", "LANT_ PEDO",
                     "PRESENZA_L", "PRESENZA_P", "PRESENZA_1",
                     "PRESENZA_2", "PRESENZA_D"]
        cols_dett = [c for c in cols_dett if c in df_sel.columns]
        df_dett = df_sel[cols_dett].copy().replace({False: "", True: "✔"})

        header = [Paragraph(f"<b>{_esc_pdf(c)}</b>", st_small) for c in df_dett.columns]
        body = []
        for _, r in df_dett.iterrows():
            body.append([Paragraph(_esc_pdf(v), st_small) for v in r.values])
        # larghezze proporzionali (A4 utile ~180mm)
        ncol = len(header)
        larghezze = [180*mm/ncol]*ncol
        t3 = Table([header]+body, colWidths=larghezze, repeatRows=1)
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d8d8d8")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("FONTSIZE", (0,0), (-1,-1), 7),
        ]))
        story.append(t3)

        # Link foto
        foto_col = [c for c in df_sel.columns if str(c).upper().startswith("FOTO")]
        if foto_col:
            foto = df_sel[foto_col[0]].dropna()
            if not foto.empty and str(foto.iloc[0]).startswith("http"):
                story.append(Spacer(1, 4*mm))
                story.append(Paragraph(
                    f'<a href="{_esc_pdf(foto.iloc[0])}" color="blue">'
                    f'Foto su Google Maps</a>', st_norm))

    doc.build(story)
    return buf.getvalue()


def pdf_download_button(pdf_bytes, filename):
    """Mostra il pulsante che apre la finestra 'Apri o Salva' del browser."""
    b64 = base64.b64encode(pdf_bytes).decode()
    # Link data:URI -> il browser mostra la sua dialog nativa apri/salva
    href = f"data:application/pdf;base64,{b64}"
    components.html(
        f"""
        <a href="{href}" download="{filename}" target="_blank"
           style="display:inline-block; padding:10px 18px; background:#0068c9;
                  color:white; border-radius:6px; text-decoration:none;
                  font-family:sans-serif; font-weight:600;">
            📄 Genera PDF (apri o salva)
        </a>
        """,
        height=60,
    )

st.set_page_config(page_title="My App", layout="wide")

class var():
    OPZIONI1 = ["ATTRAVERSAMENTO", "DISSUASORE", "SEMAFORO-"]
    OPZIONI = {"ATT-": "ATT-", "DIS-": "DIS-", "LAM-": "LAM-",
               "PMW-": "PMW-", "RLA-": "12345", "SEM-": "SEM-"}

Aggiornamento = '2.02'

@st.cache_data
def fun_df():
    return pd.read_excel('ARCHIVIO_2.00.xlsx')

def fun_num_totali(df):
    return df.shape[0]

# Colonne (0-based) dal file Excel:
# 0=ID.IMP 1=NOME_IMP 2=LAT_X_E 3=LONG_Y_N 4=ID.ELEM ... 8=SOSTEGNO? 
# NB: nel codice originale il commento dice "tipologia elemento" su iloc[:,8],
# ma la colonna 8 è SOSTEGNO; TIPOLOGIA è la colonna 5 (F).
# Qui uso TIPOLOGIA (colonna 5) come da intestazione.
COL_ID_IMP   = 0
COL_NOME_IMP = 1
COL_LON_X    = 2
COL_LAT_Y    = 3
COL_ID_ELEM  = 4
COL_TIPOLOGIA= 5

def fun_maps(df):
    """Mappa con tutti gli impianti (un marker per impianto, non per elemento)."""
    # Prendo un solo record per impianto (il primo) per non sovrapporre marker
    df_imp = df.drop_duplicates(subset=[df.columns[COL_ID_IMP]]).copy()

    # Centro mappa: media delle coordinate valide
    lats = pd.to_numeric(df_imp.iloc[:, COL_LAT_Y], errors='coerce')
    lons = pd.to_numeric(df_imp.iloc[:, COL_LON_X], errors='coerce')
    mask = lats.notna() & lons.notna()
    if mask.any():
        center = [lats[mask].mean(), lons[mask].mean()]
    else:
        center = [41.1092, 16.8539]  # Bari (lat, lon)

    m = folium.Map(location=center, zoom_start=12)

    for i in range(len(df_imp)):
        if not mask.iloc[i]:
            continue
        lat = float(lats.iloc[i])
        lon = float(lons.iloc[i])
        nome = str(df_imp.iloc[i, COL_NOME_IMP])
        id_imp = str(df_imp.iloc[i, COL_ID_IMP])
        tip = str(df_imp.iloc[i, COL_TIPOLOGIA])
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{nome}</b><br>ID: {id_imp}<br>Tipologia: {tip}",
            tooltip=nome,
            icon=folium.DivIcon(
                html='<div style="font: arial; font-size: 60px; color: red">.</div>'
            )
        ).add_to(m)
    return m

def fun_maps_dett(df, id_imp):
    """Mappa di dettaglio: tutti gli elementi dell'impianto selezionato."""
    df_sel = df[df[df.columns[COL_ID_IMP]] == id_imp].copy()
    if df_sel.empty:
        st.warning("Nessun elemento trovato per l'impianto selezionato.")
        return None

    lats = pd.to_numeric(df_sel.iloc[:, COL_LAT_Y], errors='coerce')
    lons = pd.to_numeric(df_sel.iloc[:, COL_LON_X], errors='coerce')
    mask = lats.notna() & lons.notna()
    if not mask.any():
        st.warning("Coordinate non valide per l'impianto selezionato.")
        return None

    center = [lats[mask].mean(), lons[mask].mean()]
    nome_incrocio = str(df_sel.iloc[0, COL_NOME_IMP])

    m = folium.Map(location=center, zoom_start=19)

    for i in range(len(df_sel)):
        if not mask.iloc[i]:
            continue
        lat = float(lats.iloc[i])
        lon = float(lons.iloc[i])
        id_elem = str(df_sel.iloc[i, COL_ID_ELEM])
        tip = str(df_sel.iloc[i, COL_TIPOLOGIA])
        sostegno = str(df_sel.iloc[i, 8]) if df_sel.shape[1] > 8 else ""
        colore = "red" if "SEMAFORO" in tip.upper() else "blue"
        folium.Marker(
            location=[lat, lon],
            popup=(f"<b>{nome_incrocio}</b><br>ID.ELEM: {id_elem}"
                   f"<br>Tipologia: {tip}<br>Sostegno: {sostegno}"),
            tooltip=f"{id_elem} - {tip}",
            icon=folium.DivIcon(
                html=f'<div style="font: arial; font-size: 40px; color: {colore}">●</div>'
            )
        ).add_to(m)
    return m, nome_incrocio

# ------------------------------------------------------------------
# ------------------------------------------------------------------
# ... (funzioni e header restano identici) ...
# ------------------------------------------------------------------

df = fun_df()

# --- Header ---
col1, col2, col3 = st.columns(3)
with col1:
    st.caption('Elem. Analizzati:')
    st.code(fun_num_totali(df))
with col2:
    st.write("")
    st.markdown("<h3 style='text-align: center; color: grey;'>CITTA' DI BARI</h3>",
                unsafe_allow_html=True)
with col3:
    st.caption('Versione Archivio:')
    st.code(Aggiornamento)

# --- Selettore impianto ---
id_disponibili = sorted(df[df.columns[COL_ID_IMP]].dropna().unique().tolist())
opzioni = ["TUTTI"] + id_disponibili
selected_section = st.selectbox("Seleziona impianto:", opzioni, index=0)

# --- CSS: box con bordo + scroll, responsive, cross-browser ---
st.markdown("""
<style>
/* Contenitore generico con bordo e scroll, compatibile con tutti i browser */
.info-frame {
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    padding: 12px 14px;
    background-color: #fafafa;
    max-height: 600px;          /* stessa altezza della mappa */
    overflow-y: auto;           /* scroll verticale */
    overflow-x: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    /* scrollbar sottile e coerente cross-browser */
    scrollbar-width: thin;                 /* Firefox */
    scrollbar-color: #bbb #f0f0f0;         /* Firefox */
}
/* WebKit (Chrome, Edge, Safari) */
.info-frame::-webkit-scrollbar { width: 8px; }
.info-frame::-webkit-scrollbar-track { background: #f0f0f0; border-radius: 4px; }
.info-frame::-webkit-scrollbar-thumb { background: #bbb; border-radius: 4px; }
.info-frame::-webkit-scrollbar-thumb:hover { background: #999; }

/* Titoletti interni */
.info-frame h4 { margin: 10px 0 4px 0; font-size: 1rem; color: #333; }
.info-frame h4:first-child { margin-top: 0; }

/* Tabelle interne compatte */
.info-frame table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.info-frame table th { text-align: left; background: #eee; padding: 4px 6px; }
.info-frame table td { padding: 3px 6px; border-bottom: 1px solid #eaeaea; }

/* Su schermi stretti (mobile/tablet) impila mappa e pannello */
@media (max-width: 768px) {
    .info-frame { max-height: 400px; }
}
</style>
""", unsafe_allow_html=True)

# --- Funzione che costruisce l'HTML del pannello dati ---
def build_info_html(df, selected_section):
    """Ritorna una stringa HTML con tutti i dati dell'impianto selezionato."""
    import html as _html  # per escaping sicuro

    def esc(v):
        return _html.escape(str(v)) if not pd.isna(v) else ""

    # Se "TUTTI": panoramica generale
    if selected_section == "TUTTI":
        tipi = df[df.columns[COL_TIPOLOGIA]].astype(str).value_counts()
        rows = "".join(
            f"<tr><td>{esc(t)}</td><td style='text-align:right'>{n}</td></tr>"
            for t, n in tipi.items()
        )
        return f"""
        <div class="info-frame">
            <h4>Panoramica archivio</h4>
            <table>
                <tr><th>Tipologia</th><th style='text-align:right'>N.</th></tr>
                {rows}
            </table>
            <h4>Totali</h4>
            <table>
                <tr><td>Impianti</td><td style='text-align:right'>
                    {df[df.columns[COL_ID_IMP]].nunique()}</td></tr>
                <tr><td>Elementi</td><td style='text-align:right'>{len(df)}</td></tr>
            </table>
        </div>
        """

    # Se impianto specifico
    df_sel = df[df[df.columns[COL_ID_IMP]] == selected_section].copy()

    # 1) Info impianto dalla riga centralina (o prima riga)
    riga_centr = df_sel[df_sel[df_sel.columns[COL_TIPOLOGIA]]
                        .astype(str).str.upper() == "CENTRALINA"]
    riga_rif = riga_centr.iloc[0] if not riga_centr.empty else df_sel.iloc[0]

    campi_impianto = [
        ("ID Impianto",      df.columns[COL_ID_IMP]),
        ("Nome",             df.columns[COL_NOME_IMP]),
        ("Modello",          "MODELLO"),
        ("Centralizzazione", "CENTRALIZZ"),
        ("Uscite",           "USCITE"),
        ("Funzionamento",    "FUNZIONAME"),
        ("Tipo senso",       "TIPO_SENSO"),
    ]
    info_rows = ""
    for label, col in campi_impianto:
        if isinstance(col, int):
            val = riga_rif.iloc[col]
        else:
            match = [c for c in df.columns
                     if str(c).strip().upper() == col.upper()]
            val = riga_rif[match[0]] if match else ""
        if pd.isna(val) or str(val).strip().lower() in ("", "false"):
            continue
        info_rows += f"<tr><td>{esc(label)}</td><td>{esc(val)}</td></tr>"

    # 2) Conteggio per tipologia
    tipi = df_sel[df_sel.columns[COL_TIPOLOGIA]].astype(str).value_counts()
    tipi_rows = "".join(
        f"<tr><td>{esc(t)}</td><td style='text-align:right'>{n}</td></tr>"
        for t, n in tipi.items()
    )

    # 3) Dettaglio elementi (tabella compatta)
    cols_dett = [df.columns[COL_ID_ELEM], df.columns[COL_TIPOLOGIA],
                 "SOSTEGNO", "LANT_BASSE", "LANT_ALTE", "LANT_ PEDO",
                 "PRESENZA_L", "PRESENZA_P", "PRESENZA_1",
                 "PRESENZA_2", "PRESENZA_D"]
    cols_dett = [c for c in cols_dett if c in df_sel.columns]
    df_dett = df_sel[cols_dett].copy().replace({False: "", True: "✔"})

    header = "".join(f"<th>{esc(c)}</th>" for c in df_dett.columns)
    body = ""
    for _, r in df_dett.iterrows():
        body += "<tr>" + "".join(f"<td>{esc(v)}</td>" for v in r.values) + "</tr>"

    # 4) Link foto
    foto_col = [c for c in df_sel.columns if str(c).upper().startswith("FOTO")]
    link_foto = ""
    if foto_col:
        foto = df_sel[foto_col[0]].dropna()
        if not foto.empty and str(foto.iloc[0]).startswith("http"):
            url = _html.escape(str(foto.iloc[0]), quote=True)
            link_foto = f'<h4>Foto</h4><a href="{url}" target="_blank">📷 Apri su Google Maps</a>'

    return f"""
    <div class="info-frame">
        <h4>Informazioni impianto</h4>
        <table>{info_rows}</table>
        <h4>Elementi presenti</h4>
        <table>
            <tr><th>Tipologia</th><th style='text-align:right'>N.</th></tr>
            {tipi_rows}
        </table>
        <h4>Dettaglio elementi</h4>
        <table>
            <tr>{header}</tr>
            {body}
        </table>
        {link_foto}
    </div>
    """

# --- Layout responsive: affiancato su desktop, impilato su mobile ---

# --- Layout responsive: affiancato su desktop, impilato su mobile ---
col_map, col_info = st.columns([3, 2])

# ---- MAPPA (colonna sinistra) ----
with col_map:
    if selected_section == "TUTTI":
        m = fun_maps(df)
        st_folium(m, width=None, height=600,
                  returned_objects=[], use_container_width=True)
    else:
        res = fun_maps_dett(df, selected_section)
        if res is not None:
            m, nome_incrocio = res
            st.subheader(nome_incrocio)
            st_folium(m, width=None, height=600,
                      returned_objects=[], use_container_width=True)

# ---- PANNELLO DATI + PDF (colonna destra) ----
with col_info:
    if st.button("📄 Genera PDF", use_container_width=True):
        with st.spinner("Generazione PDF in corso…"):
            pdf_bytes = genera_pdf(df, selected_section)
            fname = (f"impianto_{selected_section}.pdf"
                     if selected_section != "TUTTI"
                     else "archivio_completo.pdf")
            pdf_download_button(pdf_bytes, fname)

    st.markdown(build_info_html(df, selected_section), unsafe_allow_html=True)

