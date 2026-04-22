import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from scipy.stats import norm

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Novaes Research Suite", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = {}

# Motor de Percentiles (Basado en medias gestacionales)
def calcular_p(v, m, de):
    if de <= 0: return 50
    z = (v - m) / de
    p = round(norm.cdf(z) * 100, 1)
    return p

st.title("🧬 Novaes Clinical Intelligence v11")
st.caption("Investigación Materno-Fetal: Biometría, Doppler de Precisión y Laboratorio")

# --- GESTIÓN DE PACIENTE ---
with st.sidebar:
    st.header("👤 Paciente")
    id_p = st.text_input("ID / Nombre", placeholder="ID de seguimiento...")
    if id_p:
        if id_p not in st.session_state.db:
            st.session_state.db[id_p] = {'lab': [], 'eco': []}
        st.success(f"Expediente: {id_p}")

if id_p:
    p = st.session_state.db[id_p]
    t1, t2, t3, t4 = st.tabs(["📋 FPP", "🧪 LAB COMPLETO", "👶 DOPPLER & PERCENTILES", "📊 EVOLUCIÓN"])

    with t1:
        st.subheader("Datos Maternos")
        c1, c2 = st.columns(2)
        with c1:
            fum = st.date_input("FUM", datetime.now() - timedelta(weeks=20))
            fpp = fum + timedelta(days=280)
            eg = round((datetime.now().date() - fum).days / 7, 1)
            st.metric("FPP (Naegele)", fpp.strftime("%d/%m/%Y"))
            st.metric("Edad Gestacional", f"{eg} sem")
        with c2:
            peso = st.number_input("Peso (kg)", 40.0, 150.0, 70.0)
            talla = st.number_input("Talla (cm)", 140, 210, 165) / 100
            st.metric("IMC", round(peso/(talla**2), 2))

    with t2:
        st.subheader("Análisis de Laboratorio")
        with st.form("lab_f"):
            l1, l2, l3 = st.columns(3)
            with l1:
                st.markdown("**Hematología/Metabólico**")
                hb = st.number_input("Hb", 8.0, 16.0, 12.0); glu = st.number_input("Glicemia", 60, 250, 85)
                acur = st.number_input("Ác. Úrico", 1.0, 10.0, 4.0)
            with l2:
                st.markdown("**Tiroides/Hígado**")
                tsh = st.number_input("TSH", 0.1, 8.0, 1.5); tgo = st.number_input("TGO", 5, 200, 25)
                tgp = st.number_input("TGP", 5, 200, 25)
            with l3:
                st.markdown("**Vitaminas/Otros**")
                vitd = st.number_input("Vit D", 5, 100, 30); col = st.number_input("Colest.", 100, 400, 190)
                tri = st.number_input("Triglicéridos", 50, 600, 150)
            if st.form_submit_button("💾 Guardar Lab"):
                p['lab'].append({"Fecha": datetime.now(), "EG": eg, "Hb": hb, "TSH": tsh, "Glu": glu})
                st.success("Laboratorio guardado")

    with t3:
        st.subheader("Evaluación Doppler y Percentiles")
        with st.form("eco_f"):
            e1, e2 = st.columns(2)
            with e1:
                st.markdown("**Biometría (mm)**")
                dbo = st.number_input("DBO", 30.0, 115.0, 75.0); cc = st.number_input("CC", 100.0, 450.0, 280.0)
                ca = st.number_input("CA", 100.0, 450.0, 260.0); lf = st.number_input("LF", 20.0, 95.0, 55.0)
            with e2:
                st.markdown("**IP Doppler**")
                au = st.number_input("IP Umbilical", 0.4, 2.5, 0.9)
                acm = st.number_input("IP ACM", 0.6, 3.5, 1.6)
                ut = st.number_input("IP Medio Uterinas", 0.3, 3.0, 0.7)
            
            if st.form_submit_button("📊 Procesar Biometría"):
                # Hadlock IV y Percentiles
                pfe = round(10**(1.3596 + (0.00061*dbo/10*ca/10) + (0.424*ca/10) + (1.74*lf/10) + (0.0064*cc/10) - (0.00386*ca/10*lf/10)), 1)
                icp = round(acm/au, 2)
                p_pfe = calcular_p(pfe, (eg*110)-1100, 220)
                p_au = calcular_p(au, 1.1 - (eg*0.01), 0.12)
                p_acm = calcular_p(acm, 2.3 - (eg*0.02), 0.18)
                p_icp = calcular_p(icp, 2.2 - (eg*0.02), 0.22)
                
                st.divider()
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("PFE", f"{pfe}g", f"p{p_pfe}")
                r2.metric("IP Umbilical", au, f"p{p_au}", delta_color="inverse" if p_au > 95 else "normal")
                r3.metric("IP ACM", acm, f"p{p_acm}")
                r4.metric("ICP", icp, f"p{p_icp}", delta_color="normal" if icp > 1.08 else "inverse")
                
                p['eco'].append({"Fecha": datetime.now(), "EG": eg, "PFE": pfe, "pPFE": p_pfe, "ICP": icp, "pICP": p_icp, "IMAU": ut})
                st.success("Estudio añadido")

    with t4:
        st.subheader("Análisis Longitudinal")
        if p['eco']:
            df = pd.DataFrame(p['eco'])
            st.plotly_chart(px.line(df, x="EG", y="PFE", title="Crecimiento Fetal (g)", markers=True))
            st.plotly_chart(px.line(df, x="EG", y=["ICP", "IMAU"], title="Evolución Doppler", markers=True))
            st.dataframe(df)
            st.download_button("📥 Exportar para Publicación (CSV)", df.to_csv().encode('utf-8'), f"Novaes_{id_p}.csv")
else:
    st.info("👈 Identifique a la paciente para comenzar.")
