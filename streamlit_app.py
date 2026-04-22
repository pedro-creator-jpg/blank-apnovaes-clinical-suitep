import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- CONFIGURACIÓN DE APARIENCIA PROFESIONAL ---
st.set_page_config(page_title="Novaes Clinical Intelligence", layout="wide", initial_sidebar_state="expanded")

# CSS Personalizado para estética moderna
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #1e40af; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e2e8f0; border-radius: 5px 5px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #1e40af !important; color: white !important; }
    .status-normal { color: #10b981; font-weight: bold; }
    .status-warning { color: #f59e0b; font-weight: bold; }
    .status-alert { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS EN MEMORIA ---
if 'db' not in st.session_state:
    st.session_state.db = {}

# --- FUNCIONES DE EVALUACIÓN CLÍNICA ---
def evaluar_resultado(nombre, valor, eg=None):
    """Retorna (Estado, Color, Mensaje)"""
    if nombre == "Hb":
        umbral = 11.0 if (eg < 13 or eg > 28) else 10.5
        return ("Normal", "green", "") if valor >= umbral else ("Anemia", "red", f"Baja p/ EG (<{umbral})")
    if nombre == "Glicemia":
        return ("Normal", "green", "") if valor < 92 else ("Alerta", "red", "Riesgo Diabetes (>92)")
    if nombre == "TSH":
        return ("Normal", "green", "") if 0.1 <= valor <= 3.0 else ("Alterada", "orange", "Revisar perfil")
    if nombre == "TGO" or nombre == "TGP":
        return ("Normal", "green", "") if valor < 40 else ("Elevada", "red", "Riesgo HELLP/Hepático")
    if nombre == "PFE_Pct":
        if valor < 10: return ("RCIU/PEG", "red", "Bajo Percentil (<p10)")
        if valor > 90: return ("Macrosomía", "orange", "Alto Percentil (>p90)")
        return ("Adecuado", "green", "p10 - p90")
    return ("Registrado", "blue", "")

# --- ESTRUCTURA PRINCIPAL ---
st.title("🧬 Novaes Fetal & Metabolic Intelligence")
st.caption("Advanced Maternal-Fetal Research & Clinical Suite | Dr. Novaes Edition")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2785/2785482.png", width=80) # Icono médico
    id_paciente = st.text_input("🆔 ID Paciente", placeholder="Buscar o Crear...")
    if id_paciente:
        if id_paciente not in st.session_state.db:
            st.session_state.db[id_paciente] = {'materno': {}, 'lab': [], 'eco': []}
            st.info("🆕 Nueva Ficha")
        else: st.success("📁 Expediente Cargado")

if id_paciente:
    paciente = st.session_state.db[id_paciente]
    tab1, tab2, tab3, tab4 = st.tabs(["📋 HISTORIA", "🧪 LABORATORIO", "👶 ECOGRAFÍA", "📈 EVOLUCIÓN"])

    # --- TAB 1: FICHA MATERNA ---
    with tab1:
        st.subheader("Perfil de Riesgo Materno")
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            fum = st.date_input("FUM", datetime.now() - timedelta(weeks=20))
            eg_actual = round((datetime.now().date() - fum).days / 7, 1)
            st.metric("Edad Gestacional", f"{eg_actual} sem")
        with c2:
            peso = st.number_input("Peso (kg)", 40.0, 180.0, 70.0)
            talla = st.number_input("Talla (cm)", 140, 210, 165) / 100
            imc = round(peso / (talla**2), 2)
            est, col, msg = ("Normal", "green", "") if imc < 25 else ("Sobrepeso", "orange", "") if imc < 30 else ("Obesidad", "red", "")
            st.metric("IMC", f"{imc}", delta=est, delta_color=col)
        with c3:
            st.markdown("**Hábitos Tóxicos**")
            tabaco = st.number_input("Tabaco (Cig/día)", 0, 50, 0)
            alcohol = st.selectbox("Alcohol", ["Nulo", "Ocasional", "Riesgo"])
        
        st.text_area("Antecedentes Obstétricos Relevantes", placeholder="Paridad, Preeclampsia previa, Cirugías...")

    # --- TAB 2: LABORATORIO ---
    with tab2:
        st.subheader("Analítica Sucesiva y Cribado")
        with st.form("form_lab"):
            l1, l2, l3, l4 = st.columns(4)
            with l1:
                hb = st.number_input("Hb (g/dL)", 7.0, 16.0, 12.0)
                plaquetas = st.number_input("Plaquetas", 50000, 500000, 220000)
            with l2:
                glu = st.number_input("Glicemia", 50, 250, 85)
                acur = st.number_input("Ácido Úrico", 1.0, 12.0, 4.0)
            with l3:
                tsh = st.number_input("TSH", 0.05, 10.0, 1.5)
                t4l = st.number_input("T4 Libre", 0.5, 2.5, 1.2)
            with l4:
                tgo = st.number_input("TGO", 0, 300, 25)
                tgp = st.number_input("TGP", 0, 300, 25)
            
            if st.form_submit_button("➕ Registrar y Evaluar"):
                res_hb = evaluar_resultado("Hb", hb, eg_actual)
                res_glu = evaluar_resultado("Glicemia", glu)
                paciente['lab'].append({"Fecha": datetime.now(), "EG": eg_actual, "Hb": hb, "Hb_St": res_hb, "Glu": glu, "Glu_St": res_glu})
                st.toast("Laboratorio Guardado", icon="✅")

    # --- TAB 3: ECOGRAFÍA & PERCENTILES ---
    with tab3:
        st.subheader("Biometría y Hemodinámica Avanzada")
        with st.form("form_eco"):
            e1, e2, e3 = st.columns(3)
            with e1:
                dbo = st.number_input("DBO (mm)", 30, 110, 75); cc = st.number_input("CC (mm)", 100, 400, 280)
                ca = st.number_input("CA (mm)", 100, 400, 260); lf = st.number_input("LF (mm)", 20, 90, 55)
            with e2:
                ip_au = st.number_input("IP Umbilical", 0.4, 2.5, 0.9); ip_acm = st.number_input("IP ACM", 0.6, 3.5, 1.6)
                ip_ut = st.number_input("IP Medio Uterinas", 0.3, 3.0, 0.7)
            with e3:
                # Lógica Hadlock y Percentil Prototipo
                pfe = round(10**(1.3596 + (0.00061*dbo/10*ca/10) + (0.424*ca/10) + (1.74*lf/10) + (0.0064*cc/10) - (0.00386*ca/10*lf/10)), 1)
                pct_pfe = round(min(99, max(1, (pfe / (eg_actual * 120)) * 50)), 1) # Simulación de percentil
                icp = round(ip_acm / ip_au, 2)
                
                est_p, col_p, msg_p = evaluar_resultado("PFE_Pct", pct_pfe)
                st.metric("PFE (Hadlock IV)", f"{pfe} g", delta=f"p{pct_pfe}", delta_color="normal")
                st.markdown(f"Estado: <span class='status-{col_p}'>{est_p}</span>", unsafe_allow_html=True)
                st.metric("ICP", icp, delta="Normal" if icp > 1.08 else "Redistribución", delta_color="normal" if icp > 1.08 else "inverse")

            if st.form_submit_button("➕ Guardar Estudio"):
                paciente['eco'].append({"EG": eg_actual, "PFE": pfe, "p": pct_pfe, "ICP": icp, "IMAU": ip_ut})
                st.success("Eco Guardada")

    # --- TAB 4: EVOLUCIÓN (INVESTIGACIÓN) ---
    with tab4:
        st.subheader("Análisis de Tendencias")
        if paciente['eco']:
            df = pd.DataFrame(paciente['eco'])
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                fig_p = px.line(df, x="EG", y="PFE", title="Curva de Peso (g)", markers=True, template="plotly_white")
                st.plotly_chart(fig_p, use_container_width=True)
            with c_g2:
                fig_d = px.line(df, x="EG", y=["ICP", "IMAU"], title="Evolución Doppler", markers=True, template="plotly_white")
                st.plotly_chart(fig_d, use_container_width=True)
            
            st.markdown("### 📋 Tabla de Exportación Científica")
            st.write(df)
            st.download_button("📥 Descargar Datos", df.to_csv().encode('utf-8'), f"Novaes_{id_paciente}.csv")
else:
    st.info("👋 Bienvenida/o, Doctor. Ingrese el ID de una paciente para comenzar la evaluación.")
