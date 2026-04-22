import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from scipy.stats import norm

# --- CONFIGURACIÓN DE LA SUITE NOVAES v10 ---
st.set_page_config(page_title="Novaes Clinical Suite", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = {}

# --- MOTOR DE PERCENTILES ---
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

st.title("🧬 Novaes Clinical Intelligence")
st.caption("Módulo Avanzado: Biometría, Doppler con Percentiles y Laboratorio")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Paciente")
    id_p = st.text_input("ID Paciente", placeholder="Ej: 1010")
    if id_p:
        if id_p not in st.session_state.db:
            st.session_state.db[id_p] = {'materno': {}, 'lab': [], 'eco': []}
        st.success(f"Expediente Activo: {id_p}")

# --- CONTENIDO PRINCIPAL ---
if id_p:
    pac = st.session_state.db[id_p]
    tab1, tab2, tab3, tab4 = st.tabs(["📋 FPP & MADRE", "🧪 LABORATORIO", "👶 ECO & DOPPLER", "📈 EVOLUCIÓN"])

    with tab1:
        st.subheader("Cronología Gestacional")
        c1, c2, c3 = st.columns(3)
        with c1:
            fum = st.date_input("FUM", datetime.now() - timedelta(weeks=20))
            fpp = fum + timedelta(days=280)
            eg = round((datetime.now().date() - fum).days / 7, 1)
            st.metric("FPP (Naegele)", fpp.strftime("%d/%m/%Y"))
            st.metric("Edad Gestacional", f"{eg} sem")
        with c2:
            peso = st.number_input("Peso (kg)", 40.0, 180.0, 70.0)
            talla = st.number_input("Talla (cm)", 140, 210, 165) / 100
            imc = round(peso/(talla**2), 2)
            st.metric("IMC", imc, delta="Normal" if imc < 25 else "Riesgo")
        with c3:
            st.markdown("**Riesgos**")
            tob = st.number_input("Cigarrillos", 0, 50, 0)
            alc = st.selectbox("Alcohol", ["No", "Sí"])

    with tab2:
        st.subheader("Perfil de Laboratorio Completo")
        with st.form("lab_form"):
            l1, l2, l3 = st.columns(3)
            with l1:
                hb = st.number_input("Hb", 8.0, 16.0, 12.0)
                glu = st.number_input("Glicemia", 60, 200, 85)
            with l2:
                tsh = st.number_input("TSH", 0.1, 10.0, 1.5)
                tgo = st.number_input("TGO", 5, 200, 25)
                tgp = st.number_input("TGP", 5, 200, 25)
            with l3:
                acur = st.number_input("Ácido Úrico", 2.0, 10.0, 4.0)
                vitd = st.number_input("Vitamina D", 5, 100, 30)
            if st.form_submit_button("💾 Guardar Lab"):
                pac['lab'].append({"Fecha": datetime.now(), "EG": eg, "Hb": hb, "TSH": tsh})
                st.success("Analítica guardada")

    with tab3:
        st.subheader("Biometría y Doppler con Percentiles")
        with st.form("eco_form"):
            e1, e2 = st.columns(2)
            with e1:
                st.markdown("**Biometría**")
                dbo = st.number_input("DBO", 30.0, 115.0, 75.0)
                ca = st.number_input("CA", 100.0, 450.0, 260.0)
                lf = st.number_input("LF", 20.0, 100.0, 55.0)
                cc = st.number_input("CC", 100.0, 450.0, 280.0)
            with e2:
                st.markdown("**Doppler**")
                au = st.number_input("IP Umbilical", 0.4, 2.5, 0.9)
                acm = st.number_input("IP ACM", 0.6, 3.5, 1.6)
            if st.form_submit_button("📊 Calcular Percentiles"):
                # Hadlock IV
                pfe = round(10**(1.3596 + (0.00061*dbo/10*ca/10) + (0.424*ca/10) + (1.74*lf/10) + (0.0064*cc/10) - (0.00386*ca/10*lf/10)), 1)
                p_pfe = calcular_percentil(pfe, (eg*110)-1100, 220)
                st.divider()
                st.metric("PFE", f"{pfe}g", f"p{p_pfe}", delta_color=color_estado(p_pfe))
                pac['eco'].append({"Fecha": datetime.now(), "EG": eg, "PFE": pfe, "p": p_pfe})
                st.success("Estudio guardado")

    with tab4:
        st.subheader("Tendencias")
        if pac['eco']:
            df = pd.DataFrame(pac['eco'])
            st.plotly_chart(px.line(df, x="EG", y="PFE", title="Crecimiento Fetal"), use_container_width=True)
            st.dataframe(df)
        else:
            st.info("No hay datos aún.")
else:
    st.info("👈 Ingrese ID de paciente.")
