import streamlit as st
from streamlit_ace import st_ace
import os, tempfile
from utils import decompilar_apk, compilar_y_firmar, obtener_info_basica

# CONFIGURACIÓN DE ALTO RENDIMIENTO
st.set_page_config(page_title="APK Studio Pro", layout="wide")

# ESTILO DE MÁXIMA LEGIBILIDAD (Fondo Blanco, Texto Negro)
st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #28a745 !important; color: white !important; height: 3em; width: 100%; }
    .stTab { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛠️ APK LABORATORY PRO")

# --- PANEL IZQUIERDO (CARGA) ---
with st.sidebar:
    st.header("📂 ARCHIVO")
    archivo = st.file_uploader("Sube tu APK", type="apk")
    if archivo and st.button("🚀 DECOMPILAR AHORA"):
        tmp = tempfile.mkdtemp()
        ruta = os.path.join(tmp, "base.apk")
        with open(ruta, "wb") as f: f.write(archivo.getbuffer())
        salida = os.path.join(tmp, "src")
        with st.spinner("Desmontando APK..."):
            ok, _ = decompilar_apk(ruta, salida)
            if ok:
                st.session_state.carpeta_trabajo = salida
                st.success("✅ PROYECTO LISTO")

# --- PANEL DERECHO (IDE PROFESIONAL) ---
if st.session_state.carpeta_trabajo:
    tab_tools, tab_editor = st.tabs(["🧰 HERRAMIENTAS", "💻 EDITOR DE CÓDIGO"])

    with tab_tools:
        st.subheader("Acciones Rápidas")
        if st.button("📦 COMPILAR Y GENERAR APK FINAL"):
            with st.spinner("Construyendo..."):
                compilar_y_firmar(st.session_state.carpeta_trabajo, "modificada.apk")
                st.balloons()

    with tab_editor:
        st.subheader("Explorador de Archivos")
        
        # CATEGORÍAS TIPO ANDROID STUDIO
        cat = st.selectbox("Módulo:", ["res", "smali", "manifest", "assets", "otros"])
        
        # BUSCADOR DINÁMICO (Esto evita que se cuelgue)
        filtro = st.text_input("🔍 Escribe nombre del archivo (ej: strings):", "")
        
        lista_archivos = []
        for raiz, dirs, ficheros in os.walk(st.session_state.carpeta_trabajo):
            if cat == "manifest" and "AndroidManifest.xml" in ficheros:
                lista_archivos.append("AndroidManifest.xml")
                break
            if cat in raiz:
                for f in ficheros:
                    if filtro.lower() in f.lower():
                        lista_archivos.append(os.path.relpath(os.path.join(raiz, f), st.session_state.carpeta_trabajo))
        
        # Solo mostramos los primeros 50 para que el navegador vuele
        archivo_sel = st.selectbox("Selecciona para editar:", sorted(lista_archivos)[:50])

        if archivo_sel:
            ruta_f = os.path.join(st.session_state.carpeta_trabajo, archivo_sel)
            st.code(f"Editando: {archivo_sel}")
            
            try:
                with open(ruta_f, "r", errors="ignore") as f:
                    contenido = f.read()
                
                # Editor profesional con letra grande (font_size=18)
                nuevo_code = st_ace(
                    value=contenido,
                    language="xml" if ".xml" in archivo_sel else "java",
                    theme="chrome", # Fondo claro para mejor lectura
                    height=500,
                    font_size=18,
                    key=f"ed_{archivo_sel}"
                )
                
                if nuevo_code != contenido:
                    with open(ruta_f, "w") as f: f.write(nuevo_code)
                    st.toast("✅ GUARDADO")
            except:
                st.error("Archivo no editable.")
else:
    st.info("Carga una APK en el panel de la izquierda para desplegar el IDE.")