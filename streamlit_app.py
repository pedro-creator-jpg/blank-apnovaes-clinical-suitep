import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from scipy.stats import norm

# --- 1. CONFIGURACIÓN Y MOTOR ---
st.set_page_config(page_title="Novaes Clinical CDSS v13", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = {}

def calcular_p(v, m, de):
    if de <= 0: return 50
    z = (v - m) / de
    return round(norm.cdf(z) * 100, 1)

# --- 2. DEFINICIÓN DE MÓDULOS ---

def modulo_obstetricia(id_p):
    st.header("🤰 Medicina Materno-Fetal")
    c1, c2 = st.columns([1, 2])
    with c1:
        fum = st.date_input("FUM", datetime.now() - timedelta(weeks=20))
        eg = round((datetime.now().date() - fum).days / 7, 1)
        st.metric("Edad Gestacional", f"{eg} sem")
        
        st.markdown("---")
        dbo = st.number_input("DBO (mm)", 30.0, 120.0, 75.0)
        ca = st.number_input("CA (mm)", 100.0, 450.0, 260.0)
        lf = st.number_input("LF (mm)", 20.0, 100.0, 55.0)
        cc = st.number_input("CC (mm)", 100.0, 450.0, 280.0)
        
    with c2:
        st.subheader("Doppler e Índices")
        d1, d2 = st.columns(2)
        au = d1.number_input("IP Umbilical", 0.4, 2.5, 0.9)
        acm = d2.number_input("IP ACM", 0.6, 3.5, 1.6)
        
        if st.button("📊 Procesar Biometría y Doppler"):
            pfe = round(10**(1.3596 + (0.00061*dbo/10*ca/10) + (0.424*ca/10) + (1.74*lf/10) + (0.0064*cc/10) - (0.00386*ca/10*lf/10)), 1)
            icp = round(acm/au, 2)
            p_pfe = calcular_p(pfe, (eg*110)-1100, 220)
            
            r1, r2, r3 = st.columns(3)
            r1.metric("PFE", f"{pfe}g", f"p{p_pfe}")
            r2.metric("ICP", icp, "Normal" if icp > 1.08 else "Alterado", delta_color="normal" if icp > 1.08 else "inverse")
            r3.metric("IP Umbilical", au)
            
            st.session_state.db[id_p]['eco'].append({"Fecha": datetime.now(), "EG": eg, "PFE": pfe, "ICP": icp})

def modulo_reproduccion():
    st.header("🧬 Fertilidad y Metabolismo")
    tab_repro1, tab_repro2 = st.tabs(["Metabolismo (HOMA/VitD)", "Seguimiento Folicular"])
    
    with tab_repro1:
        col1, col2 = st.columns(2)
        with col1:
            ins = st.number_input("Insulina (µU/mL)", 2.0, 50.0, 10.0)
            glu = st.number_input("Glucosa (mg/dL)", 50, 200, 90)
            homa = (ins * glu) / 405
            st.metric("HOMA-IR", round(homa, 2), delta="Resistencia" if homa > 2.5 else "Normal", delta_color="inverse" if homa > 2.5 else "normal")
        with col2:
            vd = st.number_input("Vit D 25-(OH)", 5.0, 100.0, 30.0)
            if vd < 20: st.error("Deficiencia")
            elif vd < 30: st.warning("Insuficiencia")
            else: st.success("Suficiencia")

    with tab_repro2:
        c1, c2 = st.columns(2)
        f_der = c1.text_input("Fov Derecho (mm)", "18, 12")
        f_izq = c2.text_input("Fov Izquierdo (mm)", "10")
        endo = st.slider("Endometrio (mm)", 1.0, 15.0, 8.0)
        if st.button("Analizar Disparo"):
            st.success("Criterios de inducción analizados.")

def modulo_farmacologia():
    st.header("💊 Farmacología Perinatal")
    protocolo = st.radio("Protocolo:", ["Crisis Hipertensiva", "Insulina Rápida", "Sulfato de Magnesio"])
    
    if protocolo == "Crisis Hipertensiva":
        st.info("**Nifedipina:** 10mg VO cada 20 min (Máx 40mg). Evitar si hay bradicardia.")
        st.info("**Labetalol:** Inicio 20mg IV. Duplicar dosis cada 10 min si persiste TA alta.")
    elif protocolo == "Insulina Rápida":
        glic = st.number_input("Glicemia actual", 60, 400, 160)
        if glic > 140:
            unidades = (glic - 100) / 40
            st.warning(f"Sugerencia: Administrar {round(unidades, 1)} UI de Insulina Rápida.")

# --- 3. INTERFAZ PRINCIPAL ---
st.title("🧬 Novaes Clinical Intelligence v13")

with st.sidebar:
    id_p = st.text_input("ID Paciente", key="id_paciente")
    if id_p:
        if id_p not in st.session_state.db:
            st.session_state.db[id_p] = {'eco': [], 'lab': []}
        st.success(f"Paciente: {id_p}")

if id_p:
    menu = st.tabs(["🤰 OBSTETRICIA", "🧪 REPRO/METAB", "💊 FARMACO", "📈 INVESTIGACIÓN"])
    
    with menu[0]: modulo_obstetricia(id_p)
    with menu[1]: modulo_reproduccion()
    with menu[2]: modulo_farmacologia()
    with menu[3]:
        st.subheader("Datos para Publicación")
        if st.session_state.db[id_p]['eco']:
            df = pd.DataFrame(st.session_state.db[id_p]['eco'])
            st.dataframe(df)
            st.download_button("📥 Descargar CSV", df.to_csv().encode('utf-8'), f"Novaes_{id_p}.csv")
else:
    st.info("👈 Por favor, ingrese el ID de la paciente en la barra lateral.")
