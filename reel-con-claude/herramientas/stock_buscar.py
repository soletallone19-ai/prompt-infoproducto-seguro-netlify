"""Paso 3: busca clips candidatos (gratis) y baja solo las miniaturas.

Uso: python herramientas/stock_buscar.py [escena_id ...]
Sin argumentos busca todas las escenas de reel/escenas.json; con ids, re-busca
solo esas y conserva el resto de candidatos.json.
"""
import hashlib
import os
import sys
import time
import urllib.parse

from comun import REEL, bajar, cargar_env, escribir_json, http_json, leer_json, registrar

CACHE = REEL / "cache"
POR_ESCENA = 3


def cacheado(url, headers=None):
    clave = hashlib.sha256(url.encode()).hexdigest()[:20]
    ruta = CACHE / f"{clave}.json"
    if ruta.exists() and time.time() - ruta.stat().st_mtime < 86400:
        return leer_json(ruta), True
    datos = http_json(url, headers)
    escribir_json(ruta, datos)
    time.sleep(0.7)  # < 100 pedidos/min
    return datos, False


def sirve(ancho, alto, dur):
    if dur < 3:
        return False
    if alto >= ancho and alto >= 1920:
        return True
    return alto >= 1080 and ancho >= alto * 9 / 16


def pixabay(termino, clave):
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": clave, "q": termino, "video_type": "film", "safesearch": "true", "per_page": 50})
    datos, cache = cacheado(url)
    if not cache:
        registrar("pixabay", f"buscar '{termino}'", "ok", costo=0)
    for h in datos.get("hits", []):
        archivos = [v for v in h["videos"].values() if v.get("url")]
        mayor = max(archivos, key=lambda v: v.get("width", 0) * v.get("height", 0))
        yield {"proveedor": "pixabay", "id": h["id"], "autor": h.get("user"),
               "pagina": h.get("pageURL"), "archivo": mayor["url"],
               "ancho": mayor["width"], "alto": mayor["height"], "duracion": h["duration"],
               "miniatura": mayor.get("thumbnail") or h["videos"].get("medium", {}).get("thumbnail")}


def pexels(termino, clave):
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": termino, "orientation": "portrait", "size": "medium", "per_page": 15})
    datos, cache = cacheado(url, {"Authorization": clave})
    if not cache:
        registrar("pexels", f"buscar '{termino}'", "ok", costo=0)
    for v in datos.get("videos", []):
        archivos = [f for f in v["video_files"] if f.get("width") and f.get("height")]
        if not archivos:
            continue
        mayor = max(archivos, key=lambda f: f["width"] * f["height"])
        yield {"proveedor": "pexels", "id": v["id"], "autor": v["user"]["name"],
               "pagina": v["url"], "archivo": mayor["link"],
               "ancho": mayor["width"], "alto": mayor["height"], "duracion": v["duration"],
               "miniatura": v.get("image")}


def main():
    cargar_env()
    pex, pix = os.environ.get("PEXELS_API_KEY"), os.environ.get("PIXABAY_API_KEY")
    if not (pex or pix):
        sys.exit("Falta PIXABAY_API_KEY (o PEXELS_API_KEY) en .env")
    escenas = leer_json(REEL / "escenas.json")
    if not escenas:
        sys.exit("Falta reel/escenas.json (paso 2)")
    solo = set(sys.argv[1:])
    descartados = {str(i) for i in leer_json(REEL / "descartados.json", [])}
    candidatos = leer_json(REEL / "candidatos" / "candidatos.json", {})
    for esc in escenas:
        eid = str(esc["id"])
        if solo and eid not in solo:
            continue
        vistos, elegidos = set(), []
        for termino in esc["palabras_clave"]:
            fuente = pexels(termino, pex) if pex else pixabay(termino, pix)
            for c in fuente:
                if str(c["id"]) in descartados or c["id"] in vistos:
                    continue
                if not sirve(c["ancho"], c["alto"], c["duracion"]):
                    continue
                vistos.add(c["id"])
                c["termino"] = termino
                elegidos.append(c)
                if len(elegidos) >= POR_ESCENA:
                    break
            if len(elegidos) >= POR_ESCENA:
                break
        for c in elegidos:
            if c.get("miniatura"):
                destino = REEL / "candidatos" / f"{eid}_{c['id']}.jpg"
                if not destino.exists():
                    bajar(c["miniatura"], destino)
                c["miniatura_local"] = str(destino.relative_to(REEL.parent))
        candidatos[eid] = elegidos
        print(f"escena {eid}: {len(elegidos)} candidato(s)")
    escribir_json(REEL / "candidatos" / "candidatos.json", candidatos)


if __name__ == "__main__":
    main()
