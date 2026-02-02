import streamlit as st
from streamlit_ace import st_ace
import os, tempfile
from utils import (
    decompilar_apk, compilar_y_firmar, listar_archivos, 
    obtener_info_basica, traducir_textos_app,
    cambiar_icono_app, clonar_app, parche_permitir_capturas, 
    parche_bypass_root, eliminar_librerias_ads
)

# Configuración de página ancha (Estilo IDE)
st.set_page_config(page_title="APK Lab Expert", layout="wide", page_icon="🛡️")

# Estilo CSS para que parezca una herramienta profesional
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 15px;
        background-color: #161b22;
        border-radius: 5px;
        border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] { background-color: #238636 !important; border-color: #2ea043 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'carpeta_trabajo' not in st.session_state:
    st.session_state.carpeta_trabajo = None

st.title("🛡️ APK Lab Expert")

# --- BARRA LATERAL (SUBIDA DE ARCHIVOS) ---
with st.sidebar:
    st.header("⚙️ Laboratorio")
    archivo = st.file_uploader("Cargar APK para cirujía", type="apk")
    if archivo and st.button("🚀 Iniciar Decompilación"):
        tmp = tempfile.mkdtemp()
        ruta_apk = os.path.join(tmp, "base.apk")
        with open(ruta_apk, "wb") as f: f.write(archivo.getbuffer())
        with st.spinner("Desmontando APK... (Paciencia, esto es arte)"):
            salida = os.path.join(tmp, "work")
            if decompilar_apk(ruta_apk, salida)[0]:
                st.session_state.carpeta_trabajo = salida
                st.success("¡APK lista para modificar!")

# --- CUERPO PRINCIPAL (SOLO SI HAY APK) ---
if st.session_state.carpeta_trabajo:
    info = obtener_info_basica(st.session_state.carpeta_trabajo)
    st.caption(f"📦 Paquete: `{info['package']}` | 🏷️ Versión: `{info['version']}`")

    # Las 5 Pestañas Maestras
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛡️ Privacidad", "🧠 Parches", "👥 Clonación", "🎨 Reskin", "📝 Editor IDE"
    ])

    with tab1:
        st.subheader("Limpiador de Rastreadores")
        if st.button("🧹 Eliminar Anuncios y Telemetría"):
            exito, cant = eliminar_librerias_ads(st.session_state.carpeta_trabajo)
            st.success(f"Se han extirpado {cant} módulos de publicidad.")

    with tab2:
        st.subheader("Bypass de Seguridad")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📸 Habilitar Capturas de Pantalla"):
                parche_permitir_capturas(st.session_state.carpeta_trabajo)
                st.toast("Restricciones de pantalla eliminadas")
        with c2:
            if st.button("🛡️ Ocultar Root/Emulador"):
                parche_bypass_root(st.session_state.carpeta_trabajo)
                st.toast("Detección de seguridad anulada")

    with tab3:
        st.subheader("Duplicador de Identidad")
        nuevo_id = st.text_input("Nuevo Package ID:", value=info['package'] + ".clon")
        if st.button("🧬 Generar Clon"):
            if clonar_app(st.session_state.carpeta_trabajo, nuevo_id):
                st.success("Identidad cambiada. Ya puedes compilar.")
                st.rerun()

    with tab4:
        st.subheader("Traducción y Estética")
        if st.button("🌍 Traducir Interfaz a Español"):
            with st.spinner("Traduciendo con IA..."):
                traducir_textos_app(st.session_state.carpeta_trabajo)
                st.success("¡App traducida!")
        
        nuevo_ico = st.file_uploader("Subir nuevo icono (PNG)", type=["png"])
        if nuevo_ico and st.button("🎨 Aplicar Icono"):
            cambiar_icono_app(st.session_state.carpeta_trabajo, nuevo_ico)
            st.success("Imagen de icono reemplazada.")

    # EL SANTO GRIAL: EXPLORADOR + EDITOR
    with tab5:
        st.subheader("📂 Explorador de Proyecto")
        
        # 1. Obtener lista de archivos
        archivos_totales = listar_archivos(st.session_state.carpeta_trabajo)
        
        # Buscador rápido arriba
        busqueda = st.text_input("🔍 Buscar archivo por nombre...", "")
        lista_filtrada = [f for f in archivos_totales if busqueda.lower() in f.lower()]

        # 2. Layout de 2 columnas (1:4 de proporción)
        col_tree, col_editor = st.columns([1, 3])

        with col_tree:
            st.write("📂 **Estructura**")
            # Extraemos las carpetas de primer nivel
            carpetas_raiz = sorted(list(set([f.split(os.sep)[0] for f in lista_filtrada])))
            folder_sel = st.selectbox("Carpeta:", ["Todas"] + carpetas_raiz)
            
            # Filtramos por carpeta
            if folder_sel != "Todas":
                final_list = [f for f in lista_filtrada if f.startswith(folder_sel)]
            else:
                final_list = lista_filtrada

            # Radio para seleccionar archivo como en un árbol real
            archivo_elegido = st.radio("Archivos:", final_list, label_visibility="collapsed")

        with col_editor:
            if archivo_elegido:
                ruta_full = os.path.join(st.session_state.carpeta_trabajo, archivo_elegido)
                st.caption(f"📄 Editando: `{archivo_elegido}`")
                
                try:
                    with open(ruta_full, "r", errors="ignore") as f:
                        codigo_inicial = f.read()
                    
                    # Determinar lenguaje para el resaltado
                    ext = archivo_elegido.split('.')[-1]
                    lang_map = {"xml": "xml", "smali": "java", "json": "json", "yml": "yaml"}
                    
                    nuevo_codigo = st_ace(
                        value=codigo_inicial,
                        language=lang_map.get(ext, "text"),
                        theme="monokai",
                        height=500,
                        key=f"editor_{archivo_elegido}"
                    )
                    
                    if nuevo_codigo != codigo_inicial:
                        with open(ruta_full, "w", errors="ignore") as f:
                            f.write(nuevo_codigo)
                        st.toast("✅ Archivo guardado")
                except:
                    st.error("Este archivo es binario y no se puede editar aquí.")

    st.divider()
    # Botón de construcción final
    if st.button("📦 COMPILAR Y FIRMAR APK"):
        with st.spinner("Reconstruyendo el binario..."):
            nombre_final = "modificada_por_mi.apk"
            if compilar_y_firmar(st.session_state.carpeta_trabajo, nombre_final)[0]:
                with open(nombre_final, "rb") as f:
                    st.download_button("📥 DESCARGAR RESULTADO", f, file_name=nombre_final)
                st.balloons()
else:
    st.info("Sube una APK en el panel lateral para desplegar las herramientas.")