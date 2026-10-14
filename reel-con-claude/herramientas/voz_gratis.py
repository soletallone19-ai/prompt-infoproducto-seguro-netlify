"""Paso 5 alternativo (GRATIS): voz con voces de Microsoft vía edge-tts.

No necesita cuenta ni clave. Es un servicio no oficial: si deja de andar, usar voz.py.
Instalar una vez: pip install edge-tts

Uso:
  python herramientas/voz_gratis.py voces              lista voces en español
  python herramientas/voz_gratis.py generar [voz]      por defecto es-AR-ElenaNeural

Entra reel/guion.txt y sale lo mismo que voz.py (reel/voz.mp3 y reel/alineacion.json),
así que alinear.py, armar.py y verificar.py funcionan igual.
"""
import asyncio
import sys

from comun import REEL, escribir_json, registrar

VOZ = "es-AR-ElenaNeural"
LIMPIAR = ".,;:!?¡¿\"'()…"


def importar():
    try:
        import edge_tts
        return edge_tts
    except ImportError:
        sys.exit("Falta edge-tts. Instalalo con: pip install edge-tts")


def a_caracteres(guion, tiempos):
    """Convierte tiempos por palabra al formato por carácter que usa alinear.py."""
    pals = guion.split()
    if len(pals) != len(tiempos):
        sys.exit(f"La voz devolvió {len(tiempos)} palabras y el guion tiene {len(pals)}. "
                 "Escribí los números con letras (\"nueve\", no \"9\") y probá de nuevo.")
    ch, ini, fin = [], [], []
    for k, (p, (a, b)) in enumerate(zip(pals, tiempos)):
        if k:
            ch.append(" ")
            ini.append(a)
            fin.append(a)
        paso = (b - a) / len(p)
        for j, c in enumerate(p):
            ch.append(c)
            ini.append(a + paso * j)
            fin.append(a + paso * (j + 1))
    return {"characters": ch, "character_start_times_seconds": ini,
            "character_end_times_seconds": fin}


async def generar(voz):
    edge_tts = importar()
    ruta = REEL / "guion.txt"
    if not ruta.exists():
        sys.exit("Falta reel/guion.txt (una frase por línea)")
    guion = " ".join(l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip())
    com = edge_tts.Communicate(guion, voz, boundary="WordBoundary")
    audio, tiempos = bytearray(), []
    async for parte in com.stream():
        if parte["type"] == "audio":
            audio += parte["data"]
        elif parte["type"] == "WordBoundary":
            if not parte["text"].strip(LIMPIAR):
                continue
            a = parte["offset"] / 1e7
            tiempos.append((a, a + parte["duration"] / 1e7))
    (REEL / "voz.mp3").write_bytes(bytes(audio))
    escribir_json(REEL / "alineacion.json", a_caracteres(guion, tiempos))
    registrar("edge-tts", f"voz {voz}", "ok", costo=0)
    print(f"listo: reel/voz.mp3 ({len(tiempos)} palabras, voz {voz})")


async def voces():
    edge_tts = importar()
    for v in await edge_tts.list_voices():
        if v["Locale"].startswith("es-"):
            print(v["ShortName"], v["Gender"])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "voces":
        asyncio.run(voces())
    elif cmd == "generar":
        asyncio.run(generar(sys.argv[2] if len(sys.argv) > 2 else VOZ))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
