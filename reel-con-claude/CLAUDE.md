# Este proyecto: un reel de anuncio para un infoproducto

Acá se arma un video vertical corto (25–40 segundos) para anunciar un producto digital: clips de video reales de un banco de stock, una voz sintética que lee un guion, subtítulos y una tarjeta con el precio al final. La persona que te habla probablemente no sabe de video ni de programación, y no tiene por qué saber. Vos hacés el trabajo; ella decide.

## Cómo trabajar acá
- El procedimiento completo está en `.claude/skills/reel-clips/SKILL.md`. Leelo antes de empezar y seguilo paso por paso. No inventes otro camino.
- Hablá en español, de vos, simple. Sin siglas ni jerga técnica salvo que te la pregunten. Si algo falla, decí qué pasó en una frase y qué proponés, no un informe.
- Avanzá de a un paso y frená donde la skill dice que hay que preguntar: después de proponer el guion, después de mostrar los clips candidatos, y antes de cualquier cosa que cueste plata.
- Cuando tengas que preguntar, proponé una respuesta. "Elegí estos clips, ¿va?" es mejor que "¿cuáles querés?".
- Todo queda dentro de esta carpeta. No toques nada afuera.

## Lo que no se negocia
1. **Nada que cueste plata sin un tope dicho por la persona.** Antes de la voz, decí cuánto estimás y esperá el número. Si no hay tope, no se envía.
2. **Las claves viven en `.env`.** Nunca las pidas en el chat, nunca las muestres, nunca las copies a otro archivo. Si falta una, decí cuál falta y dónde se consigue.
3. **El video dice solo lo que está en `ficha.md`.** Sin testimonios, sin "últimos cupos", sin promesas de resultado. Si la persona te pide una de esas cosas, explicá en una línea por qué no y seguí.
4. **Clips de video reales, nunca un collage de imágenes.** Al menos 4 clips distintos. Si el banco de stock no tiene nada que sirva para una escena, decilo y proponé que la grabe con el teléfono (10 segundos, vertical).
5. **Sin caras de chicos reconocibles.** Manos, planos cerrados, de espaldas.
6. **Sin cartel de "hecho con IA" adentro del video.** La plataforma lo etiqueta sola al subir.
7. **Lo que no sabés es "desconocido", no cero.** Un costo que no pudiste leer se anota como `null`.

## Dónde está cada cosa
- `ficha.md`: lo que el producto tiene de verdad. Es la única fuente para el guion.
- `guion.md`: 7 frases cortas. Lo proponés vos desde la ficha; lo aprueba la persona.
- `.env`: claves. Pixabay (clips, gratis) y ElevenLabs (voz, centavos).
- `reel/`: todo lo que se va generando (escenas, candidatos, clips, voz, final).
- `reel/registro.json`: cada pedido a un servicio externo, gratuito o pago, con su costo real.
- `reel/final/reel.mp4`: el resultado. Solo se entrega si pasó la verificación de la skill.

## Qué entregar al final
La tira de 8 fotogramas (`reel/final/hoja_fotogramas.jpg`, mostrala), la ruta del mp4, los clips usados con autor y licencia, cuánto costó la voz de verdad, y qué quedó pendiente (por ejemplo, una página real del producto para la escena de "prueba"). Nada más.
