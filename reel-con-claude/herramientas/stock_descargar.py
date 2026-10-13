"""Paso 4: baja solo los clips de reel/elegidos.json y escribe reel/clips.json.

elegidos.json: { "<escena>": [ {"id": n, "inicio": seg, "motivo": "..."} ] }
Para un clip propio: {"id": "propio1", "origen": "propio", "archivo": "ruta/al.mp4", "inicio": 0}
"""
import shutil
import sys
from pathlib import Path

from comun import RAIZ, REEL, bajar, escribir_json, leer_json, registrar, sha256, sondear

LICENCIAS = {"pixabay": "Pixabay Content License", "pexels": "Pexels License"}


def main():
    elegidos = leer_json(REEL / "elegidos.json")
    candidatos = leer_json(REEL / "candidatos" / "candidatos.json", {})
    if not elegidos:
        sys.exit("Falta reel/elegidos.json")
    clips = []
    for escena, lista in elegidos.items():
        for e in lista:
            if e.get("origen") == "propio":
                origen = Path(e["archivo"])
                origen = origen if origen.is_absolute() else RAIZ / origen
                destino = REEL / "clips" / f"{escena}_propio_{e['id']}.mp4"
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(origen, destino)
                meta = {"origen": "propio", "autor": "propio", "licencia": "propia", "pagina": None}
            else:
                c = next((c for c in candidatos.get(str(escena), []) if c["id"] == e["id"]), None)
                if not c:
                    sys.exit(f"El clip {e['id']} no está entre los candidatos de la escena {escena}")
                destino = REEL / "clips" / f"{escena}_{c['proveedor']}_{c['id']}.mp4"
                if not destino.exists():
                    n = registrar(c["proveedor"], f"descargar {c['id']}", "enviando", costo=0)
                    bajar(c["archivo"], destino)
                    registrar(c["proveedor"], f"descargar {c['id']}", "ok", costo=0, ref=n)
                meta = {"origen": c["proveedor"], "autor": c["autor"],
                        "licencia": LICENCIAS[c["proveedor"]], "pagina": c["pagina"]}
            info = sondear(destino)
            clips.append({"escena": str(escena), "id": e["id"], "inicio": e.get("inicio", 0),
                          "motivo": e.get("motivo"), "archivo": str(destino.relative_to(RAIZ)),
                          "sha256": sha256(destino), **meta, **info})
            print(f"escena {escena}: {destino.name} {info['ancho']}x{info['alto']} {info['duracion']:.1f}s")
    escribir_json(REEL / "clips.json", clips)


if __name__ == "__main__":
    main()
