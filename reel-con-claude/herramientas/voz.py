"""Paso 5 (PAGO): voz con marcas de tiempo en ElevenLabs.

Uso:
  python herramientas/voz.py voces                      lista voces (gratis)
  python herramientas/voz.py estimar                    créditos estimados (gratis)
  python herramientas/voz.py generar <voice_id> <tope>  genera, solo si estimado <= tope

El texto sale de reel/guion.txt (una frase por línea, en orden de bloque).
"""
import base64
import json
import os
import sys
import urllib.error

from comun import REEL, actualizar_registro, cargar_env, escribir_json, http_json, registrar

API = "https://api.elevenlabs.io/v1"


def texto():
    ruta = REEL / "guion.txt"
    if not ruta.exists():
        sys.exit("Falta reel/guion.txt (una frase por línea)")
    return " ".join(l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip())


def estimado():
    return round(len(texto()) * 1.2)


def clave():
    cargar_env()
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        sys.exit("Falta ELEVENLABS_API_KEY en .env (elevenlabs.io → Profile → API keys)")
    return {"xi-api-key": k}


def consumo_historial(h, desde_unix):
    """Lee el consumo real del ítem nuevo del historial. None si no aparece."""
    try:
        hist = http_json(f"{API}/history?page_size=5", h)
    except urllib.error.URLError:
        return None
    for item in hist.get("history", []):
        if item.get("date_unix", 0) >= desde_unix - 5:
            a, b = item.get("character_count_change_from"), item.get("character_count_change_to")
            if a is not None and b is not None and b - a > 0:
                return b - a
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "estimar":
        print(f"{len(texto())} caracteres → ~{estimado()} créditos")
        return
    h = clave()
    if cmd == "voces":
        for v in http_json(f"{API}/voices", h)["voices"]:
            lab = v.get("labels") or {}
            print(v["voice_id"], v["name"], lab.get("accent"), lab.get("gender"), lab.get("language"))
        return
    if cmd != "generar" or len(sys.argv) != 4:
        sys.exit(__doc__)
    voice_id, tope = sys.argv[2], int(sys.argv[3])
    est = estimado()
    if est > tope:
        sys.exit(f"Estimado {est} créditos supera el tope {tope}. No se envía.")
    import time
    t0 = int(time.time())
    try:
        antes = http_json(f"{API}/user/subscription", h).get("character_count")
    except urllib.error.URLError:
        antes = None
    n = registrar("elevenlabs", "text-to-speech/with-timestamps", "enviando",
                  costo=None, estimado=est, tope=tope, voice_id=voice_id)
    cuerpo = {"text": texto(), "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.2}}
    try:
        r = http_json(f"{API}/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128",
                      h, metodo="POST", cuerpo=cuerpo, timeout=180)
    except urllib.error.HTTPError as e:
        actualizar_registro(n, estado="error", detalle=f"HTTP {e.code}")
        sys.exit(f"ElevenLabs respondió {e.code}. Revisá el registro; no se reintenta solo.")
    (REEL / "voz.mp3").write_bytes(base64.b64decode(r["audio_base64"]))
    al = r.get("alignment") or r.get("normalized_alignment")
    escribir_json(REEL / "alineacion.json", {
        "characters": al["characters"],
        "character_start_times_seconds": al["character_start_times_seconds"],
        "character_end_times_seconds": al["character_end_times_seconds"]})
    time.sleep(3)
    real = consumo_historial(h, t0)
    try:
        despues = http_json(f"{API}/user/subscription", h).get("character_count")
    except urllib.error.URLError:
        despues = None
    contador = (despues - antes) if (antes is not None and despues is not None and despues > antes) else None
    actualizar_registro(n, estado="ok", costo=real if real is not None else contador,
                        costo_historial=real, costo_contador=contador)
    print(json.dumps({"estimado": est, "real_historial": real, "real_contador": contador}))


if __name__ == "__main__":
    main()
