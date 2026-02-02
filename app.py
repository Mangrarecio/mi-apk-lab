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

# 2. ESTILO DE ALTO CONTRASTE Y LEGIBILIDAD
st.markdown("""
    <style>
    /* Fondo principal y color de texto */
    .stApp {
        background-color: #1a1c24; 
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Mejorar la lectura de los títulos */
    h1, h2, h3 {
        color: #00ff88 !important; /* Verde neón suave para títulos */
        font-weight: 700;
    }

    /* Estilo de las pestañas (Tabs) para que se vean claras */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #262730;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #3d3f4b;
        border-radius: 5px;
        color: #ffffff !important;
        font-weight: bold;
        border: 1px solid #555;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00ff88 !important;
        color: #000000 !important;
    }

    /* Botones más grandes y visibles */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #2ea043;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Panel lateral más claro */
    section[data-testid="stSidebar"] {
        background-color: #262730 !important;
        border-right: 2px solid #00ff88;
    }

    /* Editor de código con borde para no perderse */
    .ace_editor {
        border: 2px solid #00ff88;
        border-radius: 5px;
    }
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
        with st.spinner("Analizando..."):
            salida = os.path.join(tmp, "work")
            if decompilar_apk(ruta_apk, salida)[0]:
                st.session_state.carpeta_trabajo = salida
                st.success("✅ APK CARGADA")

# --- PANEL PRINCIPAL ---
if st.session_state.carpeta_trabajo:
    info = obtener_info_basica(st.session_state.carpeta_trabajo)
    st.warning(f"📦 APP: {info['package']} | VERSIÓN: {info['version']}")

    # PESTAÑAS CON TEXTO CLARO
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛡️ PRIVACIDAD", "🧠 PARCHES", "👥 CLONAR", "🎨 DISEÑO", "📝 EDITOR IDE"
    ])

    with tab1:
        st.subheader("ELIMINAR RASTREO")
        st.write("Quita publicidad y telemetría de la aplicación.")
        if st.button("🧹 LIMPIAR PUBLICIDAD"):
            exito, cant = eliminar_librerias_ads(st.session_state.carpeta_trabajo)
            st.success(f"¡Hecho! Se eliminaron {cant} elementos.")

    with tab2:
        st.subheader("MODIFICAR FUNCIONES")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📸 PERMITIR CAPTURAS"):
                parche_permitir_capturas(st.session_state.carpeta_trabajo)
                st.success("✅ Capturas habilitadas")
        with col2:
            if st.button("🛡️ BYPASS SEGURIDAD"):
                parche_bypass_root(st.session_state.carpeta_trabajo)
                st.success("✅ Seguridad modificada")

    with tab3:
        st.subheader("CREAR COPIA (CLON)")
        nuevo_id = st.text_input("Nuevo nombre de paquete:", value=info['package'] + ".clon")
        if st.button("🧬 CLONAR"):
            if clonar_app(st.session_state.carpeta_trabajo, nuevo_id):
                st.success("✅ ID Cambiado")
                st.rerun()

    with tab4:
        st.subheader("ESTÉTICA Y LENGUAJE")
        if st.button("🌍 TRADUCIR TODO AL ESPAÑOL"):
            traducir_textos_app(st.session_state.carpeta_trabajo)
            st.success("✅ Traducción lista")
        
        nuevo_ico = st.file_uploader("Subir icono PNG", type=["png"])
        if nuevo_ico and st.button("🎨 CAMBIAR ICONO"):
            cambiar_icono_app(st.session_state.carpeta_trabajo, nuevo_ico)
            st.success("✅ Icono actualizado")

    with tab5:
        st.subheader("📂 EXPLORADOR DE ARCHIVOS")
        lista = listar_archivos(st.session_state.carpeta_trabajo)
        
        # Buscador visible
        busqueda = st.text_input("🔍 BUSCAR ARCHIVO (ej: strings):", "")
        filtrados = [f for f in lista if busqueda.lower() in f.lower()]

        c_tree, c_editor = st.columns([1, 3])

        with c_tree:
            st.write("**ARCHIVOS:**")
            # Selección de archivo por lista clara
            archivo_sel = st.radio("Lista:", filtrados, label_visibility="collapsed")

        with c_editor:
            if archivo_sel:
                ruta_f = os.path.join(st.session_state.carpeta_trabajo, archivo_sel)
                st.code(f"Archivo actual: {archivo_sel}")
                
                try:
                    with open(ruta_f, "r", errors="ignore") as f:
                        code = f.read()
                    
                    # EDITOR CON TEMA CLARO PARA LEER MEJOR (Optional: "chrome", "tomorrow")
                    # Usamos "monokai" pero con fuente más grande
                    nuevo_code = st_ace(
                        value=code,
                        language="xml" if archivo_sel.endswith(".xml") else "java",
                        theme="monokai",
                        height=500,
                        font_size=16, 
                        key=f"ed_{archivo_sel}"
                    )
                    
                    if nuevo_code != code:
                        with open(ruta_f, "w", errors="ignore") as f:
                            f.write(nuevo_code)
                        st.toast("💾 GUARDADO")
                except:
                    st.error("No se puede leer este archivo.")

    st.divider()
    if st.button("📦 COMPILAR APK FINAL"):
        with st.spinner("Construyendo..."):
            nombre = "app_final.apk"
            if compilar_y_firmar(st.session_state.carpeta_trabajo, nombre)[0]:
                with open(nombre, "rb") as f:
                    st.download_button("📥 DESCARGAR APK MODIFICADA", f, file_name=nombre)
                st.balloons()
else:
    st.info("👋 BIENVENIDO. CARGA UNA APK EN LA IZQUIERDA PARA EMPEZAR.")