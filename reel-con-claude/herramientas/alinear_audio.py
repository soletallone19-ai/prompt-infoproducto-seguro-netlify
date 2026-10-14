"""Paso 5 alternativo: arma reel/alineacion.json para una voz SIN marcas de tiempo
(grabada con el celular o bajada de la web de ElevenLabs).

Uso: python herramientas/alinear_audio.py [reel/voz.mp3]

Detecta las pausas con ffmpeg, elige las que separan las frases de reel/guion.txt
(las que mejor coinciden con un ritmo parejo) y reparte cada frase por letras.
Es aproximado: alcanza para subtítulos de 3 palabras y cortes de bloque.
"""
import re
import subprocess
import sys
from itertools import combinations

from comun import REEL, escribir_json


def pausas(audio, minimo):
    err = subprocess.run(["ffmpeg", "-i", str(audio), "-af",
                          f"silencedetect=noise=-35dB:d={minimo}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
    fin = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    return list(zip(ini, fin))


def main():
    audio = REEL / "voz.mp3" if len(sys.argv) < 2 else sys.argv[1]
    frases = [l.strip() for l in (REEL / "guion.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    ps = pausas(audio, 0.25)
    inicio = 0.0
    if ps and ps[0][0] < 0.05:
        inicio = ps.pop(0)[1]
    fin = ps.pop()[0] if ps and ps[-1][1] > 0 else None
    if fin is None:
        sys.exit("No encontré el final de la voz")
    necesarias = len(frases) - 1
    if len(ps) < necesarias:
        sys.exit(f"Encontré {len(ps)} pausas y necesito {necesarias}: grabala con una pausa entre frases")

    # Elegir las pausas que mejor encajan con un ritmo parejo de letras por segundo.
    largos = [len(f) for f in frases]
    total = sum(largos)
    esperados, acum = [], 0
    for l in largos[:-1]:
        acum += l
        esperados.append(inicio + (fin - inicio) * acum / total)
    mejor = min(combinations(range(len(ps)), necesarias),
                key=lambda c: sum(abs((ps[i][0] + ps[i][1]) / 2 - e) for i, e in zip(c, esperados)))
    tramos = [inicio] + [x for i in mejor for x in ps[i]] + [fin]
    tramos = list(zip(tramos[0::2], tramos[1::2]))

    ch, ini, fn = [], [], []
    for k, (frase, (a, b)) in enumerate(zip(frases, tramos)):
        if k:
            ch.append(" "); ini.append(a); fn.append(a)
        paso = (b - a) / len(frase)
        for j, c in enumerate(frase):
            ch.append(c); ini.append(a + paso * j); fn.append(a + paso * (j + 1))
        print(f"frase {k + 1}: {a:.2f}–{b:.2f}  {frase}")
    escribir_json(REEL / "alineacion.json", {"characters": ch, "character_start_times_seconds": ini,
                                             "character_end_times_seconds": fn})


if __name__ == "__main__":
    main()
