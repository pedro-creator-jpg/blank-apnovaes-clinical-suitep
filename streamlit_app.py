import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURACIÓN MÉDICA ---
st.set_page_config(page_title="Novaes Clinical Suite v5", layout="wide")

# Inicializar Base de Datos en la sesión
if 'db' not in st.session_state:
    st.session_state.db = {}

st.title("🧬 Novaes Fetal & Metabolic Intelligence")
st.caption("Suite de Alta Complejidad para Medicina Materno-Fetal")

# --- BARRA LATERAL: GESTIÓN DE PACIENTES ---
with st.sidebar:
    st.header("👤 Paciente")
    id_paciente = st.text_input("ID / Nombre Completo", placeholder="Ej: Novaes_001")
    
    if id_paciente:
        if id_paciente not in st.session_state.db:
            st.session_state.db[id_paciente] = {
                'historial_materno': {},
                'historial_lab': [],
                'historial_eco': []
            }
        st.success(f"Archivo: {id_paciente}")

# --- LOGICA PRINCIPAL SI HAY PACIENTE ---
if id_paciente:
    t1, t2, t3, t4 = st.tabs(["📋 Ficha & Riesgo", "🧪 Laboratorio Detallado", "👶 Eco & Doppler", "📊 Evolución Clínica"])

    # --- TAB 1: FICHA MATERNA ---
    with t1:
        st.subheader("Historia Clínica y Antropometría")
        c1, c2 = st.columns(2)
        with c1:
            fum = st.date_input("Fecha de Última Menstruación (FUM)", datetime.now() - timedelta(weeks=20))
            fpp = fum + timedelta(days=280)
            eg_actual = round((datetime.now().date() - fum).days / 7, 1)
            
            st.metric("FPP (Regla de Naegele)", fpp.strftime("%d/%m/%Y"))
            st.metric("Edad Gestacional Actual", f"{eg_actual} semanas")
            
            peso = st.number_input("Peso Actual (kg)", 30.0, 200.0, 70.0)
            talla = st.number_input("Talla (cm)", 100.0, 220.0, 165.0) / 100
            imc = round(peso / (talla**2), 2)
            
            # Clasificación IMC
            if imc < 18.5: clas = "Bajo Peso"; color = "inverse"
            elif 18.5 <= imc < 25: clas = "Normal"; color = "normal"
            elif 25 <= imc < 30: clas = "Sobrepeso"; color = "off"
            else: clas = "Obesidad"; color = "off"
            st.metric("IMC", f"{imc} ({clas})")

        with c2:
            st.markdown("**Hábitos Tóxicos (Cantidad/Día)**")
            tabaco = st.number_input("Cigarrillos", 0, 40, 0)
            alcohol = st.selectbox("Consumo Alcohol", ["Nulo", "Ocasional", "Frecuente"])
            otras_sust = st.text_area("Otras sustancias / Comentarios adicionales")
            
            st.markdown("**Historia Obstétrica**")
            gestas = st.number_input("Gestas", 0, 20, 1)
            partos = st.number_input("Partos", 0, 20, 0)
            cesareas = st.number_input("Cesáreas", 0, 20, 0)
            antecedentes = st.text_area("Antecedentes de importancia (RCIU, Preeclampsia, etc.)")

    # --- TAB 2: LABORATORIO DETALLADO ---
    with t2:
        st.subheader("Ingreso de Analítica Periódica")
        with st.form("form_lab"):
            fecha_lab = st.date_input("Fecha del Análisis")
            l1, l2, l3 = st.columns(3)
            with l1:
                st.markdown("**Hemograma**")
                hb = st.number_input("Hb (g/dL)", 5.0, 18.0, 12.0)
                hcto = st.number_input("Hcto (%)", 15.0, 55.0, 36.0)
                plaquetas = st.number_input("Plaquetas", 50000, 600000, 250000)
            with l2:
                st.markdown("**Bioquímica & Renal**")
                glicemia = st.number_input("Glicemia (mg/dL)", 40, 300, 85)
                urea = st.number_input("Urea (mg/dL)", 5, 100, 25)
                ac_urico = st.number_input("Ácido Úrico (mg/dL)", 1.0, 12.0, 4.0)
                tgo = st.number_input("TGO (U/L)", 0, 500, 25)
                tgp = st.number_input("TGP (U/L)", 0, 500, 25)
            with l3:
                st.markdown("**Perfil Lipídico & Vits**")
                colest = st.number_input("Colesterol Total", 100, 400, 180)
                trigli = st.number_input("Triglicéridos", 50, 600, 150)
                vit_d = st.number_input("Vitamina D (ng/mL)", 5, 100, 30)
            
            if st.form_submit_button("💾 Guardar Laboratorio"):
                st.session_state.db[id_paciente]['historial_lab'].append({
                    "Fecha": fecha_lab, "Hb": hb, "Glicemia": glicemia, "AcUrico": ac_urico, "EG": eg_actual
                })
                st.success("Analítica guardada en el historial.")

    # --- TAB 3: ECOGRAFÍA & DOPPLER ---
    with t3:
        st.subheader("Evaluación Morfo-Fetal e Hemodinámica")
        with st.form("form_eco"):
            e1, e2, e3 = st.columns(3)
            with e1:
                st.markdown("**Biometría**")
                dbo = st.number_input("DBO", 0, 120, 75)
                dfo = st.number_input("DFO", 0, 150, 95)
                cc = st.number_input("CC", 0, 450, 280)
                ca = st.number_input("CA", 0, 450, 260)
                lf = st.number_input("LF", 0, 100, 55)
                lh = st.number_input("LH (Húmero)", 0, 100, 50)
            with e2:
                st.markdown("**Doppler**")
                ip_au = st.number_input("IP Art. Umbilical", 0.3, 3.0, 0.9)
                ip_acm = st.number_input("IP Art. Cerebral Media", 0.5, 3.5, 1.6)
                ip_ut_d = st.number_input("IP Uterina Derecha", 0.3, 3.0, 0.7)
                ip_ut_i = st.number_input("IP Uterina Izquierda", 0.3, 3.0, 0.7)
            with e3:
                st.markdown("**Cálculos Automáticos**")
                imau = round((ip_ut_d + ip_ut_i) / 2, 2)
                icp = round(ip_acm / ip_au, 2) if ip_au > 0 else 0
                st.write(f"**IMAU:** {imau}")
                st.write(f"**ICP:** {icp}")
            
            if st.form_submit_button("💾 Guardar Ecografía"):
                # Cálculo Hadlock simplificado
                pfe = (dbo + ca + lf) * 10 # Representación simbólica
                st.session_state.db[id_paciente]['historial_eco'].append({
                    "Fecha": datetime.now(), "EG": eg_actual, "PFE": pfe, "ICP": icp, "IMAU": imau
                })
                st.success("Datos ecográficos guardados.")

    # --- TAB 4: HISTORIAL & TENDENCIAS ---
    with t4:
        st.subheader(f"Evolución Clínica: {id_paciente}")
        
        hist_eco = st.session_state.db[id_paciente]['historial_eco']
        if hist_eco:
            df_eco = pd.DataFrame(hist_eco)
            fig_pfe = px.line(df_eco, x="EG", y="PFE", title="Curva de Crecimiento Fetal (PFE)", markers=True)
            st.plotly_chart(fig_pfe, use_container_width=True)
            
            fig_doppler = px.line(df_eco, x="EG", y=["ICP", "IMAU"], title="Tendencia Hemodinámica (ICP vs IMAU)", markers=True)
            st.plotly_chart(fig_doppler, use_container_width=True)
        else:
            st.info("No hay datos sucesivos para mostrar tendencias.")

else:
    st.warning("👈 Ingrese el ID de la paciente para activar la Suite.")r, ingrese un ID de paciente en la barra lateral para comenzar.")
