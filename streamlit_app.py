import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from scipy.stats import norm

# --- CONFIGURACIÓN DE LA SUITE NOVAES ---
st.set_page_config(page_title="Novaes Clinical Suite v10", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = {}

# --- MOTOR DE PERCENTILES CLÍNICOS ---
def calcular_percentil(valor, media, de):
    if de <= 0: return 50
    z = (valor - media) / de
    return round(norm.cdf(z) * 100, 1)

def color_estado(p, invertido=False):
    if not invertido:
        if p < 10 or p > 90: return "inverse"
        return "normal"
    else:
        if p > 95: return "inverse"
        return "normal"

st.title("🧬 Novaes Clinical Intelligence v10")
st.caption("Módulo de Investigación Materno-Fetal: Biometría, Doppler y Laboratorio")

with st.sidebar:
    st.header("🔍 Identificación")
    id_p = st.text_input("ID Paciente", placeholder="Nueva o Seguimiento...")
    if id_p:
        if id_p not in st.session_state.db:
            st.session_state.db[id_p] = {'materno': {}, 'lab': [], 'eco': []}
        st.success(f"Expediente: {id_p}")

if id_p:
    pac = st.session_state.db[id_p]
    tab1, tab2, tab3, tab4 = st.tabs(["📋 FICHA & FPP", "🧪 LAB INTEGRAL", "👶 DOPPLER & PERCENTILES", "📈 TENDENCIAS"])

    with tab1:
        st.subheader("Datos Maternos y Cronología")
        col1, col2, col3 = st.columns(3)
        with col1:
            fum = st.date_input("FUM", datetime.now() - timedelta(weeks=20))
            fpp = fum + timedelta(days=280)
            eg = round((datetime.now().date() - fum).days / 7, 1)
            st.metric("FPP (Naegele)", fpp.strftime("%d/%m/%Y"))
            st.metric("Edad Gestacional", f"{eg} sem")
        with col2:
            peso = st.number_input("Peso Actual (kg)", 40.0, 180.0, 70.0)
            talla = st.number_input("Talla (cm)", 140, 210, 165) / 100
            imc = round(peso/(talla**2), 2)
            st.metric("IMC", imc, delta="Normal" if imc < 25 else "Riesgo", delta_color="normal" if imc < 25 else "inverse")
        with col3:
            st.markdown("**Hábitos Tóxicos**")
            tob = st.number_input("Cigarrillos/Día", 0, 50, 0)
            alc = st.selectbox("Alcohol", ["No", "Ocasional", "Riesgo"])

    with tab2:
        st.subheader("Laboratorio con Rangos Normales")
        with st.form("lab_v10"):
            l1, l2, l3 = st.columns(3)
            with l1:
                st.markdown("**Metabólico**")
                hb = st.number_input("Hb (g/dL)", 8.0, 16.0, 12.0)
                glu = st.number_input("Glicemia", 60, 250, 85)
                acur = st.number_input("Ácido Úrico", 2.0, 10.0, 4.0)
            with l2:
                st.markdown("**Tiroideo/Hepático**")
                tsh = st.number_input("TSH", 0.1, 10.0, 1.5)
                t4l = st.number_input("T4 Libre", 0.5, 2.5, 1.2)
                tgo = st.number_input("TGO", 5, 300, 25)
                tgp = st.number_input("TGP", 5, 300, 25)
            with l3:
                st.markdown("**Serología/Inmuno**")
                torch = st.selectbox("TORCH", ["Negativo", "IgG+", "Infección Activa"])
                vitd = st.number_input("Vitamina D", 5, 100, 35)
                ets = st.text_input("ETS/Otras", "No reactivas")
            if st.form_submit_button("💾 Guardar Análisis Sucesivo"):
                pac['lab'].append({"Fecha": datetime.now(), "EG": eg, "Hb": hb, "TSH": tsh, "Glu": glu, "TGO": tgo})
                st.success("✅ Datos de laboratorio integrados.")

    with tab3:
        st.subheader("Evaluación Fetal de Precisión")
        with st.form("eco_v10"):
            e1, e2 = st.columns(2)
            with e1:
                st.markdown("**Biometría**")
                dbo = st.number_input("DBO", 30, 120, 75); cc = st.number_input("CC", 100, 450, 280)
                ca = st.number_input("CA", 100, 450, 260); lf = st.number_input("LF", 20, 100, 55)
            with e2:
                st.markdown("**Doppler**")
                au = st.number_input("IP Arteria Umbilical", 0.4, 2.5, 0.9)
                acm = st.number_input("IP ACM", 0.6, 3.5, 1.6)
                ut = st.number_input("IP Medio Uterinas", 0.3, 3.0, 0.7)
            if st.form_submit_button("📊 Calcular Percentiles y Guardar"):
                pfe = round(10**(1.3596 + (0.00061*dbo/10*ca/10) + (0.424*ca/10) + (1.74*lf/10) + (0.0064*cc/10) - (0.00386*ca/10*lf/10)), 1)
                icp = round(acm/au, 2)
                p_pfe = calcular_percentil(pfe, (eg*110)-1100, 220)
                p_au = calcular_percentil(au, 1.1 - (eg*0.01), 0.12)
                p_acm = calcular_percentil(acm, 2.3 - (eg*0.02), 0.18)
                p_icp = calcular_percentil(icp, 2.2 - (eg*0.02), 0.22)
                st.divider()
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("PFE", f"{pfe}g", f"p{p_pfe}", delta_color=color_estado(p_pfe))
                r2.metric("IP Umbilical", au, f"p{p_au}", delta_color=color_estado(p_au, True))
                r3.metric("IP ACM", acm, f"p{p_acm}", delta_color=color_estado(p_acm))
                r4.metric("ICP", icp, f"p{p_icp}", delta_color=color_estado(p_icp))
                pac['eco'].append({"Fecha": datetime.now(), "EG": eg, "PFE": pfe, "pPFE": p_pfe, "ICP": icp, "pICP": p_icp, "IMAU": ut})
                st.success("✅ Registro ecográfico añadido.")

    with tab4:
        st.subheader("Análisis Longitudinal para Publicación")
        if pac['eco']:
            df = pd.DataFrame(pac['eco'])
            st.plotly_chart(px.line(df, x="EG", y="PFE", title="Crecimiento Fetal", markers=True))
            st.plotly_chart(px.line(df, x="EG", y=["ICP", "IMAU"], title="Evolución Hemodinámica", markers=True))
            st.dataframe(df)
            st.download_button("📥 Descargar CSV", df.to_csv().encode('utf-8'), f"Novaes_{id_p}.csv")
else:
    st.info("Identifique a la paciente en la barra lateral para activar la suite.")
