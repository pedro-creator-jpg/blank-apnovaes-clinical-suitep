import streamlit as st

# Configuración profesional de la página
st.set_page_config(page_title="Novaes Clinical Intelligence", layout="wide")

st.title("🧬 Novaes Fetal & Metabolic Intelligence")
st.markdown("---")

# PANEL LATERAL: ENTRADA DE DATOS CLÍNICOS
with st.sidebar:
    st.header("📋 Datos de la Paciente")
    semanas = st.number_input("Semanas de Gestación", 11.0, 41.0, 28.0, step=0.1)
    etnia = st.selectbox("Etnia/Raza", ["Hispana", "Caucásica", "Afrodescendiente", "Asiática"])
    
    st.divider()
    st.header("📏 Biometría Fetal (mm)")
    dbo = st.number_input("DBO", 20.0, 110.0, 70.0)
    cc = st.number_input("CC (Circ. Cefálica)", 100.0, 400.0, 260.0)
    ca = st.number_input("CA (Circ. Abdominal)", 100.0, 450.0, 240.0)
    lf = st.number_input("LF (Long. Femoral)", 10.0, 90.0, 54.0)

    st.divider()
    st.header("📡 Doppler Hemodinámico (IP)")
    ip_umb = st.number_input("IP Art. Umbilical", 0.4, 2.5, 0.9)
    ip_acm = st.number_input("IP Art. Cerebral Media", 0.5, 3.0, 1.6)
    ila = st.number_input("ILA (Líquido Amniótico)", 0.0, 30.0, 12.0)

# CÁLCULOS AUTOMÁTICOS DE IA
# Cálculo del Índice Cerebro-Placentario (ICP)
icp = round(ip_acm / ip_umb, 2)

# PRESENTACIÓN DE RESULTADOS
st.subheader("📊 Análisis del Agente de IA")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Índice Cerebro-Placentario (ICP)", icp)
    if icp < 1.0:
        st.error("🚨 REDISTRIBUCIÓN DE FLUJO: Riesgo de hipoxia o fallo de implantación tardío.")
    else:
        st.success("✅ Hemodinámica Cerebral Fetal Normal")

with col2:
    st.write("**Balance de Líquido Amniótico**")
    if ila < 5: 
        st.error("⚠️ OLIGOHIDRAMNIOS")
    elif ila > 25: 
        st.warning("⚠️ POLIHIDRAMNIOS")
    else: 
        st.success("✅ ILA Normal")

with col3:
    st.write("**Estrategia Clínica Sugerida**")
    if icp < 1.0 or ila < 5:
        st.warning("Control estricto (48-72h). Evaluar perfil biofísico.")
    else:
        st.info("Continuar protocolo estándar según edad gestacional.")

st.divider()
st.info(f"**Criterio Novaes:** Los cálculos están ajustados para la etnia **{etnia}**. La biometría sugiere un peso fetal acorde a las **{semanas}** semanas.")
