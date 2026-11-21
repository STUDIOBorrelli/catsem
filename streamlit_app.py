import io
import base64
import html as _html
from datetime import datetime

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle, Image as RLImage)

try:
    from staticmap import StaticMap, CircleMarker
    _STATICMAP_OK = True
except Exception:
    _STATICMAP_OK = False


# ============================================================
# CONFIGURAZIONE
# ============================================================
st.set_page_config(page_title="Archivio Semafori Bari", layout="wide")

Aggiornamento = '2.02'

# Colonne 0-based del nuovo Excel:
# A=ID.IMP B=NOME_IMP C=LAT_X_E D=LONG_Y_N E=ID.ELEM F=TIPOLOGIA
# G=FOTO 1 H=FOTO 2 I=SOSTEGNO J=LANT_BASSE K=LANT_ALTE L=LANT_ PEDO
# M=PRESENZA_L N=PRESENZA_P O=PRESENZA_1 P=PRESENZA_2 Q=PRESENZA_D
# R=CENTRALINA S=MODELLO T=CENTRALIZZ U=USCITE V=FUNZIONAME W=TIPO_SENSO
# X=TELECAMERE Y=SERIALE Z=DISPALYZTL
COL_ID_IMP    = 0
COL_NOME_IMP  = 1
COL_LON_X     = 2   # LAT_X_E  -> longitudine
COL_LAT_Y     = 3   # LONG_Y_N -> latitudine
COL_ID_ELEM   = 4
COL_TIPOLOGIA = 5

# Ordine preferenziale per il pannello "Informazioni impianto"
ORDINE_INFO = [
    "ID.IMP", "NOME_IMP", "CENTRALINA", "MODELLO", "SERIALE",
    "DISPALYZTL", "CENTRALIZZ", "USCITE", "FUNZIONAME", "TIPO_SENSO",
    "TELECAMERE",
]

# Colonne mostrate nella tabella "Dettaglio elementi"
COLS_DETTAGLIO = [
    "ID.ELEM", "TIPOLOGIA", "SOSTEGNO",
    "LANT_BASSE", "LANT_ALTE", "LANT_ PEDO",
    "PRESENZA_L", "PRESENZA_P", "PRESENZA_1", "PRESENZA_2", "PRESENZA_D",
]


# ============================================================
# UTILITY
# ============================================================
def _esc_pdf(v):
    if pd.isna(v):
        return ""
    s = str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;"))


def _esc_html(v):
    if pd.isna(v):
        return ""
    return _html.escape(str(v))


def _riga_centralina(df_sel):
    """Ritorna la riga della centralina (o la prima riga se manca)."""
    mask = df_sel[df_sel.columns[COL_TIPOLOGIA]].astype(str).str.upper() == "CENTRALINA"
    if mask.any():
        return df_sel[mask].iloc[0]
    return df_sel.iloc[0]


def _info_centralina(riga_rif, df_columns):
    """Tutti i campi valorizzati della centralina, con ordine preferenziale."""
    # 1) prima le colonne dell'ordine preferenziale (se valorizzate)
    out = []
    usate = set()
    for col in ORDINE_INFO:
        if col in df_columns:
            val = riga_rif[col]
            if pd.isna(val):
                continue
            sval = str(val).strip()
            if sval == "" or sval.lower() == "false":
                continue
            out.append((col, sval))
            usate.add(col)
    # 2) poi tutte le altre colonne valorizzate
    for col in df_columns:
        if col in usate:
            continue
        val = riga_rif[col]
        if pd.isna(val):
            continue
        sval = str(val).strip()
        if sval == "" or sval.lower() == "false":
            continue
        out.append((str(col), sval))
    return out


# ============================================================
# DATI
# ============================================================
@st.cache_data
def fun_df():
    return pd.read_excel('ARCHIVIO_2.00.xlsx')


def fun_num_totali(df):
    return df.shape[0]


