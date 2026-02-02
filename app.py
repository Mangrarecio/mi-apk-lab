with tab5:
        st.subheader("📝 Editor de Código Inteligente")
        
        # Obtenemos la lista de archivos
        todos_los_archivos = listar_archivos(st.session_state.carpeta_trabajo)
        
        # --- MEJORA: BUSCADOR RÁPIDO ---
        busqueda = st.text_input("🔍 Buscar archivo (ej: strings.xml o smali):", "").lower()
        
        # Filtramos la lista según lo que escribas
        archivos_filtrados = [f for f in todos_los_archivos if busqueda in f.lower()]
        
        if not archivos_filtrados:
            st.warning("No se encontraron archivos con ese nombre.")
            sel = None
        else:
            # Mostramos solo lo que coincide con la búsqueda
            sel = st.selectbox(
                f"📂 Selecciona uno de los {len(archivos_filtrados)} archivos encontrados:", 
                archivos_filtrados,
                key="editor_selector" # Esto ayuda a Streamlit a no perder el foco
            )

        if sel:
            pth = os.path.join(st.session_state.carpeta_trabajo, sel)
            
            # Intentamos leer el archivo
            try:
                with open(pth, "r", errors="ignore") as f: 
                    txt = f.read()
                
                st.caption(f"📍 Editando: {sel}")
                
                # El Editor (Ace)
                nuevo_codigo = st_ace(
                    value=txt, 
                    language="xml" if sel.endswith(".xml") else "java",
                    theme="monokai",
                    height=400,
                    key=f"ace_{sel}" # Cambia la clave según el archivo para evitar errores
                )
                
                if nuevo_codigo != txt:
                    with open(pth, "w", errors="ignore") as f: 
                        f.write(nuevo_codigo)
                    st.toast(f"✅ Guardado: {os.path.basename(sel)}")
            except Exception as e:
                st.error(f"No se pudo abrir este archivo: {e}")