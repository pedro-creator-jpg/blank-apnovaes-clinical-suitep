import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import math

# --- CONFIGURACIÓN DE NIVEL SUPERIOR ---
st.set_page_config(page_title="Novaes Clinical Intelligence B-Suite", layout="wide")

# --- ESTADO DE LA APLICACIÓN (BASE DE DATOS TEMPORAL) ---
# Nota: Para persistencia permanente en la nube, conectaríamos esto a SQL/Supabase más adelante.
if 'db_pacientes' not in st.session_state:
    st.session_state.db_pacientes = {}

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f1f5f9; border-radius: 5px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #1e40af !important; color: white !important; }
    div[data-testid="stMetricValue"] { color: #0f172a; font-size: 28px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER PRINCIPAL ---
st.title("🧬 Novaes Fetal & Metabolic Intelligence")
st.caption("Asesor de Investigaciones Clínicas y Gestión Perinatal | v4.0 Alpha")

# --- SISTEMA DE IDENTIFICACIÓN ---
with st.sidebar:
    st.header("🔍 Gestión de Paciente")
    paciente_id = st.text_input("ID o Nombre de la Paciente", placeholder="Ej: Maria_Perez_001")
    
    if paciente_id:
        if paciente_id not in st.session_state.db_pacientes:
            st.info("Nueva ficha técnica creada.")
            st.session_state.db_pacientes[paciente_id] = {
                'datos_maternos': {},
                'laboratorio': {'T1': {}, 'T2': {}, 'T3': {}},
                'biometrias': []
            }
        else:
            st.success(f"Ficha de {paciente_id} cargada.")

# --- CUERPO PRINCIPAL (TABS) ---
if paciente_id:
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Ficha Materna & Riesgo", 
        "🧪 Laboratorio Evolutivo", 
        "👶 Ecografía & Doppler", 
        "📈 Historial & Tendencias"
    ])

    # --- TAB 1: FICHA MATERNA & RIESGO ---
    with tab1:
        st.subheader("Evaluación de Factores de Riesgo Obstétrico")
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.session_state.db_pacientes[paciente_id]['datos_maternos']['edad'] = st.number_input("Edad Materna", 12, 55, 30)
            fum = st.date_input("FUM (Fecha Última Menstruación)", datetime.now() - timedelta(weeks=20))
            st.session_state.db_pacientes[paciente_id]['datos_maternos']['fum'] = fum
            
            # Antropometría e IMC
            talla = st.number_input("Talla (cm)", 100.0, 220.0, 165.0) / 100
            peso_m = st.number_input("Peso Actual (kg)", 30.0, 200.0, 70.0)
            imc = round(peso_m / (talla**2), 1)
            st.metric("IMC Calculado", f"{imc} kg/m²")
            
        with col_m2:
            st.subheader("Antecedentes (APP)")
            tabaquismo = st.checkbox("Hábito Tabáquico / Tóxicos")
            preeclampsia_prev = st.checkbox("Antecedente de Preeclampsia")
            diabetes_prev = st.checkbox("Antecedente Diabetes Gestacional")
            hta_cronica = st.checkbox("Hipertensión Crónica")
        
        # Lógica de Riesgo OMS/FMF (Simplificada para prototipo)
        st.divider()
        if imc > 30 or preeclampsia_prev or hta_cronica:
            st.error("🚨 **ALERTA DE RIESGO OBSTÉTRICO ALTO:** Se recomienda seguimiento estricto de TA y Doppler de Arterias Uterinas.")
        else:
            st.success("✅ Riesgo obstétrico basal dentro de la normalidad.")

    # --- TAB 2: LABORATORIO EVOLUTIVO ---
    with tab2:
        trimestre = st.radio("Seleccione Trimestre", ["1er Trimestre", "2do Trimestre", "3er Trimestre"], horizontal=True)
        t_key = "T1" if "1er" in trimestre else "T2" if "2do" in trimestre else "T3"
        
        st.subheader(f"Analítica del {trimestre}")
        col_l1, col_l2 = st.columns(2)
        
        with col_l1:
            hb = st.number_input("Hemoglobina (g/dL)", 5.0, 20.0, 12.0)
            glicemia = st.number_input("Glicemia Basal (mg/dL)", 40, 300, 85)
            st.session_state.db_pacientes[paciente_id]['laboratorio'][t_key]['Hb'] = hb
            st.session_state.db_pacientes[paciente_id]['laboratorio'][t_key]['Glicemia'] = glicemia
            
        with col_l2:
            creatinina = st.number_input("Creatinina (mg/dL)", 0.1, 2.0, 0.6)
            plaquetas = st.number_input("Plaquetas (uL)", 50000, 600000, 250000)
        
        # Validación de Rangos Dinámicos
        if t_key == "T1" and hb < 11.0: st.warning("Hb baja para 1er Trimestre (Anemia)")
        if t_key == "T2" and hb < 10.5: st.warning("Hb baja para 2do Trimestre (Hemodilución normal pero límite)")
        if glicemia > 92 and t_key == "T1": st.error("Posible Diabetes Gestacional (Criterios OMS)")

    # --- TAB 3: ECOGRAFÍA & DOPPLER ---
    with tab3:
        st.subheader("Ingreso de Biometría y Hemodinámica")
        col_e1, col_e2, col_e3 = st.columns(3)
        
        with col_e1:
            st.markdown("**Cabeza**")
            dbo = st.number_input("DBO (mm)", 0.0, 120.0, 0.0) # 0 para permitir opcionalidad
            cc = st.number_input("CC (mm)", 0.0, 450.0, 0.0)
            dfo = st.number_input("DFO (mm) [Opcional]", 0.0, 150.0, 0.0)
        
        with col_e2:
            st.markdown("**Cuerpo y Miembros**")
            ca = st.number_input("CA (mm)", 0.0, 500.0, 0.0)
            lf = st.number_input("LF (mm)", 0.0, 100.0, 0.0)
            ila = st.number_input("ILA (cm)", 0.0, 35.0, 12.0)
            
        with col_e3:
            st.markdown("**Doppler (IP)**")
            au = st.number_input("IP Art. Umbilical", 0.0, 3.0, 0.0)
            acm = st.number_input("IP Art. Cerebral Media", 0.0, 3.5, 0.0)
            dv = st.number_input("IP Ducto Venoso", 0.0, 2.0, 0.0)
        
        if st.button("💾 Guardar y Analizar"):
            # Lógica No-Excluyente para PFE (Hadlock IV)
            # Solo calcula si tiene los parámetros mínimos
            if ca > 0 and lf > 0:
                # Conversión a cm para fórmula
                db_cm = dbo/10; cc_cm = cc/10; ca_cm = ca/10; lf_cm = lf/10
                log_pfe = 1.3596 + (0.00061*db_cm*ca_cm) + (0.424*ca_cm) + (1.74*lf_cm) + (0.0064*cc_cm) - (0.00386*ca_cm*lf_cm)
                pfe_final = round(10**log_pfe, 1)
                
                # Calcular Semanas por Eco (Simplificado)
                eg_estimada = round((lf * 0.5) + 15, 1) # Estimación burda
                
                nueva_eco = {
                    "Fecha": datetime.now(),
                    "Semanas": eg_estimada,
                    "PFE": pfe_final,
                    "IP_AU": au,
                    "IP_ACM": acm,
                    "ICP": round(acm/au, 2) if au > 0 else 0
                }
                st.session_state.db_pacientes[paciente_id]['biometrias'].append(nueva_eco)
                st.success(f"Estudio guardado: PFE {pfe_final}g")
            else:
                st.error("Faltan parámetros críticos (CA y LF) para calcular el peso.")

    # --- TAB 4: HISTORIAL & INVESTIGACIÓN ---
    with tab4:
        st.subheader("Análisis Longitudinal")
        historial = st.session_state.db_pacientes[paciente_id]['biometrias']
        
        if historial:
            df = pd.DataFrame(historial)
            
            # Gráfico de Crecimiento
            fig = px.line(df, x="Semanas", y="PFE", markers=True, title="Curva Evolutiva de Peso Fetal")
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla para Investigaciones
            st.markdown("### Exportar Datos para Investigación")
            st.dataframe(df)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar CSV para Investigación", csv, f"investigacion_{paciente_id}.csv", "text/csv")
        else:
            st.info("No hay datos históricos para esta paciente.")

else:
    st.warning("👈 Por favor, ingrese un ID de paciente en la barra lateral para comenzar.")
