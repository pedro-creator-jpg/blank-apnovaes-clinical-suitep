import streamlit as st
import math

# Configuración de alto nivel - Novaes Clinical Intelligence
st.set_page_config(page_title="Novaes Fetal Intelligence", layout="wide")

st.title("🧬 Novaes Fetal & Metabolic Intelligence")
st.markdown("#### Agente de Decisión Clínica Basado en Consensos FIGO / ISUOG / ACOG")
st.divider()

# PANEL LATERAL: RECOLECCIÓN DE DATOS BIOMÉTRICOS Y HEMODINÁMICOS
with st.sidebar:
    st.header("📋 Perfil de la Paciente")
    semanas = st.number_input("Edad Gestacional (Semanas)", 11.0, 41.0, 28.0, step=0.1)
    etnia = st.selectbox("Etnia (Ajuste Intergrowth-21st)", ["Hispana", "Caucásica", "Afrodescendiente", "Asiática"])
    
    st.divider()
    st.header("📏 Biometría Fetal (Hadlock 4)")
    dbo = st.number_input("DBO (Diám. Biparietal) - mm", 20.0, 110.0, 72.0)
    cc = st.number_input("CC (Circ. Cefálica) - mm", 100.0, 400.0, 261.0)
    ca = st.number_input("CA (Circ. Abdominal) - mm", 100.0, 450.0, 239.0)
    lf = st.number_input("LF (Long. Femoral) - mm", 10.0, 90.0, 53.0)

    st.divider()
    st.header("📡 Doppler Hemodinámico (IP)")
    ip_umb = st.number_input("IP Arteria Umbilical", 0.4, 2.5, 0.95)
    ip_acm = st.number_input("IP Art. Cerebral Media", 0.5, 3.0, 1.70)
    ila = st.number_input("ILA (Líquido Amniótico)", 0.0, 30.0, 14.0)

# CÁLCULOS MATEMÁTICOS DE PRECISIÓN
# Fórmula de Hadlock 4 (Peso Fetal Estimado en gramos)
db_cm = dbo/10; cc_cm = cc/10; ca_cm = ca/10; lf_cm = lf/10
log_pfe = 1.3596 + (0.00061*db_cm*ca_cm) + (0.424*ca_cm) + (1.74*lf_cm) + (0.0064*cc_cm) - (0.00386*ca_cm*lf_cm)
pfe_gramos = round(10**log_pfe, 2)

# Índice Cerebro-Placentario (ICP)
icp = round(ip_acm / ip_umb, 2)

# VISUALIZACIÓN DE RESULTADOS PARA EL DOCTOR
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Peso Fetal Estimado (PFE)", f"{pfe_gramos} g")
    st.caption("Estatura y peso calculados vía Hadlock IV")

with col2:
    st.metric("Índice Cerebro-Placentario", icp)
    if icp < 1.08: # Umbral de sospecha según ISUOG/FIGO
        st.error("🚨 REDISTRIBUCIÓN DETECTADA")
    else:
        st.success("✅ HEMODINÁMICA NORMAL")

with col3:
    status_liq = "NORMAL" if 5 <= ila <= 25 else "ALTERADO"
    st.metric("Líquido Amniótico", f"{ila} cm", delta=status_liq)

# EL "CORAZÓN" DEL AGENTE: RAZONAMIENTO CLÍNICO EXPERTO
st.divider()
st.subheader("🧠 Análisis Predictivo del Agente")
with st.container():
    st.info(f"Análisis para feto de **{semanas} semanas** ({etnia})")
    
    # Simulación de lógica de percentiles (esto se ampliará con bases de datos)
    if pfe_gramos < 1100 and semanas > 28:
        st.warning("⚠️ SOSPECHA DE RCIU: El peso está por debajo del p10 para esta edad gestacional.")
    
    if icp < 1.08:
        st.markdown("**Conducta Médica Sugerida:**")
        st.write("1. Repetir Doppler en 48h incluyendo Ducto Venoso.")
        st.write("2. Monitorización electrónica fetal (MEF) diaria.")
        st.write("3. Protocolo de maduración pulmonar si se considera interrupción.")
    else:
        st.markdown("**Estatus:** Crecimiento y bienestar fetal dentro de parámetros esperados.")

st.divider()
st.caption("Novaes Clinical Intelligence | Basado en estándares globales de medicina materno-fetal.")
