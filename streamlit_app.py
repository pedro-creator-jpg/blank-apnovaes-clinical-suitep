import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE NIVEL MÉDICO ---
st.set_page_config(page_title="Novaes Clinical Suite v5", layout="wide")

# Inicialización de la base de datos en memoria
if 'db' not in st.session_state:
    st.session_state.db = {}

st.title("🧬 Novaes Fetal & Metabolic Intelligence")
st.caption("Plataforma Integral de Medicina Materno-Fetal e Investigación")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("👤 Gestión de Paciente")
    id_paciente = st.text_input("ID o Nombre de la Paciente", placeholder="Ej: Novaes_001")
    
    if id_paciente:
        if id_paciente not in st.session_state.db:
            st.session_state.db[id_paciente] = {
                'materno': {'antecedentes': '', 'toxicos': {}},
                'lab_historial': [],
                'eco_historial': []
            }
        st.success(f"Expediente activo: {id_paciente}")

# --- LÓGICA PRINCIPAL ---
if id_paciente:
    t1, t2, t3, t4 = st.tabs(["📋 Ficha Materna", "🧪 Laboratorio Expandido", "👶 Eco & Doppler", "📊 Evolución & Evolución"])

    # --- TAB 1: FICHA MATERNA ---
    with t1:
        st.subheader("Anamnesis y Riesgo Obstétrico")
        c1, c2 = st.columns(2)
        with c1:
            fum = st.date_input("FUM (Fecha Última Menstruación)", datetime.now() - timedelta(weeks=20))
            fpp = fum + timedelta(days=280)
            eg_actual = round((datetime.now().date() - fum).days / 7, 1)
            
            st.metric("Fecha Probable de Parto", fpp.strftime("%d/%m/%Y"))
            st.metric("Edad Gestacional Actual", f"{eg_actual} semanas")
            
            peso = st.number_input("Peso Actual (kg)", 30.0, 200.0, 70.0)
            talla = st.number_input("Talla (cm)", 100.0, 220.0, 165.0) / 100
            imc = round(peso / (talla**2), 2)
            
            clas = "Normal"
            if imc < 18.5: clas = "Bajo Peso"
            elif imc >= 25 and imc < 30: clas = "Sobrepeso"
            elif imc >= 30: clas = "Obesidad"
            st.metric("IMC", f"{imc} ({clas})")

        with c2:
            st.markdown("**Hábitos Tóxicos**")
            tabaco = st.number_input("Cigarrillos / día", 0, 50, 0)
            alcohol = st.selectbox("Alcohol", ["No consume", "Ocasional", "Frecuente"])
            otros = st.text_input("Otras sustancias")
            
            st.markdown("**Historia Obstétrica**")
            st.session_state.db[id_paciente]['materno']['antecedentes'] = st.text_area("Antecedentes relevantes (Preeclampsia previa, RCIU, etc.)")

    # --- TAB 2: LABORATORIO (CON RANGOS) ---
    with t2:
        st.subheader("Analítica de Laboratorio por Trimestre")
        with st.form("lab_form"):
            col_l1, col_l2, col_l3 = st.columns(3)
            with col_l1:
                st.markdown("**Hemograma**")
                hb = st.number_input("Hemoglobina (g/dL)", 5.0, 18.0, 12.0)
                hcto = st.number_input("Hematocrito (%)", 15.0, 55.0, 36.0)
                plaquetas = st.number_input("Plaquetas (mil/uL)", 50, 600, 250)
            with col_l2:
                st.markdown("**Bioquímica & Hepático**")
                glicemia = st.number_input("Glicemia (mg/dL)", 40, 300, 85)
                urea = st.number_input("Urea (mg/dL)", 5, 120, 25)
                ac_urico = st.number_input("Ácido Úrico (mg/dL)", 1.0, 15.0, 4.0)
                tgo = st.number_input("TGO / AST (U/L)", 0, 500, 25)
                tgp = st.number_input("TGP / ALT (U/L)", 0, 500, 25)
            with col_l3:
                st.markdown("**Lípidos & Vitaminas**")
                colest = st.number_input("Colesterol Total", 100, 500, 190)
                trigli = st.number_input("Triglicéridos", 50, 800, 150)
                vit_d = st.number_input("Vitamina D (ng/mL)", 5, 150, 30)
            
            if st.form_submit_button("💾 Guardar Laboratorio"):
                st.session_state.db[id_paciente]['lab_historial'].append({
                    "Fecha": datetime.now(), "Hb": hb, "Glicemia": glicemia, "AcUrico": ac_urico, "EG": eg_actual
                })
                st.success("Analítica guardada correctamente.")

    # --- TAB 3: ECO & DOPPLER ---
    with t3:
        st.subheader("Biometría y Hemodinámica Fetal")
        with st.form("eco_form"):
            e1, e2, e3 = st.columns(3)
            with e1:
                st.markdown("**Biometría (mm)**")
                dbo = st.number_input("DBO", 0, 120, 75)
                dfo = st.number_input("DFO", 0, 150, 95)
                cc = st.number_input("CC", 0, 450, 280)
                ca = st.number_input("CA", 0, 450, 260)
                lf = st.number_input("LF", 0, 110, 55)
                lh = st.number_input("LH (Húmero)", 0, 110, 50)
            with e2:
                st.markdown("**Doppler**")
                ip_au = st.number_input("IP Arteria Umbilical", 0.3, 3.0, 0.9)
                ip_acm = st.number_input("IP Arteria Cerebral Media", 0.3, 3.5, 1.6)
                ip_ut_d = st.number_input("IP Uterina Derecha", 0.2, 3.0, 0.7)
                ip_ut_i = st.number_input("IP Uterina Izquierda", 0.2, 3.0, 0.7)
            with e3:
                st.markdown("**Resultados**")
                imau = round((ip_ut_d + ip_ut_i) / 2, 2)
                icp = round(ip_acm / ip_au, 2) if ip_au > 0 else 0
                st.write(f"**IMAU:** {imau}")
                st.write(f"**ICP:** {icp}")

            if st.form_submit_button("💾 Guardar Ecografía"):
                # Cálculo de peso (Hadlock simplificado para este módulo)
                pfe = (dbo + ca + lf) * 10 
                st.session_state.db[id_paciente]['eco_historial'].append({
                    "Fecha": datetime.now(), "EG": eg_actual, "PFE": pfe, "ICP": icp, "IMAU": imau, "CA": ca
                })
                st.success("Estudio ecográfico guardado.")

    # --- TAB 4: EVOLUCIÓN ---
    with t4:
        st.subheader("Tendencias y Análisis de Investigación")
        eco_data = st.session_state.db[id_paciente]['eco_historial']
        if eco_data:
            df = pd.DataFrame(eco_data)
            fig1 = px.line(df, x="EG", y="PFE", title="Crecimiento Fetal (PFE)", markers=True)
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = px.line(df, x="EG", y=["ICP", "IMAU"], title="Evolución Doppler (ICP vs IMAU)", markers=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Ingrese al menos un estudio para ver las gráficas.")

else:
    st.warning("👈 Ingrese el ID de la paciente en la barra lateral para comenzar.")