# ============================================================
# MAPPA STATICA PER PDF
# ============================================================
def _mappa_png_bytes(df_sel, lat_col, lon_col, zoom=18, size=(800, 500)):
    if not _STATICMAP_OK:
        return None
    lats = pd.to_numeric(df_sel.iloc[:, lat_col], errors='coerce')
    lons = pd.to_numeric(df_sel.iloc[:, lon_col], errors='coerce')
    mask = lats.notna() & lons.notna()
    if not mask.any():
        return None
    clat = float(lats[mask].mean())
    clon = float(lons[mask].mean())
    m = StaticMap(size[0], size[1],
                  url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
    m.add_marker(CircleMarker((clon, clat), 'blue', 14))
    for la, lo in zip(lats[mask], lons[mask]):
        m.add_marker(CircleMarker((float(lo), float(la)), 'red', 8))
    try:
        img = m.render(zoom=zoom)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    except Exception:
        return None


# ============================================================
# PDF
# ============================================================
def genera_pdf(df, selected_section):
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
                              alignment=TA_CENTER,
                              textColor=colors.HexColor("#333333"))
    st_h2 = ParagraphStyle("h2", parent=styles["Heading2"],
                           textColor=colors.HexColor("#444444"),
                           spaceBefore=8)
    st_norm = styles["Normal"]
    st_small = ParagraphStyle("s", parent=styles["Normal"],
                              fontSize=7.5, leading=9)

    story = []

    # --- Intestazione ---
    story.append(Paragraph("CITTÀ DI BARI", st_title))
    story.append(Paragraph("Archivio impianti semaforici", st_h2))
    story.append(Paragraph(
        f"Versione archivio: {Aggiornamento} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}", st_norm))
    story.append(Spacer(1, 4*mm))

    # ============ MAPPA ============
    if selected_section == "TUTTI":
        png = _mappa_png_bytes(df, COL_LAT_Y, COL_LON_X, zoom=11)
        titolo_mappa = "Mappa generale archivio"
    else:
        df_sel_mappa = df[df[df.columns[COL_ID_IMP]] == selected_section].copy()
        png = _mappa_png_bytes(df_sel_mappa, COL_LAT_Y, COL_LON_X, zoom=19)
        titolo_mappa = "Mappa impianto"

    if png:
        story.append(Paragraph(titolo_mappa, st_h2))
        try:
            img = RLImage(io.BytesIO(png), width=170*mm, height=110*mm)
            story.append(img)
        except Exception:
            story.append(Paragraph("[Mappa non disponibile]", st_norm))
        story.append(Spacer(1, 4*mm))
    else:
        story.append(Paragraph("[Mappa non disponibile]", st_norm))
        story.append(Spacer(1, 4*mm))

    # ============ CONTENUTO ============
    if selected_section == "TUTTI":
        story.append(Paragraph("Riepilogo generale archivio", st_h2))
        tipi = df[df.columns[COL_TIPOLOGIA]].astype(str).value_counts()
        dati = [["Tipologia", "N."]] + [[t, str(n)] for t, n in tipi.items()]
        t = Table(dati, colWidths=[120*mm, 30*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ]))
        story.append(t)
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(
            f"<b>Totale impianti:</b> {df[df.columns[COL_ID_IMP]].nunique()} "
            f"&nbsp;&nbsp; <b>Totale elementi:</b> {len(df)}", st_norm))
    else:
        df_sel = df[df[df.columns[COL_ID_IMP]] == selected_section].copy()
        nome = str(df_sel.iloc[0, COL_NOME_IMP])
        story.append(Paragraph(f"Impianto: {_esc_pdf(nome)}", st_h2))

        # --- TUTTI i dati della centralina (incl. SERIALE/DISPALYZTL/TELECAMERE) ---
        riga_rif = _riga_centralina(df_sel)
        info = _info_centralina(riga_rif, df.columns)
        if info:
            story.append(Paragraph("Informazioni impianto (centralina)", st_h2))
            data = [[_esc_pdf(k), _esc_pdf(v)] for k, v in info]
            t = Table(data, colWidths=[50*mm, 100*mm])
            t.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t)

        # Conteggio per tipologia
        story.append(Paragraph("Elementi presenti", st_h2))
        tipi = df_sel[df_sel.columns[COL_TIPOLOGIA]].astype(str).value_counts()
        dati = [["Tipologia", "N."]] + [[t, str(n)] for t, n in tipi.items()]
        t2 = Table(dati, colWidths=[120*mm, 30*mm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ]))
        story.append(t2)

        # Dettaglio elementi
        story.append(Paragraph("Dettaglio elementi", st_h2))
        cols_dett = [c for c in COLS_DETTAGLIO if c in df_sel.columns]
        df_dett = df_sel[cols_dett].copy().replace({False: "", True: "✔"})

        header = [Paragraph(f"<b>{_esc_pdf(c)}</b>", st_small)
                  for c in df_dett.columns]
        body = []
        for _, r in df_dett.iterrows():
            body.append([Paragraph(_esc_pdf(v), st_small) for v in r.values])
        ncol = len(header)
        larghezze = [180*mm / ncol] * ncol
        t3 = Table([header] + body, colWidths=larghezze, repeatRows=1)
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d8d8d8")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        story.append(t3)

        # Link foto
        if "FOTO 1" in df_sel.columns:
            foto = df_sel["FOTO 1"].dropna()
            if not foto.empty and str(foto.iloc[0]).startswith("http"):
                story.append(Spacer(1, 4*mm))
                story.append(Paragraph(
                    f'<a href="{_esc_pdf(foto.iloc[0])}" color="blue">'
                    f'Foto 1 - Google Maps</a>', st_norm))

    doc.build(story)
    return buf.getvalue()


