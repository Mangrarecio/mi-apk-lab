import subprocess, os, urllib.request, zipfile, shutil, re
import xml.etree.ElementTree as ET
from googletrans import Translator
from PIL import Image

TOOLS_DIR = "tools"
APKTOOL_JAR = os.path.join(TOOLS_DIR, "apktool.jar")

def descargar_herramientas():
    if not os.path.exists(TOOLS_DIR): os.makedirs(TOOLS_DIR)
    if not os.path.exists(APKTOOL_JAR):
        url = "https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar"
        urllib.request.urlretrieve(url, APKTOOL_JAR)

def ejecutar_comando(comando):
    proceso = subprocess.run(comando, shell=True, capture_output=True, text=True)
    return proceso.returncode == 0, proceso.stdout or proceso.stderr

def decompilar_apk(ruta_apk, carpeta_salida):
    descargar_herramientas()
    comando = f"java -jar {APKTOOL_JAR} d {ruta_apk} -o {carpeta_salida} -f -r" # -r evita decompilar recursos xml complejos que a veces fallan
    return ejecutar_comando(comando)

def compilar_y_firmar(carpeta_proyecto, apk_salida):
    apk_sin_firmar = "temp_unsigned.apk"
    # Usamos --use-aapt2 porque es más moderno y falla menos al recompilar apps complejas
    cmd_build = f"java -jar {APKTOOL_JAR} b {carpeta_proyecto} -o {apk_sin_firmar} --use-aapt2"
    if ejecutar_comando(cmd_build)[0]:
        cmd_align = f"zipalign -f -v 4 {apk_sin_firmar} {apk_salida}"
        ejecutar_comando(cmd_align)
        return True, apk_salida
    return False, "Error en compilación. Revisa los logs."

# --- NUEVO: ELIMINADOR DE ADS (PRIVACIDAD) ---
def eliminar_librerias_ads(carpeta_proyecto):
    """Elimina físicamente las carpetas de los SDKs de anuncios conocidos."""
    # Lista de rutas comunes donde se esconden los anuncios en el código Smali
    rutas_ads = [
        os.path.join("smali", "com", "google", "android", "gms", "ads"), # AdMob
        os.path.join("smali", "com", "facebook", "ads"), # Facebook Audience Network
        os.path.join("smali", "com", "unity3d", "ads"), # Unity Ads
        os.path.join("smali", "com", "applovin"), # AppLovin
        os.path.join("smali", "com", "mopub"), # MoPub
        os.path.join("smali", "com", "ironSource"), # IronSource
        os.path.join("smali", "com", "inmobi"), # InMobi
        os.path.join("smali", "com", "vungle"), # Vungle
        os.path.join("smali", "com", "adcolony") # AdColony
    ]
    
    eliminados = 0
    # Buscamos también en smali_classes2, smali_classes3, etc. para apps grandes
    for raiz_dir in os.listdir(carpeta_proyecto):
        if raiz_dir.startswith("smali"):
            base_smali = os.path.join(carpeta_proyecto, raiz_dir)
            # Intentamos eliminar cada ruta de anuncios conocida
            for ruta_parcial in rutas_ads:
                ruta_completa = os.path.join(carpeta_proyecto, ruta_parcial.replace("smali", raiz_dir))
                if os.path.exists(ruta_completa):
                    try:
                        shutil.rmtree(ruta_completa) # Borrado recursivo de la carpeta
                        eliminados += 1
                    except: pass
    return eliminados > 0, eliminados

# --- CLONACIÓN Y PARCHES ANTERIORES ---
def clonar_app(cp, nid):
    m = os.path.join(cp, "AndroidManifest.xml")
    try:
        with open(m,'r',encoding='utf-8') as f: c=f.read()
        oid = re.search(r'package="([^"]+)"', c).group(1)
        with open(m,'w',encoding='utf-8') as f: f.write(c.replace(oid, nid))
        for r,d,fs in os.walk(cp):
            for f in fs:
                if f.endswith(('.smali','.xml')):
                    p=os.path.join(r,f)
                    with open(p,'r',errors='ignore') as f2: dt=f2.read()
                    if oid in dt:
                        with open(p,'w',errors='ignore') as f2: f2.write(dt.replace(oid,nid))
        return True
    except: return False

def parche_permitir_capturas(cp):
    e=False
    for r,d,fs in os.walk(cp):
        for f in fs:
            if f.endswith(".smali"):
                p=os.path.join(r,f)
                with open(p,'r') as fl: c=fl.read()
                if "setFlags" in c and "0x2000" in c:
                    with open(p,'w') as fl: fl.write(c.replace("0x2000","0x0"))
                    e=True
    return e

def parche_bypass_root(cp):
    pts=["isRooted","checkRoot","test-keys"]
    for r,d,fs in os.walk(cp):
        for f in fs:
            if f.endswith(".smali"):
                p=os.path.join(r,f)
                with open(p,'r') as fl: c=fl.read()
                m=False
                for pt in pts:
                    if pt in c:
                        c=re.sub(r'move-result v(\d+)', r'const/4 v\1, 0x0', c)
                        m=True
                if m:
                    with open(p,'w') as fl: fl.write(c)
    return True

# --- UTILIDADES BÁSICAS ---
def traducir_textos_app(cp):
    r=os.path.join(cp,"res","values","strings.xml")
    if not os.path.exists(r): return False
    try:
        tr=Translator(); t=ET.parse(r); rt=t.getroot()
        for s in rt.findall('string'):
            if s.text and not s.text.startswith('@'):
                try: s.text=tr.translate(s.text,src='en',dest='es').text
                except: continue
        t.write(r,encoding='utf-8',xml_declaration=True); return True
    except: return False

def cambiar_icono_app(cp,im):
    for r,d,fs in os.walk(os.path.join(cp,"res")):
        for f in fs:
            if "ic_launcher" in f and f.lower().endswith(('png','webp')): Image.open(im).save(os.path.join(r,f))
    return True

def listar_archivos(d):
    l=[]
    for r,ds,fs in os.walk(d):
        for f in fs: l.append(os.path.relpath(os.path.join(r,f),d))
    return sorted(l)

def obtener_info_basica(cp):
    try: r=ET.parse(os.path.join(cp,"AndroidManifest.xml")).getroot()
    except: return {"package":"N/A","version":"N/A"}
    return {"package":r.get('package'),"version":r.get('{http://schemas.android.com/apk/res/android}versionName')}