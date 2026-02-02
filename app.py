import streamlit as st
from streamlit_ace import st_ace
import os, tempfile
from utils import (
    decompilar_apk, compilar_y_firmar, listar_archivos, 
    obtener_info_basica, traducir_textos_app,
    cambiar_icono_app, clonar_app, parche_permitir_capturas, 
    parche_bypass_root, eliminar_librerias_ads
)

# Configuración de pantalla ancha para que quepa todo
st.set_page_config(page_title="APK Privacy Suite", layout="wide", page_icon="🛡️")

# ESTILO PARA COMPACTAR PESTAÑAS (Para que quepan las 5)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px;
        background-color: #161b22;
        border-radius: 5px;
        font-size: 14px;
    }
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    </style>
    """, unsafe_allow_html=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛡️ APK Lab: Suite Profesional")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🛠️ Laboratorio")
    archivo = st.file_uploader("Cargar APK", type="apk")
    if archivo and st.button("🚀 Analizar y Desmontar"):
        tmp = tempfile.mkdtemp()
        ruta = os.path.join(tmp, "base.apk")
        with open(ruta, "wb") as f: f.write(archivo.getbuffer())
        with st.spinner("Analizando entrañas de la APK..."):
            salida = os.path.join(tmp, "work")
            if decompilar_apk(ruta, salida)[0]:
                st.session_state.carpeta_trabajo = salida
                st.success("¡Análisis completo!")

# --- AREA DE TRABAJO ---
if st.session_state.carpeta_trabajo:
    info = obtener_info_basica(st.session_state.carpeta_trabajo)
    st.info(f"📦 {info['package']} | 🏷️ v.{info['version']}")

    # AQUÍ ESTÁN LAS 5 PESTAÑAS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛡️ Privacidad", "🧠 Parches", "👥 Clonar", "🎨 Reskin", "📝 Editor"
    ])

    with tab1:
        st.subheader("Eliminador de Publicidad")
        if st.button("🧹 Limpiar SDKs de Ads"):
            exito, cant = eliminar_librerias_ads(st.session_state.carpeta_trabajo)
            if exito: st.success(f"Eliminadas {cant} librerías de rastreo.")
            else: st.warning("No se encontraron anuncios conocidos.")

    with tab2:
        st.subheader("Modificar Comportamiento")
        if st.button("📸 Permitir Capturas"):
            if parche_permitir_capturas(st.session_state.carpeta_trabajo): st.success("¡Hecho!")
        if st.button("🛡️ Bypass Root"):
            if parche_bypass_root(st.session_state.carpeta_trabajo): st.success("¡Hecho!")

    with tab3:
        st.subheader("Duplicar App")
        nid = st.text_input("ID del Clon:", value=info['package'] + ".clon")
        if st.button("🧬 Ejecutar Clonación"):
            if clonar_app(st.session_state.carpeta_trabajo, nid):
                st.success("ID Cambiado correctamente.")
                st.rerun()

    with tab4:
        st.subheader("Apariencia y Lenguaje")
        if st.button("🌍 Traducir a Español"):
            with st.spinner("Traduciendo..."):
                traducir_textos_app(st.session_state.carpeta_trabajo)
                st.success("Textos traducidos.")
        
        ico = st.file_uploader("Nuevo Icono (PNG)", type=["png"])
        if ico and st.button("Cambiar Imagen"):
            cambiar_icono_app(st.session_state.carpeta_trabajo, ico)
            st.success("Icono cambiado.")

    with tab5:
        st.subheader("Editor de Código Avanzado")
        st.write("Modifica manualmente cualquier archivo de la app.")
        archivos = listar_archivos(st.session_state.carpeta_trabajo)
        sel = st.selectbox("Busca un archivo (ej: strings.xml):", archivos)
        pth = os.path.join(st.session_state.carpeta_trabajo, sel)
        
        # Leemos el código del archivo seleccionado
        with open(pth, "r", errors="ignore") as f: txt = f.read()
        
        # El Editor Mágico
        nuevo_codigo = st_ace(
            value=txt, 
            language="xml" if sel.endswith(".xml") else "java",
            theme="monokai",
            height=300
        )
        
        if nuevo_codigo != txt:
            with open(pth, "w") as f: f.write(nuevo_codigo)
            st.toast("✅ Cambios guardados en el archivo")

    st.divider()
    if st.button("📦 GENERAR NUEVA APK MODIFICADA"):
        with st.spinner("Construyendo..."):
            nom = "app_modificada.apk"
            ok, res = compilar_y_firmar(st.session_state.carpeta_trabajo, nom)
            if ok:
                with open(res, "rb") as f:
                    st.download_button("📥 DESCARGAR RESULTADO", f, file_name=nom)
                st.balloons()
else:
    st.info("Sube una APK en el panel de la izquierda para empezar.")