---
name: reel-clips
description: Arma un reel vertical de anuncio (9:16, 25–40 s) a partir de un guion por bloques, con clips de video reales de Pixabay o Pexels, voz sintética de ElevenLabs con marcas de tiempo, subtítulos y tarjeta de precio. Usar cuando el usuario pida un reel, un video de anuncio o "el video para Meta" de un infoproducto.
---

# reel-clips · reel automático con clips reales

Adaptado del método Hyperflujo (recetas/reel/PLAN.md, reglas D13/D24). Ejecutás cada paso con scripts propios en `herramientas/` dentro del proyecto. Nunca editás video a mano.

## Reglas que no se negocian
1. **Clips reales.** Al menos 4 clips de video distintos (stock libre o propios) que cubran ≥ 70 % de la duración. Si no se llega, no se entrega: se informa qué falta. Nunca un collage de imágenes.
2. **Tope antes de pagar.** Cada llamada que cuesta (ElevenLabs, cualquier IA) se registra antes en `registro.json` con estimado y tope autorizado por el usuario. Sin tope, no se envía. Se guarda el ID del pedido antes de esperar la respuesta; si se corta, se recupera por ID, nunca se repite a ciegas. Costo desconocido = `null`, nunca 0.
3. **Claves en `.env`.** Se leen con `os.environ` tras cargar `.env`. Nunca se imprimen, nunca se pegan en el chat, nunca se escriben en otro archivo.
4. **Solo afirmaciones de la ficha.** El guion afirma lo que `ficha.md` dice que el producto tiene. Sin testimonios, cupos, timers ni promesas de resultado. Si el usuario pide una, se le explica y no se incluye.
5. **Sin cartel "generado con IA"** dentro del video. La plataforma lo etiqueta al subir.
6. **Sin caras de menores reconocibles** en primer plano. Preferir manos, planos cerrados, de espaldas.
7. **Licencia por clip**: id, autor, URL, licencia, sha256 en `clips.json`. Clips propios: `origen: "propio"`.

## Estructura del proyecto
```
ficha.md                  qué es, formato, qué incluye (números reales), precio, público
guion.md                  7 bloques (ver paso 1)
.env                      PIXABAY_API_KEY / PEXELS_API_KEY / ELEVENLABS_API_KEY
herramientas/             scripts que vos escribís (python, stdlib + requests opcional)
reel/
  escenas.json            paso 2
  candidatos/             miniaturas jpg + candidatos.json (paso 3)
  elegidos.json           paso 4
  clips/ + clips.json     paso 4 (descargas)
  voz.mp3, alineacion.json, subtitulos.srt   pasos 5–6
  final/reel.mp4, hoja_fotogramas.jpg, verificacion.json   pasos 7–8
  registro.json           toda solicitud (gratuita o paga) con estado
```

## Pasos

### 1 · Guion por bloques
Si no hay `guion.md`, proponé uno desde `ficha.md` y pedí aprobación. Formato:
```
| # | bloque | texto | visual |
| 1 | gancho | ... | clip |
| 2 | qué es | ... | clip |
| 3 | detalle/dolor | ... | clip |
| 4 | cómo se usa | ... | clip |
| 5 | cómo se usa (2) | ... | clip |
| 6 | prueba | ... | página real del producto (inserto ≤ 3 s) |
| 7 | CTA + precio | "... [precio]. El enlace está abajo." | clip + tarjeta de precio |
```
Límites: ≤ 100 palabras, ≤ 40 s estimados (2,5 palabras/s). Tuteo neutro o "vos" según indique el usuario. Cada afirmación con su origen en la ficha, anotado debajo de la tabla.

### 2 · Palabras clave
Escribí `reel/escenas.json`: por bloque con clip, `id`, `frase`, `palabras_clave` (3–4 términos en inglés de **1–2 palabras**, concretos: "bread dough", "kneading", "child writing"; Pixabay busca por etiquetas y con frases largas devuelve basura) y `clips` (1–2). Mostralo al usuario antes de buscar.

### 3 · Buscar candidatos (gratis)
Script `herramientas/stock_buscar.py`:
- Proveedor: Pexels si hay `PEXELS_API_KEY` (`GET https://api.pexels.com/videos/search?query=&orientation=portrait&size=medium&per_page=15`, header `Authorization: <clave>`), si no Pixabay (`GET https://pixabay.com/api/videos/?key=&q=&video_type=film&safesearch=true&per_page=50`).
- Filtro: duración ≥ 3 s; archivo con alto ≥ 1920 vertical, o ≥ 1080 de alto recortable a 9:16 (ancho ≥ alto·9/16).
- De cada video, guardar la URL del archivo **más grande disponible** (en Pixabay, `videos.large`, que suele ser 4K): el recorte a 9:16 de un 4K queda en Full HD; el de un 1080p queda en 608 px de ancho y se ve blando.
- Guardar hasta 3 candidatos por escena en `candidatos.json` (id, autor, URL de página, URL del archivo, ancho, alto, duración) y bajar **solo la miniatura** a `candidatos/<escena>_<id>.jpg`.
- Respetar 100 pedidos/min (Pixabay). Cachear respuestas 24 h.
- Llevar `reel/descartados.json` con los ids que el usuario rechazó: no volver a proponerlos. Poder re-buscar solo algunas escenas sin perder las demás.
- Si una escena no consigue nada usable en dos intentos, decirlo y proponer un clip propio (10 s con el teléfono, vertical): la skill lo acepta como `origen: "propio"`.
Mostrá las miniaturas al usuario (Read) agrupadas por escena, con id, autor y una marca ✓ / ✗ con tu criterio, y **proponé una elección**: el usuario solo tiene que decir sí o cambiar alguna. Si una escena queda sin candidato usable, volvé a buscar esa escena con palabras más concretas antes de preguntar. **No bajes videos en este paso.**

