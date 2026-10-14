"""Paso 7: arma reel/final/reel.mp4 con ffmpeg.

Entra: reel/tiempos.json, reel/clips.json, reel/voz.mp3, reel/subtitulos.srt, ficha.md
Opcional: reel/pagina.png (inserto del bloque 6, página real del producto).
Un bloque sin clip ni inserto se cubre alargando el tramo anterior.
"""
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

from comun import FPS, RAIZ, REEL, escribir_json, leer_json

FINAL = REEL / "final"
TRAMOS = FINAL / "tramos"
ESTILO = ("FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,"
          "BorderStyle=3,Alignment=2,MarginV=62")
RETRASO_TARJETA = 0.5


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, args)], check=True)


def ficha():
    datos = {}
    for linea in (RAIZ / "ficha.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"-\s*([^:]+):\s*(.+)", linea)
        if m:
            datos[m.group(1).strip().lower()] = m.group(2).strip()
    return datos


def fuente(tam):
    for nombre in ["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   "arialbd.ttf", "Arial Bold.ttf"]:
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def envolver(draw, texto, f, ancho):
    lineas, actual = [], ""
    for p in texto.split():
        prueba = f"{actual} {p}".strip()
        if draw.textlength(prueba, font=f) <= ancho:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def tarjeta(destino):
    d = ficha()
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 90, 560, 990, 1180  # dentro de zonas seguras
    dr.rounded_rectangle((x0, y0, x1, y1), 40, fill=(255, 255, 255, 235))
    y = y0 + 50
    for texto, tam, color in [(d.get("qué es", "").split(",")[0], 64, (20, 20, 20)),
                              (d.get("formato", ""), 40, (90, 90, 90)),
                              ("" if d.get("precio en video", "sí").lower().startswith("no") else d.get("precio", ""), 110, (200, 40, 40)),
                              ("Enlace abajo", 44, (20, 20, 20))]:
        f = fuente(tam)
        for l in envolver(dr, texto, f, x1 - x0 - 80)[:2]:
            w = dr.textlength(l, font=f)
            dr.text(((1080 - w) / 2, y), l, font=f, fill=color)
            y += int(tam * 1.2)
        y += 20
    img.save(destino)


def tramo_clip(clip, dur, salida):
    inicio = float(clip.get("inicio", 0))
    disponible = clip["duracion"] - inicio
    factor = 1.0
    if disponible < dur:
        factor = dur / disponible
        if factor > 2.0:
            sys.exit(f"El clip {clip['archivo']} es muy corto para {dur:.2f}s aun a 0,5×: elegí otro")
    if clip["alto"] >= 1920:
        escala = "scale=-2:1920,crop=1080:1920"
    else:
        escala = ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920")
    vf = f"setpts={factor:.4f}*PTS,{escala},setsar=1,fps={FPS}"
    ff("-ss", inicio, "-t", dur / factor + 0.1, "-i", RAIZ / clip["archivo"], "-vf", vf,
       "-t", dur, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", 20, "-pix_fmt", "yuv420p",
       salida)


def tramo_pagina(png, dur, salida):
    cuadros = round(dur * FPS)
    vf = ("scale=1080:1920:force_original_aspect_ratio=decrease,"
          "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=white,"
          f"zoompan=z='min(zoom+0.0008,1.08)':d={cuadros}:s=1080x1920,fps={FPS},setsar=1")
    ff("-loop", 1, "-i", png, "-t", dur, "-vf", vf, "-c:v", "libx264", "-preset", "fast",
       "-crf", 20, "-pix_fmt", "yuv420p", salida)


def main():
    t = leer_json(REEL / "tiempos.json")
    clips = leer_json(REEL / "clips.json")
    if not t or not clips:
        sys.exit("Faltan reel/tiempos.json o reel/clips.json")
    TRAMOS.mkdir(parents=True, exist_ok=True)
    pagina = REEL / "pagina.png"

    # Visual por bloque: lista de (tipo, fuente, dur).
    plan = []
    for b in t["bloques"]:
        propios = [c for c in clips if c["escena"] == str(b["bloque"])]
        if b["bloque"] == 6 and pagina.exists():
            plan.append({"tipo": "pagina", "dur": b["dur"], "bloque": 6})
        elif propios:
            # Partes iguales en cuadros enteros.
            cuadros = round(b["dur"] * FPS)
            partes = [cuadros // len(propios)] * len(propios)
            partes[-1] += cuadros - sum(partes)
            for c, q in zip(propios, partes):
                plan.append({"tipo": "clip", "clip": c, "dur": q / FPS, "bloque": b["bloque"]})
        elif plan:
            plan[-1]["dur"] += b["dur"]
        else:
            sys.exit(f"El bloque {b['bloque']} no tiene clip y es el primero")

    lista = []
    for n, p in enumerate(plan):
        salida = TRAMOS / f"tramo_{n:02}.mp4"
        if p["tipo"] == "pagina":
            tramo_pagina(pagina, p["dur"], salida)
        else:
            tramo_clip(p["clip"], p["dur"], salida)
        lista.append(f"file '{salida.as_posix()}'")
    (TRAMOS / "lista.txt").write_text("\n".join(lista) + "\n", encoding="utf-8")
    ff("-f", "concat", "-safe", 0, "-i", TRAMOS / "lista.txt", "-c", "copy", TRAMOS / "video.mp4")

    tarjeta(TRAMOS / "tarjeta.png")
    desde_tarjeta = t["bloques"][-1]["desde"] + RETRASO_TARJETA
    srt = (REEL / "subtitulos.srt").as_posix().replace(":", r"\:")
    filtro = (f"[0:v][1:v]overlay=0:0:enable='gte(t,{desde_tarjeta:.3f})'[v1];"
              f"[v1]subtitles='{srt}':force_style='{ESTILO}'[v]")
    FINAL.mkdir(parents=True, exist_ok=True)
    ff("-i", TRAMOS / "video.mp4", "-loop", 1, "-i", TRAMOS / "tarjeta.png", "-i", REEL / "voz.mp3",
       "-filter_complex", filtro, "-map", "[v]", "-map", "2:a",
       "-af", f"apad=whole_dur={t['total']:.3f}", "-t", t["total"],
       "-c:v", "libx264", "-preset", "medium", "-crf", 20, "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", FINAL / "reel.mp4")
    escribir_json(FINAL / "plan.json", [{k: (v["archivo"] if k == "clip" else v) for k, v in p.items()}
                                        for p in plan])
    print(f"listo: {FINAL / 'reel.mp4'}")


if __name__ == "__main__":
    main()
