"""Paso 8: verifica reel/final/reel.mp4 y arma la tira de 8 fotogramas."""
import subprocess
import sys

from PIL import Image

from comun import REEL, escribir_json, leer_json, sondear

FINAL = REEL / "final"


def main():
    mp4 = FINAL / "reel.mp4"
    if not mp4.exists():
        sys.exit("No existe reel/final/reel.mp4 (paso 7)")
    info = sondear(mp4)
    t = leer_json(REEL / "tiempos.json")
    plan = leer_json(FINAL / "plan.json", [])
    clips_dist = {p["clip"] for p in plan if p["tipo"] == "clip"}
    cobertura = sum(p["dur"] for p in plan if p["tipo"] == "clip") / info["duracion"]
    checks = {
        "1080x1920": info["ancho"] == 1080 and info["alto"] == 1920,
        "h264/aac": info["video"] == "h264" and info["audio"] == "aac",
        "duracion": abs(info["duracion"] - (t["audio"] + 0.8)) <= 1,
        "clips_distintos>=4": len(clips_dist) >= 4,
        "cobertura>=70%": cobertura >= 0.70,
    }
    fotos = []
    for i in range(8):
        seg = info["duracion"] * (i + 0.5) / 8
        destino = FINAL / "tramos" / f"f{i}.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{seg:.2f}", "-i", str(mp4),
                        "-frames:v", "1", "-vf", "scale=270:480", str(destino)], check=True)
        fotos.append(Image.open(destino))
    tira = Image.new("RGB", (270 * 8, 480), "black")
    for i, f in enumerate(fotos):
        tira.paste(f, (270 * i, 0))
    tira.save(FINAL / "hoja_fotogramas.jpg", quality=88)
    res = {"ok": all(checks.values()), "checks": checks, "info": info,
           "clips_distintos": len(clips_dist), "cobertura": round(cobertura, 3)}
    escribir_json(FINAL / "verificacion.json", res)
    for k, v in checks.items():
        print(("✓ " if v else "✗ ") + k)
    print("VERIFICACIÓN OK" if res["ok"] else "VERIFICACIÓN FALLÓ: no se entrega")
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
