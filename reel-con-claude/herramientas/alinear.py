"""Paso 6: alineación por carácter → palabras → subtítulos y cortes de bloque.

Entra: reel/alineacion.json, reel/guion.txt (una frase por bloque, en orden).
Sale:  reel/subtitulos.srt, reel/tiempos.json
"""
import sys

from comun import REEL, a_cuadros, escribir_json, leer_json

COLA = 0.8


def palabras(al):
    res, actual, desde, hasta = [], "", None, None
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"],
                        al["character_end_times_seconds"]):
        if ch.isspace():
            if actual:
                res.append({"texto": actual, "desde": desde, "hasta": hasta})
            actual, desde = "", None
            continue
        if not actual:
            desde = a
        actual += ch
        hasta = b
    if actual:
        res.append({"texto": actual, "desde": desde, "hasta": hasta})
    return res


def srt_t(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def main():
    al = leer_json(REEL / "alineacion.json")
    if not al:
        sys.exit("Falta reel/alineacion.json (paso 5)")
    frases = [l.strip() for l in (REEL / "guion.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    pals = palabras(al)
    total_esperado = sum(len(f.split()) for f in frases)
    if total_esperado != len(pals):
        sys.exit(f"La voz tiene {len(pals)} palabras y el guion {total_esperado}: no coinciden")

    # Subtítulos: grupos de hasta 3 palabras, sin cruzar bloques.
    lineas, i = [], 0
    inicios = []
    for frase in frases:
        n = len(frase.split())
        bloque = pals[i:i + n]
        inicios.append(bloque[0]["desde"])
        for j in range(0, n, 3):
            g = bloque[j:j + 3]
            lineas.append((g[0]["desde"], g[-1]["hasta"], " ".join(p["texto"] for p in g)))
        i += n
    srt = []
    for k, (a, b, t) in enumerate(lineas, 1):
        srt.append(f"{k}\n{srt_t(a)} --> {srt_t(b)}\n{t}\n")
    (REEL / "subtitulos.srt").write_text("\n".join(srt), encoding="utf-8")

    total = a_cuadros(pals[-1]["hasta"] + COLA)
    cortes = [0.0] + [a_cuadros(x) for x in inicios[1:]] + [total]
    bloques = [{"bloque": n + 1, "desde": cortes[n], "hasta": cortes[n + 1],
                "dur": round(cortes[n + 1] - cortes[n], 4)} for n in range(len(frases))]
    escribir_json(REEL / "tiempos.json", {"total": total, "audio": pals[-1]["hasta"],
                                          "bloques": bloques, "palabras": pals})
    for b in bloques:
        print(f"bloque {b['bloque']}: {b['desde']:.2f}–{b['hasta']:.2f} ({b['dur']:.2f}s)")
    print(f"total {total:.2f}s")


if __name__ == "__main__":
    main()
