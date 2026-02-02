import streamlit as st
from streamlit_ace import st_ace
import os
import tempfile
import shutil
from utils import (
    decompilar_apk, compilar_y_firmar, listar_archivos, 
    extraer_permisos, buscar_imagenes, buscar_texto_en_archivos
)

# Configuración de la página
st.set_page_config(page_title="APK Lab Expert", layout="wide", page_icon="🛡️")

# Estilo personalizado
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e2129; border-radius: 5px; color: white; padding: 10px 20px; }
    </style>
    """, unsafe_allow_value=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛡️ APK Lab: Plataforma de Ingeniería Inversa")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📂 Carga de Archivos")
    archivo_subido = st.file_uploader("Sube tu archivo APK", type="apk")
    
    if archivo_subido and st.button("🚀 Desmontar APK"):
        directorio_tmp = tempfile.mkdtemp()
        ruta_apk = os.path.join(directorio_tmp, "original.apk")
        with open(ruta_apk, "wb") as f:
            f.write(archivo_subido.getbuffer())
        
        with st.spinner("Procesando..."):
            salida = os.path.join(directorio_tmp, "proyecto")
            exito, mensaje = decompilar_apk(ruta_apk, salida)
            if exito:
                st.session_state.carpeta_trabajo = salida
                st.success("¡Listos para trabajar!")
            else:
                st.error(f"Error: {mensaje}")

# --- CONTENIDO PRINCIPAL ---
if st.session_state.carpeta_trabajo:
    # Ahora tenemos 4 pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Editor", "🔍 Seguridad", "🖼️ Imágenes", "🔎 Buscador"
    ])

    # PESTAÑA 1: EDITOR
    with tab1:
        col_files, col_code = st.columns([1, 3])
        with col_files:
            todos_archivos = listar_archivos(st.session_state.carpeta_trabajo)
            seleccion = st.selectbox("Archivo actual:", todos_archivos)
        
        with col_code:
            ruta_archivo = os.path.join(st.session_state.carpeta_trabajo, seleccion)
            with open(ruta_archivo, "r", errors="ignore") as f:
                contenido = f.read()
            idioma = "xml" if seleccion.endswith(".xml") else "java"
            nuevo_texto = st_ace(value=contenido, language=idioma, theme="monokai", height=500)
            if nuevo_texto != contenido:
                with open(ruta_archivo, "w") as f:
                    f.write(nuevo_texto)
                st.toast("Guardado", icon="💾")

    # PESTAÑA 2: SEGURIDAD
    with tab2:
        st.subheader("Permisos Detectados")
        lista_p = extraer_permisos(st.session_state.carpeta_trabajo)
        for p in lista_p:
            if any(x in p.upper() for x in ["CAMERA", "SMS", "LOCATION", "CONTACTS"]):
                st.error(f"⚠️ SENSIBLE: {p}")
            else:
                st.info(f"✅ {p}")

    # PESTAÑA 3: IMÁGENES
    with tab3:
        st.subheader("Galería de Recursos")
        fotos = buscar_imagenes(st.session_state.carpeta_trabajo)
        if fotos:
            columnas = st.columns(5)
            for i, r in enumerate(fotos[:50]):
                with columnas[i % 5]:
                    st.image(r, use_container_width=True)
        else:
            st.write("No hay imágenes.")

    # PESTAÑA 4: BUSCADOR (NUEVA)
    with tab4:
        st.subheader("🔎 Buscador de Código")
        st.write("Busca textos específicos en todos los archivos del proyecto.")
        
        termino = st.text_input("¿Qué quieres buscar? (ej: 'http', 'API_KEY', 'password')")
        
        if termino:
            if len(termino) < 3:
                st.warning("Escribe al menos 3 letras.")
            else:
                encontrados = buscar_texto_en_archivos(st.session_state.carpeta_trabajo, termino)
                if encontrados:
                    st.success(f"Se encontraron {len(encontrados)} coincidencias.")
                    for item in encontrados[:100]: # Mostramos los primeros 100
                        with st.expander(f"📄 {item['archivo']} - Línea {item['linea']}"):
                            st.code(item['contenido'])
                else:
                    st.info("No se encontró nada con ese nombre.")

    # BOTÓN FINAL
    st.divider()
    if st.button("📦 Recompilar APK"):
        with st.spinner("Construyendo..."):
            nombre = "mod_final.apk"
            exito, final = compilar_y_firmar(st.session_state.carpeta_trabajo, nombre)
            if exito:
                with open(final, "rb") as f:
                    st.download_button("📥 DESCARGAR APK", f, file_name=nombre)
                st.balloons()

else:
    st.info("Sube un APK para empezar.")