import subprocess
import os
import urllib.request
import zipfile
import shutil
import xml.etree.ElementTree as ET

TOOLS_DIR = "tools"
APKTOOL_JAR = os.path.join(TOOLS_DIR, "apktool.jar")
JADX_ZIP = os.path.join(TOOLS_DIR, "jadx.zip")
JADX_BIN = os.path.join(TOOLS_DIR, "jadx", "bin", "jadx")

def descargar_herramientas():
    """Descarga las herramientas necesarias si no existen."""
    if not os.path.exists(TOOLS_DIR):
        os.makedirs(TOOLS_DIR)

    if not os.path.exists(APKTOOL_JAR):
        url = "https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar"
        urllib.request.urlretrieve(url, APKTOOL_JAR)

    if not os.path.exists(JADX_BIN):
        url = "https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip"
        urllib.request.urlretrieve(url, JADX_ZIP)
        with zipfile.ZipFile(JADX_ZIP, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(TOOLS_DIR, "jadx"))
        os.chmod(JADX_BIN, 0o755)

def ejecutar_comando(comando):
    """Ejecuta un comando en el sistema."""
    proceso = subprocess.run(comando, shell=True, capture_output=True, text=True)
    return proceso.returncode == 0, proceso.stdout or proceso.stderr

def decompilar_apk(ruta_apk, carpeta_salida):
    """Desmonta el APK usando Apktool."""
    descargar_herramientas()
    comando = f"java -jar {APKTOOL_JAR} d {ruta_apk} -o {carpeta_salida} -f"
    return ejecutar_comando(comando)

def compilar_y_firmar(carpeta_proyecto, apk_salida):
    """Reconstruye el APK y lo optimiza con zipalign."""
    apk_sin_firmar = "temporal_unsigned.apk"
    comando_build = f"java -jar {APKTOOL_JAR} b {carpeta_proyecto} -o {apk_sin_firmar}"
    exito, log = ejecutar_comando(comando_build)
    
    if exito:
        comando_align = f"zipalign -f -v 4 {apk_sin_firmar} {apk_salida}"
        ejecutar_comando(comando_align)
        return True, apk_salida
    return False, log

def listar_archivos(directorio):
    """Lista todos los archivos del proyecto para el editor."""
    lista = []
    for raiz, dirs, archivos in os.walk(directorio):
        for nombre in archivos:
            ruta_relativa = os.path.relpath(os.path.join(raiz, nombre), directorio)
            lista.append(ruta_relativa)
    return sorted(lista)

def extraer_permisos(carpeta_proyecto):
    """Busca y lee los permisos en el AndroidManifest.xml."""
    ruta_manifest = os.path.join(carpeta_proyecto, "AndroidManifest.xml")
    permisos = []
    if not os.path.exists(ruta_manifest):
        return ["No se encontró el Manifest"]
    try:
        tree = ET.parse(ruta_manifest)
        root = tree.getroot()
        for permiso in root.findall('uses-permission'):
            nombre = permiso.get('{http://schemas.android.com/apk/res/android}name')
            if nombre:
                permisos.append(nombre)
    except:
        return ["Error leyendo el archivo XML"]
    return permisos

def buscar_imagenes(carpeta_proyecto):
    """Busca archivos de imagen en la carpeta de recursos."""
    imagenes = []
    extensiones = ('.png', '.jpg', '.jpeg', '.webp', '.svg')
    ruta_res = os.path.join(carpeta_proyecto, "res")
    
    if os.path.exists(ruta_res):
        for raiz, dirs, archivos in os.walk(ruta_res):
            for archivo in archivos:
                if archivo.lower().endswith(extensiones):
                    imagenes.append(os.path.join(raiz, archivo))
    return imagenes

def buscar_texto_en_archivos(directorio, termino):
    """Busca una palabra clave en todos los archivos de texto del proyecto."""
    resultados = []
    # Solo buscamos en archivos que suelen contener texto/código
    extensiones_texto = ('.xml', '.smali', '.java', '.txt', '.json', '.yml')
    
    for raiz, dirs, archivos in os.walk(directorio):
        for nombre_archivo in archivos:
            if nombre_archivo.lower().endswith(extensiones_texto):
                ruta_completa = os.path.join(raiz, nombre_archivo)
                try:
                    with open(ruta_completa, 'r', errors='ignore') as f:
                        for num_linea, linea in enumerate(f, 1):
                            if termino.lower() in linea.lower():
                                ruta_relat = os.path.relpath(ruta_completa, directorio)
                                resultados.append({
                                    "archivo": ruta_relat,
                                    "linea": num_linea,
                                    "contenido": linea.strip()
                                })
                except:
                    continue
    return resultados