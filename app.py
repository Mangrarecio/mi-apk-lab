import streamlit as st
from streamlit_ace import st_ace
import os, tempfile
from utils import (
    decompilar_apk, compilar_y_firmar, listar_archivos, 
    obtener_info_basica, traducir_textos_app,
    cambiar_icono_app, clonar_app, parche_permitir_capturas, 
    parche_bypass_root, eliminar_librerias_ads
)

# 1. MÁXIMA LEGIBILIDAD (Fondo Blanco, Texto Negro)
st.set_page_config(page_title="APK Expert", layout="wide")

st.markdown("""
    <style>
    /* Fondo blanco puro y texto negro para que no sufran tus ojos */
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: bold !important; }
    
    /* Pestañas grandes y claras */
    .stTabs [data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; padding: 10px 20px; }
    
    /* Botones verdes muy visibles */
    .stButton>button { 
        background-color: #008000 !important; 
        color: white !important; 
        border-radius: 10px; 
        height: 50px;
        font-size: 20px !important;
    }
    
    /* Editor de código con fondo crema (descansa la vista) */
    .ace_editor { border: 3px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛡️ LABORATORIO APK: MODO SEGURO")

# --- PANEL LATERAL ---
with st.sidebar:
    st.header("📂 ARCHIVO")
    archivo = st.file_uploader("Sube tu APK", type="apk")
    if archivo and st.button("▶️ ANALIZAR APK"):
        tmp = tempfile.mkdtemp()
        ruta_apk = os.path.join(tmp, "base.apk")
        with open(ruta_apk, "wb") as f: f.write(archivo.getbuffer())
        with st.spinner("Procesando..."):
            salida = os.path.join(tmp, "work")
            if decompilar_apk(ruta_apk, salida)[0]:
                st.session_state.carpeta_trabajo = salida
                st.success("✅ CARGADA")

# --- PANEL CENTRAL ---
if st.session_state.carpeta_trabajo:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛡️ PRIVACIDAD", "🧠 PARCHES", "👥 CLONAR", "🎨 DISEÑO", "📝 EDITOR"
    ])

    # Simplificamos las pestañas 1-4 para ahorrar memoria
    with tab1:
        if st.button("🧹 QUITAR ANUNCIOS"):
            eliminar_librerias_ads(st.session_state.carpeta_trabajo)
            st.success("Limpieza lista")

    with tab2:
        if st.button("📸 ACTIVAR CAPTURAS"):
            parche_permitir_capturas(st.session_state.carpeta_trabajo)
            st.success("Parche aplicado")

    with tab3:
        nuevo_id = st.text_input("Nuevo ID:", value="com.app.clon")
        if st.button("🧬 CLONAR"):
            clonar_app(st.session_state.carpeta_trabajo, nuevo_id)
            st.success("ID Cambiado")

    with tab4:
        if st.button("🌍 TRADUCIR A ESPAÑOL"):
            traducir_textos_app(st.session_state.carpeta_trabajo)
            st.success("Traducido")

    # --- EL EDITOR "ANTIFREEEZE" (NUNCA SE CUELGA) ---
    with tab5:
        st.subheader("📝 EDITOR DE ARCHIVOS")
        base = st.session_state.carpeta_trabajo
        
        # En lugar de mostrar carpetas, usamos un buscador de texto directo
        # Esto evita cargar miles de elementos visuales
        search = st.text_input("🔍 Escribe el nombre del archivo (ej: strings o manifest):", "strings.xml")
        
        # Buscamos solo los primeros 50 resultados para no colapsar el navegador
        todos = listar_archivos(base)
        coincidencias = [f for f in todos if search.lower() in f.lower()][:50]
        
        if coincidencias:
            # Usamos selectbox en lugar de radio para máxima velocidad
            archivo_sel = st.selectbox("📂 Selecciona el archivo para editar:", coincidencias)
            
            if archivo_sel:
                ruta_f = os.path.join(base, archivo_sel)
                try:
                    with open(ruta_f, "r", errors="ignore") as f:
                        code = f.read()
                    
                    st.write(f"✍️ Editando: `{archivo_sel}`")
                    
                    # Editor Ace con tema claro para leer mejor
                    nuevo_code = st_ace(
                        value=code,
                        language="xml" if ".xml" in archivo_sel else "java",
                        theme="chrome", # Tema blanco profesional
                        height=400,
                        font_size=18, # Letra muy grande
                        key=f"ed_{archivo_sel}"
                    )
                    
                    if nuevo_code != code:
                        with open(ruta_f, "w", errors="ignore") as f:
                            f.write(nuevo_code)
                        st.toast("✅ GUARDADO")
                except:
                    st.error("No se puede abrir este archivo.")
        else:
            st.warning("No se encontraron archivos con ese nombre.")

    st.divider()
    if st.button("📦 GENERAR APK FINAL"):
        with st.spinner("Compilando..."):
            nombre = "app_final.apk"
            if compilar_y_firmar(st.session_state.carpeta_trabajo, nombre)[0]:
                with open(nombre, "rb") as f:
                    st.download_button("📥 DESCARGAR APK", f, file_name=nombre)
                st.balloons()
else:
    st.info("Carga una APK a la izquierda para ver las opciones.")