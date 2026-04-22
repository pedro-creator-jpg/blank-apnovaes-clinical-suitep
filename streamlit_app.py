import streamlit as st
import pandas as pd

# Configuración de página con estilo médico profesional
st.set_page_config(page_title="Novaes Fetal Intelligence", layout="wide", initial_sidebar_state="expanded")

# Estética Personalizada (CSS) para mejorar visual y menús
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 Novaes Fetal & Metabolic Intelligence")
st.caption("Protocolos de Medicina Materno-Fetal Basados en Evidencia (FIGO/ISUOG)")

# --- BARRA LATERAL DINÁMICA ---
with st.sidebar:
    st.header("📋 Entrada de Datos")
    
    # Edad Gestacional con Slider para evitar que el cuadro se ponga rojo constantemente
    semanas = st.slider("Edad Gestacional (Semanas)", 20.0, 41.0, 32.0, step=0.1)
    
    st.divider()
    etnia = st.selectbox("Etnia (Ajuste Poblacional)", 
                        ["Hispana / Latina", "Caucásica", "Afrodescendiente", "Asiática"],
                        help="Ajusta los percentiles según Intergrowth-21st")
    
    st.divider()
    st.subheader("📏 Biometría (mm)")
    dbo = st.number_input("DBO", 40.0, 110.0, 80.0)
    cc = st.number_input("Circ. Cefálica (CC)", 150.0, 400.0, 300.0)
    ca = st.number_input("Circ. Abdominal (CA)", 150.0, 450.0, 280.0)
    lf = st.number_input("Long. Femoral (LF)", 30.0, 90.0, 62.0)

    st.divider()
    st.subheader("📡 Doppler IP")
    ip_umb = st.number_input("IP Art. Umbilical", 0.4, 2.5, 0.90)
    ip_acm = st.number_input("IP Art. Cerebral Media", 0.5, 3.0, 1.60)

# --- LÓGICA DE CÁLCULO (HADLOCK 4) ---
# Conversión a cm para la fórmula
ca_cm = ca/10; lf_cm = lf/10; cc_cm = cc/10; db_cm = dbo/10
log_pfe = 1.3596 + (0.00061*db_cm*ca_cm) + (0.424*ca_cm) + (1.74*lf_cm) + (0.0064*cc_cm) - (0.00386*ca_cm*lf_cm)
pfe = round(10**log_pfe, 1)

# Índice Cerebro-Placentario (ICP)
icp = round(ip_acm / ip_umb, 2)

# --- INTERFAZ DINÁMICA DE RESULTADOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Peso Fetal Estimado", f"{pfe} g")
    # Lógica de interpretación dinámica de peso vs edad gestacional
    p_esperado = (semanas - 20) * 130 # Estimación burda para dinamismo
    if pfe < (p_esperado * 0.8):
        st.error("⚠️ PFE BAJO PARA EG")
    else:
        st.success("✅ PESO ADECUADO")

with col2:
    st.metric("ICP (Doppler)", icp)
    if icp < 1.08:
        st.error("🚨 REDISTRIBUCIÓN")
    else:
        st.success("✅ NORMAL")

with col3:
    # Relación CC/CA (Indicador de asimetría)
    rel_cc_ca = round(cc/ca, 2)
    st.metric("Relación CC/CA", rel_cc_ca)

# --- EL ANALIZADOR INTELIGENTE (EL CORAZÓN DEL AGENTE) ---
st.divider()
st.subheader("🧠 Razonamiento Clínico Automático")

# Aquí es donde el Agente cambia según la Edad Gestacional
diagnostico = ""
conducta = ""

if semanas < 34 and icp < 1.08:
    diagnostico = "RCIU Precoz con signos de redistribución hemodinámica."
    conducta = "Considerar maduración pulmonar y vigilancia estricta con Doppler de Ducto Venoso."
elif semanas >= 37 and pfe < 2500:
    diagnostico = "Feto pequeño para la edad gestacional (PEG) a término."
    conducta = "Finalización del embarazo según condiciones cervicales (Protocolo FIGO)."
elif icp < 1.08:
    diagnostico = "Alteración hemodinámica (ICP < 1.08)."
    conducta = "Seguimiento Doppler en 48-72 horas."
else:
    diagnostico = "Crecimiento y bienestar fetal dentro de límites normales."
    conducta = "Control prenatal habitual."

st.info(f"**Diagnóstico Presuntivo:** {diagnostico}")
st.warning(f"**Sugerencia de Manejo:** {conducta}")

# Gráfico visual de referencia (Simulado)
st.divider()
st.caption("Nota: Este agente es una herramienta de apoyo. El juicio clínico del Dr. Novaes prevalece.")