### 4 · Elegir y descargar
`reel/elegidos.json`: `{ "<escena>": [ {"id": n, "inicio": seg, "motivo": "..."} ] }`. Criterios: mirar el encuadre recortado a 9:16 por el centro; `inicio` > 0 si el clip abre en negro; cada clip ≥ 1,5 s en pantalla; sin caras de menores.
Script `herramientas/stock_descargar.py`: baja solo los elegidos a `reel/clips/<escena>_<proveedor>_<id>.mp4`, calcula sha256, lee resolución/duración con `ffprobe`, escribe `clips.json` con licencia (`Pexels License` / `Pixabay Content License`) y registra cada descarga en `registro.json` como solicitud gratuita. Clips propios: copiarlos a `clips/` y registrarlos con `origen: "propio"`.

### 5 · Voz con marcas de tiempo (paga)
Antes: pedir tope al usuario (créditos = caracteres del guion × 1,2). Registrar solicitud `enviando`.
`POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128`, header `xi-api-key`, body `{"text": <guion completo>, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.2}}`.
El consumo real se lee del **historial** (`GET /v1/history`, campo `character_count_change_from/to` del ítem nuevo), no del contador de la suscripción, que tarda en actualizarse: si el contador dice 0, se registra `null` y se vuelve a consultar; nunca 0. Guardar `voz.mp3` (base64 → bytes) y `alineacion.json` (`alignment.characters`, `character_start_times_seconds`, `character_end_times_seconds`). Leer el consumo real en `GET /v1/user/subscription` (antes y después) y conciliar en `registro.json`.
Voice ID: pedírselo al usuario o listar `GET /v1/voices` y proponer una voz neutra LATAM. No clonar voces.

### 6 · Subtítulos y cortes
Script `herramientas/alinear.py`: de la alineación por carácter → palabras (`{texto, desde, hasta}`) → frases de ≤ 3 palabras → `subtitulos.srt`. Cortes de bloque: el `desde` de la primera palabra de cada bloque. Duración total = `hasta` de la última palabra + 0,8 s; a la voz se le agrega ese silencio al final (`apad`) para que el video no se corte con `-shortest`. Los cortes se redondean a **cuadros enteros** (30 fps): sin eso un tramo de 1,5 s puede quedar en 1,498 y fallar el mínimo.
Asignar clips a bloques: si un bloque tiene 2 clips, se reparten en partes iguales. Si el clip es más corto que su tramo, se ralentiza hasta 0,5×; si sigue corto, se elige otro.

### 7 · Armar con ffmpeg
Script `herramientas/armar.py` que genera y ejecuta:
1. Por tramo: `ffmpeg -ss <inicio> -t <dur> -i clip.mp4 -vf "scale=-2:1920,crop=1080:1920,setsar=1,fps=30" -an -c:v libx264 -preset fast -crf 20 tramo_N.mp4` (si el clip es más bajo que 1920, `scale=1080:-2` y `crop=1080:1920` con pad si hace falta).
2. Inserto del bloque 6 (página real): `ffmpeg -loop 1 -i pagina.png -t <dur> -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=white,zoompan=z='min(zoom+0.0008,1.08)':d=<frames>:s=1080x1920,fps=30" ...`.
3. Tarjeta de precio: PNG generado con Pillow (nombre, formato, precio, "Enlace abajo"), superpuesta con `overlay` en el último tramo desde `retraso_s`.
4. Concatenar (`concat` demuxer), agregar voz (`-i voz.mp3 -c:a aac -b:a 160k -shortest`), quemar subtítulos (`-vf "subtitles=subtitulos.srt:force_style='FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Alignment=2,MarginV=62'"`). Ojo: `FontSize` y `MarginV` de `force_style` van en unidades de libass (alto de referencia 288, no 1920): `MarginV=62` ≈ 21 % desde abajo. Zonas seguras: nada de texto en el 14 % superior ni el 20 % inferior. Probado 2026-10-09 con ffmpeg 6.1 (Linux, clips sintéticos) y 2026-10-12 de punta a punta en Windows con Claude Code: 8 clips de Pixabay, voz ElevenLabs (147 créditos reales), 25,4 s, verificación ok.
5. Salida `final/reel.mp4`: `-c:v libx264 -pix_fmt yuv420p -movflags +faststart`.

### 8 · Verificar (obligatorio)
Script `herramientas/verificar.py` → `final/verificacion.json` y `hoja_fotogramas.jpg` (8 fotogramas equiespaciados en una tira). Falla si: no es 1080×1920; códec no es h264/aac; duración ≠ audio + 0,8 ± 1 s; clips distintos < 4; cobertura de video < 70 %. Si falla, no se entrega: se informa qué falta y se vuelve al paso que corresponde.

## Entrega
Mostrar al usuario: `hoja_fotogramas.jpg` (Read), ruta del mp4, tabla de clips con autor y licencia, consumo real de voz, y lo que quedó fuera del guion por falta de evidencia. Nada más.
