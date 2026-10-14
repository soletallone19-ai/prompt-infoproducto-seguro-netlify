"""Utilidades compartidas: rutas, .env, JSON y registro de solicitudes."""
import datetime
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REEL = RAIZ / "reel"
FPS = 30


def cargar_env():
    """Carga .env en os.environ sin imprimir nada."""
    ruta = RAIZ / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        if v.strip():
            os.environ.setdefault(k.strip(), v.strip())


def leer_json(ruta, defecto=None):
    ruta = Path(ruta)
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    return defecto


def escribir_json(ruta, datos):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def ahora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def registrar(servicio, accion, estado, costo=None, **extra):
    """Agrega una solicitud a reel/registro.json. Costo desconocido = None."""
    ruta = REEL / "registro.json"
    reg = leer_json(ruta, [])
    item = {"n": len(reg) + 1, "fecha": ahora(), "servicio": servicio,
            "accion": accion, "estado": estado, "costo": costo, **extra}
    reg.append(item)
    escribir_json(ruta, reg)
    return item["n"]


def actualizar_registro(n, **campos):
    ruta = REEL / "registro.json"
    reg = leer_json(ruta, [])
    for item in reg:
        if item["n"] == n:
            item.update(campos)
            item["actualizado"] = ahora()
    escribir_json(ruta, reg)


def http_json(url, headers=None, metodo="GET", cuerpo=None, timeout=60):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo,
                                 headers={"User-Agent": "reel-con-claude", **(headers or {})})
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def bajar(url, destino, timeout=120):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "reel-con-claude"})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(destino, "wb") as f:
        while bloque := r.read(1 << 20):
            f.write(bloque)
    return destino


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while bloque := f.read(1 << 20):
            h.update(bloque)
    return h.hexdigest()


def sondear(ruta):
    """Devuelve ancho, alto, duración y códecs de un archivo con ffprobe."""
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(ruta)],
        capture_output=True, text=True, check=True).stdout
    info = json.loads(salida)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
    return {"ancho": video.get("width"), "alto": video.get("height"),
            "duracion": float(info["format"].get("duration", 0)),
            "video": video.get("codec_name"), "audio": audio.get("codec_name")}


def a_cuadros(seg):
    """Redondea segundos a cuadros enteros a 30 fps."""
    return round(seg * FPS) / FPS
