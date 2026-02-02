import streamlit as st
from streamlit_ace import st_ace
import os, tempfile
from utils import (
    decompilar_apk, compilar_y_firmar, listar_archivos, 
    obtener_info_basica, traducir_textos_app,
    cambiar_icono_app, clonar_app, parche_permitir_capturas, 
    parche_bypass_root, eliminar_librerias_ads
)

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="APK Lab Expert", layout="wide", page_icon="🛡️")

# 2. ESTILO DE ALTO CONTRASTE (Legibilidad Mejorada)
st.markdown("""
    <style>
    .stApp { background-color: #1a1c24; color: #ffffff; }
    h1, h2, h3 { color: #00ff88 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #262730; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #ffffff !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #00ff88 !important; color: #000000 !important; }
    .stButton>button { width: 100%; background-color: #2ea043; color: white; font-weight: bold; border-radius: 8px; }
    section[data-testid="stSidebar"] { background-color: #262730 !important; border-right: 2px solid #00ff88; }
    </style>
    """, unsafe_allow_html=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛡️ LABORATORIO APK EXPERT")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📂 ARCHIVO")
    archivo = st.file_uploader("Subir APK", type="apk")
    if archivo and st.button("▶️ INICIAR ANÁLISIS"):
        tmp = tempfile.mkdtemp()
        ruta_apk = os.path.join(tmp, "base.apk")
        with open(ruta_apk, "wb") as f: f.write(archivo.getbuffer())
        with st.spinner("Decompilando..."):
            salida = os.path.join(tmp, "work")
            if decompilar_apk(ruta_apk, salida)[0]:
                st.session_state.carpeta_trabajo = salida
                st.success("✅ APK CARGADA")

# --- PANEL PRINCIPAL ---
if st.session_state.carpeta_trabajo:
    info = obtener_info_basica(st.session_state.carpeta_trabajo)
    st.warning(f"📦 APP: {info['package']} | VERSIÓN: {info['version']}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛡️ PRIVACIDAD", "🧠 PARCHES", "👥 CLONAR", "🎨 DISEÑO", "📝 EDITOR IDE"
    ])

    # Pestañas de herramientas rápidas (Se mantienen igual)
    with tab1:
        st.subheader("LIMPIAR PUBLICIDAD")
        if st.button("🧹 EJECUTAR LIMPIEZA"):
            exito, cant = eliminar_librerias_ads(st.session_state.carpeta_trabajo)
            st.success(f"¡Hecho! Se eliminaron {cant} elementos.")

    with tab2:
        st.subheader("MODIFICAR FUNCIONES")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📸 PERMITIR CAPTURAS"):
                parche_permitir_capturas(st.session_state.carpeta_trabajo)
                st.success("✅ Hecho")
        with c2:
            if st.button("🛡️ BYPASS SEGURIDAD"):
                parche_bypass_root(st.session_state.carpeta_trabajo)
                st.success("✅ Hecho")

    with tab3:
        st.subheader("CLONAR")
        nuevo_id = st.text_input("Nuevo ID:", value=info['package'] + ".clon")
        if st.button("🧬 CLONAR"):
            if clonar_app(st.session_state.carpeta_trabajo, nuevo_id):
                st.success("✅ ID Cambiado")
                st.rerun()

    with tab4:
        st.subheader("ESTÉTICA")
        if st.button("🌍 TRADUCIR A ESPAÑOL"):
            traducir_textos_app(st.session_state.carpeta_trabajo)
            st.success("✅ Traducido")
        
        ico = st.file_uploader("Nuevo icono PNG", type=["png"])
        if ico and st.button("🎨 APLICAR ICONO"):
            cambiar_icono_app(st.session_state.carpeta_trabajo, ico)
            st.success("✅ Actualizado")

    # --- EL EDITOR REPARADO (SIN CUELGUES) ---
    with tab5:
        st.subheader("📂 EXPLORADOR DE PROYECTO")
        
        # Obtenemos la ruta actual (empezamos en la raíz)
        base = st.session_state.carpeta_trabajo
        
        col_nav, col_edit = st.columns([1, 2])

        with col_nav:
            # Filtro de carpetas para no saturar
            carpetas = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
            folder_sel = st.selectbox("1. Selecciona Carpeta:", ["Raíz"] + sorted(carpetas))
            
            ruta_actual = base if folder_sel == "Raíz" else os.path.join(base, folder_sel)
            
            # Listamos archivos de ESA carpeta solamente
            archivos = [f for f in os.listdir(ruta_actual) if os.path.isfile(os.path.join(ruta_actual, f))]
            
            # Buscador solo para esta carpeta
            busqueda = st.text_input("🔍 Buscar archivo aquí:", "")
            filtrados = [f for f in archivos if busqueda.lower() in f.lower()]
            
            archivo_sel = st.radio("2. Selecciona Archivo:", sorted(filtrados))

        with col_edit:
            if archivo_sel:
                ruta_f = os.path.join(ruta_actual, archivo_sel)
                st.code(f"📄 {archivo_sel}")
                
                try:
                    with open(ruta_f, "r", errors="ignore") as f:
                        code = f.read()
                    
                    nuevo_code = st_ace(
                        value=code,
                        language="xml" if archivo_sel.endswith(".xml") else "java",
                        theme="monokai",
                        height=500,
                        font_size=16,
                        key=f"editor_{folder_sel}_{archivo_sel}"
                    )
                    
                    if nuevo_code != code:
                        with open(ruta_f, "w", errors="ignore") as f:
                            f.write(nuevo_code)
                        st.toast("💾 GUARDADO")
                except:
                    st.error("Archivo binario (no editable)")

    st.divider()
    if st.button("📦 GENERAR APK FINAL"):
        with st.spinner("Compilando..."):
            nombre = "app_modificada.apk"
            if compilar_y_firmar(st.session_state.carpeta_trabajo, nombre)[0]:
                with open(nombre, "rb") as f:
                    st.download_button("📥 DESCARGAR APK", f, file_name=nombre)
                st.balloons()
else:
    st.info("👋 BIENVENIDO. CARGA UNA APK PARA EMPEZAR.")