import streamlit as st
from streamlit_ace import st_ace
import os, tempfile
from utils import (
    decompilar_apk, compilar_y_firmar, listar_archivos, 
    obtener_info_basica, traducir_textos_app,
    cambiar_icono_app, clonar_app, parche_permitir_capturas, 
    parche_bypass_root, eliminar_librerias_ads
)

st.set_page_config(page_title="APK Privacy Suite", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; color: #58a6ff; background-color: #161b22; margin-right: 5px; border-radius: 5px; }
    .stButton>button { border: 1px solid #30363d; background-color: #238636; color: white; font-weight: bold; }
    .stButton>button:hover { background-color: #2ea043; }
    .metric-container { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛡️ APK Lab: Suite de Privacidad y Modificación")
st.caption("Herramienta ética para análisis, limpieza y personalización de aplicaciones Android.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🛠️ Laboratorio")
    archivo = st.file_uploader("Cargar APK (Solo uso ético)", type="apk")
    if archivo and st.button("🚀 Analizar y Desmontar"):
        tmp = tempfile.mkdtemp()
        ruta = os.path.join(tmp, "base.apk")
        with open(ruta, "wb") as f: f.write(archivo.getbuffer())
        with st.spinner("Ingeniería inversa en proceso... (Esto puede tardar en apps grandes)"):
            salida = os.path.join(tmp, "work")
            # He añadido el flag -r en utils.py para que sea más estable con apps complejas
            if decompilar_apk(ruta, salida)[0]:
                st.session_state.carpeta_trabajo = salida
                st.success("APK lista para modificar.")
            else:
                st.error("Error al decompilar. Algunas apps están protegidas contra esto.")

# --- AREA DE TRABAJO ---
if st.session_state.carpeta_trabajo:
    info = obtener_info_basica(st.session_state.carpeta_trabajo)
    st.markdown(f"""<div class="metric-container">
        <b>Objetivo:</b> {info['package']} | <b>Versión:</b> {info['version']}
        </div>""", unsafe_allow_html=True)
    st.write("") # Espacio

    # PESTAÑAS REORGANIZADAS
    tab_privacy, tab_hacks, tab_clone, tab_reskin, tab_edit = st.tabs([
        "🛡️ Privacidad y Limpieza", "🧠 Parches de Comportamiento", "👥 Clonación", "🎨 Personalización", "📝 Editor Avanzado"
    ])

    # PESTAÑA 1: LA NUEVA JOYA DE LA CORONA
    with tab_privacy:
        st.subheader("Limpiador de Rastreadores y Publicidad")
        st.write("Este módulo busca y elimina las librerías de código conocidas por mostrar publicidad y rastrear usuarios.")
        st.info("💡 Ideal para aligerar apps gratuitas cargadas de anuncios.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.warning("⚠️ Advertencia: Eliminar estas librerías puede hacer que algunas apps inestables se cierren. Úsalo bajo tu propio riesgo.")
        with col2:
             if st.button("🧹 EJECUTAR LIMPIEZA DE ADS", type="primary"):
                with st.spinner("Escaneando y eliminando basura..."):
                    exito, cantidad = eliminar_librerias_ads(st.session_state.carpeta_trabajo)
                    if exito:
                        st.success(f"¡Éxito! Se han eliminado {cantidad} carpetas de SDKs de publicidad.")
                        st.balloons()
                    else:
                        st.warning("No se encontraron librerías de publicidad conocidas en esta app.")

    # PESTAÑA 2: HACKS ÉTICOS (Capturas y Root)
    with tab_hacks:
        st.subheader("Modificaciones de Comportamiento")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📸 Permitir Capturas de Pantalla (Bypass FLAG_SECURE)"):
                if parche_permitir_capturas(st.session_state.carpeta_trabajo):
                    st.success("Protección eliminada. Ahora puedes hacer capturas en apps privadas.")
                else: st.warning("No se detectó la protección de pantalla.")
        with c2:
            if st.button("🛡️ Ocultar Root/Emulador"):
                if parche_bypass_root(st.session_state.carpeta_trabajo):
                    st.success("Parche aplicado. La app creerá que el entorno es seguro.")

    # PESTAÑA 3: CLONACIÓN
    with tab_clone:
        st.subheader("Duplicador de Aplicaciones")
        nid = st.text_input("Nuevo ID de paquete:", value=info['package'] + ".dual")
        if st.button("🧬 Crear Clon"):
            with st.spinner("Clonando identidad..."):
                if clonar_app(st.session_state.carpeta_trabajo, nid):
                    st.success(f"Identidad cambiada a {nid}. Ya puedes compilar el clon.")
                    st.experimental_rerun()

    # PESTAÑA 4: RESKIN & TRADUCCIÓN
    with tab_reskin:
        c1, c2 = st.columns(2)
        with c1:
            st.write("🌍 **Traducción Automática (IA)**")
            if st.button("Traducir Inglés -> Español"):
                with st.spinner("Traduciendo..."):
                    traducir_textos_app(st.session_state.carpeta_trabajo)
                    st.success("Textos traducidos.")
        with c2:
            st.write("🖼️ **Cambiar Icono**")
            ico = st.file_uploader("Sube imagen (PNG/JPG)", type=["png", "jpg"])
            if ico and st.button("Aplicar Icono"):
                cambiar_icono_app(st.session_state.carpeta_trabajo, ico)
                st.success("Icono actualizado.")

    # PESTAÑA 5: EDITOR
    with tab_edit:
        fls = listar_archivos(st.session_state.carpeta_trabajo)
        sel = st.selectbox("Archivo:", fls)
        pth = os.path.join(st.session_state.carpeta_trabajo, sel)
        with open(pth, "r", errors="ignore") as f: txt = f.read()
        new = st_ace(value=txt, language="xml" if sel.endswith(".xml") else "java", theme="monokai", height=400)
        if new != txt:
            with open(pth, "w") as f: f.write(new)
            st.toast("Guardado")

    st.divider()
    # Botón de compilación más robusto (usa aapt2)
    if st.button("📦 COMPILAR APK MODIFICADA (PRO)"):
        with st.spinner("Reconstruyendo con motor AAPT2..."):
            nom = "app_mod_privacy.apk"
            ok, res = compilar_y_firmar(st.session_state.carpeta_trabajo, nom)
            if ok:
                with open(res, "rb") as f:
                    st.download_button("📥 DESCARGAR APK FINAL", f, file_name=nom)
                st.balloons()
            else:
                st.error("Error al compilar. A veces eliminar ciertas librerías rompe la app.")
else:
    st.info("Bienvenido al laboratorio ético. Sube un APK para comenzar.")