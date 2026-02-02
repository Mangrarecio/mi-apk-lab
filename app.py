import streamlit as st
from streamlit_ace import st_ace
import os, tempfile
from utils import (
    decompilar_apk, compilar_y_firmar, listar_archivos, 
    obtener_info_basica, traducir_textos_app,
    cambiar_icono_app, clonar_app, parche_permitir_capturas, 
    parche_bypass_root, eliminar_librerias_ads
)

# 1. Configuración base
st.set_page_config(page_title="APK Lab Expert", layout="wide", page_icon="🛡️")

# 2. Estilo visual para que todo quepa
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #161b22;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛡️ APK Lab: Edición Profesional")

# 3. Barra lateral para subir archivos
with st.sidebar:
    st.header("📂 Entrada")
    archivo = st.file_uploader("Sube tu APK", type="apk")
    if archivo and st.button("🚀 Iniciar Análisis"):
        tmp = tempfile.mkdtemp()
        ruta = os.path.join(tmp, "base.apk")
        with open(ruta, "wb") as f: f.write(archivo.getbuffer())
        with st.spinner("Decompilando..."):
            salida = os.path.join(tmp, "work")
            if decompilado := decompilar_apk(ruta, salida)[0]:
                st.session_state.carpeta_trabajo = salida
                st.success("¡Listo para editar!")

# 4. Panel de control (Solo aparece si hay una APK cargada)
if st.session_state.carpeta_trabajo:
    info = obtener_info_basica(st.session_state.carpeta_trabajo)
    st.caption(f"📦 ID: {info['package']} | v.{info['version']}")

    # Definición de las 5 pestañas (Esto es lo que faltaba antes)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛡️ Privacidad", "🧠 Parches", "👥 Clonar", "🎨 Reskin", "📝 Editor"
    ])

    with tab1:
        st.subheader("Limpiador de Rastreadores")
        if st.button("🧹 Eliminar Anuncios"):
            exito, cant = eliminar_librerias_ads(st.session_state.carpeta_trabajo)
            st.success(f"Se eliminaron {cant} carpetas de publicidad.")

    with tab2:
        st.subheader("Hacks de Comportamiento")
        if st.button("📸 Habilitar Capturas"):
            parche_permitir_capturas(st.session_state.carpeta_trabajo)
            st.toast("Parche de capturas aplicado")
        if st.button("🛡️ Bypass Root"):
            parche_bypass_root(st.session_state.carpeta_trabajo)
            st.toast("Parche Root aplicado")

    with tab3:
        st.subheader("Clonación")
        nuevo_id = st.text_input("Nuevo Package ID:", value=info['package'] + ".clone")
        if st.button("🧬 Clonar App"):
            if clonar_app(st.session_state.carpeta_trabajo, nuevo_id):
                st.success("App clonada. Reiniciando info...")
                st.rerun()

    with tab4:
        st.subheader("Personalización Visual")
        if st.button("🌍 Traducir todo al Español"):
            traducir_textos_app(st.session_state.carpeta_trabajo)
            st.success("Traducción completada.")
        
        nuevo_ico = st.file_uploader("Nuevo Icono (PNG)", type=["png"])
        if nuevo_ico and st.button("Aplicar Nuevo Icono"):
            cambiar_icono_app(st.session_state.carpeta_trabajo, nuevo_ico)
            st.success("Icono cambiado.")

    with tab5:
        st.subheader("📝 Editor con Buscador Inteligente")
        
        # Obtenemos todos los archivos de la APK
        lista = listar_archivos(st.session_state.carpeta_trabajo)
        
        # El buscador que evita que tengas que hacer scroll eterno
        busqueda = st.text_input("🔍 Escribe para buscar (ej: strings, manifest, colors):", "")
        filtrados = [f for f in lista if busqueda.lower() in f.lower()]
        
        if filtrados:
            archivo_sel = st.selectbox(f"Se encontraron {len(filtrados)} archivos:", filtrados)
            ruta_final = os.path.join(st.session_state.carpeta_trabajo, archivo_sel)
            
            try:
                with open(ruta_final, "r", errors="ignore") as f:
                    contenido_actual = f.read()
                
                # Editor de código profesional
                nuevo_cont = st_ace(
                    value=contenido_actual,
                    language="xml" if archivo_sel.endswith(".xml") else "java",
                    theme="monokai",
                    height=400,
                    key=f"editor_{archivo_sel}"
                )
                
                if nuevo_cont != contenido_actual:
                    with open(ruta_final, "w", errors="ignore") as f:
                        f.write(nuevo_cont)
                    st.toast("✅ Cambios guardados")
            except Exception as e:
                st.error("No se puede editar este tipo de archivo.")

    st.divider()
    if st.button("📦 COMPILAR Y FIRMAR APK FINAL"):
        with st.spinner("Construyendo..."):
            nombre_final = "app_modificada.apk"
            if compilar_y_firmar(st.session_state.carpeta_trabajo, nombre_final)[0]:
                with open(nombre_final, "rb") as f:
                    st.download_button("📥 DESCARGAR APK", f, file_name=nombre_final)
                st.balloons()
else:
    st.info("Sube una APK para activar el laboratorio.")