def pdf_download_button(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
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


# ============================================================
# MAPPE FOLIUM
# ============================================================
def fun_maps(df):
    df_imp = df.drop_duplicates(subset=[df.columns[COL_ID_IMP]]).copy()
    lats = pd.to_numeric(df_imp.iloc[:, COL_LAT_Y], errors='coerce')
    lons = pd.to_numeric(df_imp.iloc[:, COL_LON_X], errors='coerce')
    mask = lats.notna() & lons.notna()
    center = ([lats[mask].mean(), lons[mask].mean()]
              if mask.any() else [41.1092, 16.8539])
    m = folium.Map(location=center, zoom_start=12)
    for i in range(len(df_imp)):
        if not mask.iloc[i]:
            continue
        lat = float(lats.iloc[i]); lon = float(lons.iloc[i])
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
        lat = float(lats.iloc[i]); lon = float(lons.iloc[i])
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


# ============================================================
# PANNELLO HTML (a video)
# ============================================================
def build_info_html(df, selected_section):
    if selected_section == "TUTTI":
        tipi = df[df.columns[COL_TIPOLOGIA]].astype(str).value_counts()
        rows = "".join(
            f"<tr><td>{_esc_html(t)}</td>"
            f"<td style='text-align:right'>{n}</td></tr>"
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

    df_sel = df[df[df.columns[COL_ID_IMP]] == selected_section].copy()
    if df_sel.empty:
        return "<div class='info-frame'>Nessun dato.</div>"

    # Info centralina (stessa funzione del PDF)
    riga_rif = _riga_centralina(df_sel)
    info = _info_centralina(riga_rif, df.columns)
    info_rows = "".join(
        f"<tr><td><b>{_esc_html(k)}</b></td><td>{_esc_html(v)}</td></tr>"
        for k, v in info
    )

    # Conteggio per tipologia
    tipi = df_sel[df_sel.columns[COL_TIPOLOGIA]].astype(str).value_counts()
    tipi_rows = "".join(
        f"<tr><td>{_esc_html(t)}</td>"
        f"<td style='text-align:right'>{n}</td></tr>"
        for t, n in tipi.items()
    )

    # Dettaglio elementi
    cols_dett = [c for c in COLS_DETTAGLIO if c in df_sel.columns]
    df_dett = df_sel[cols_dett].copy().replace({False: "", True: "✔"})

    header = "".join(f"<th>{_esc_html(c)}</th>" for c in df_dett.columns)
    body = ""
    for _, r in df_dett.iterrows():
        body += "<tr>" + "".join(
            f"<td>{_esc_html(v)}</td>" for v in r.values
        ) + "</tr>"

    # Link foto 1 (Google Maps) e foto 2 (file locale)
    link_foto = ""
    if "FOTO 1" in df_sel.columns:
        foto1 = df_sel["FOTO 1"].dropna()
        if not foto1.empty and str(foto1.iloc[0]).startswith("http"):
            url = _html.escape(str(foto1.iloc[0]), quote=True)
            link_foto += (f'<h4>Foto 1 - Google Maps</h4>'
                          f'<a href="{url}" target="_blank">📷 Apri</a>')
    if "FOTO 2" in df_sel.columns:
        foto2 = df_sel["FOTO 2"].dropna()
        if not foto2.empty:
            link_foto += (f'<h4>Foto 2 - Archivio locale</h4>'
                          f'<code>{_esc_html(foto2.iloc[0])}</code>')

    return f"""
    <div class="info-frame">
        <h4>Informazioni impianto (centralina)</h4>
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


# ============================================================
# APP
# ============================================================
df = fun_df()

# --- Header ---
c1, c2, c3 = st.columns(3)
with c1:
    st.caption('Elem. Analizzati:')
    st.code(fun_num_totali(df))
with c2:
    st.write("")
    st.markdown("<h3 style='text-align: center; color: grey;'>CITTÀ DI BARI</h3>",
                unsafe_allow_html=True)
with c3:
    st.caption('Versione Archivio:')
    st.code(Aggiornamento)

# --- Selettore impianto ---
id_disponibili = sorted(df[df.columns[COL_ID_IMP]].dropna().unique().tolist())
opzioni = ["TUTTI"] + id_disponibili
selected_section = st.selectbox("Seleziona impianto:", opzioni, index=0)

# --- CSS ---
st.markdown("""
<style>
.info-frame {
    border: 1px solid #d0d0d0; border-radius: 8px;
    padding: 12px 14px; background-color: #fafafa;
    max-height: 600px; overflow-y: auto; overflow-x: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    scrollbar-width: thin;
    scrollbar-color: #bbb #f0f0f0;
}
.info-frame::-webkit-scrollbar { width: 8px; }
.info-frame::-webkit-scrollbar-track { background: #f0f0f0; border-radius: 4px; }
.info-frame::-webkit-scrollbar-thumb { background: #bbb; border-radius: 4px; }
.info-frame::-webkit-scrollbar-thumb:hover { background: #999; }
.info-frame h4 { margin: 10px 0 4px 0; font-size: 1rem; color: #333; }
.info-frame h4:first-child { margin-top: 0; }
.info-frame table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.info-frame table th { text-align: left; background: #eee; padding: 4px 6px; }
.info-frame table td { padding: 3px 6px; border-bottom: 1px solid #eaeaea; }
@media (max-width: 768px) { .info-frame { max-height: 400px; } }
</style>
""", unsafe_allow_html=True)

# --- Layout ---
col_map, col_info = st.columns([3, 2])

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

with col_info:
    if st.button("📄 Genera PDF", use_container_width=True):
        with st.spinner("Generazione PDF in corso…"):
            pdf_bytes = genera_pdf(df, selected_section)
            fname = (f"impianto_{selected_section}.pdf"
                     if selected_section != "TUTTI"
                     else "archivio_completo.pdf")
            pdf_download_button(pdf_bytes, fname)

    st.markdown(build_info_html(df, selected_section), unsafe_allow_html=True)
