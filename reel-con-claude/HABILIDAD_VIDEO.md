# Habilidad: hacer un reel de anuncio con Claude

Guardá este archivo en tu segundo cerebro (la carpeta o proyecto donde tu Claude lee tus notas). Sirve para que, cuando digas "quiero un video para anunciar mi producto", tu Claude sepa qué es esto, qué hace falta y cómo guiarte, aunque vos no te acuerdes de nada.

## Qué es
Un método para que Claude arme un video vertical corto (25–40 segundos) para Meta, Instagram o TikTok, sin editar a mano:
clips de video reales de un banco gratuito + una voz sintética que lee un guion de 7 frases + subtítulos + tarjeta de precio al final.
Está pensado para infoproductos (PDF, curso, plantilla, guía) y tiene reglas fijas: dice solo lo que el producto tiene de verdad, no gasta sin que vos lo autorices, y no entrega el video si no pasa su propia verificación.

## Dónde está
Repositorio `reel-con-claude`. Adentro: `CLAUDE.md` (las reglas), `EMPEZAR.md` (el prompt para arrancar), `ficha.md` (plantilla del producto), `.env.ejemplo` (dónde van las claves) y la skill en `.claude/skills/reel-clips/`.

## Qué hace falta tener (una sola vez)
- **Claude Code** instalado, o la app de escritorio de Claude. Claude Code es más confiable para esto porque corre en tu compu sin filtros de red.
- **Python** y **ffmpeg** instalados. Si no los tenés, Claude te dice cómo.
- **Cuenta en Pixabay** (gratis) y su clave de API. Es de donde salen los clips.
- **Cuenta en ElevenLabs** (gratis para probar) y su clave. Es la voz. Un video cuesta centavos. Para usarla en anuncios pagos, revisá en su página qué plan incluye licencia comercial.
- Las dos claves pegadas en un archivo `.env` dentro de la carpeta del proyecto. Nunca en el chat.

## Qué tenés que escribir vos
1. La **ficha** del producto: qué es, formato, qué incluye con números reales, precio, para quién. Cinco líneas.
2. Un **tope** de gasto para la voz cuando Claude te lo pida (600 créditos sobra para un video; son centavos).
3. Respuestas cortas: "dale", "cambiá esto", "buscá de nuevo". Claude propone, vos decidís.

## Cómo se pide
Abrí Claude Code en la carpeta del proyecto y pegá el prompt de `EMPEZAR.md` con tu producto. Claude verifica que esté todo, propone el guion, busca clips y te los muestra, pide el tope, genera la voz, arma y verifica el video, y te entrega una tira de 8 fotos con el resultado.

## Si tu Claude está leyendo esto porque le pediste un video
Guiá a la persona en este orden, de a un paso, sin jerga:
1. Preguntale si ya tiene la carpeta `reel-con-claude`. Si no, que la baje y la abra con Claude Code.
2. Preguntale si tiene las dos claves en `.env`. Si no, decile dónde se consiguen (Pixabay: pixabay.com/api/docs, logueado; ElevenLabs: su perfil, "API keys").
3. Pedile que complete `ficha.md`. Si te cuenta el producto en el chat, armale la ficha vos y pedile que la confirme.
4. Decile que pegue el prompt de `EMPEZAR.md`. Desde ahí, la skill lleva el proceso.
No le pidas claves por chat. No le prometas que el video va a vender. No inventes nada que no esté en la ficha.

## Lo que aprendimos haciéndolo (para que no lo aprendas de nuevo)
- Un video hecho de imágenes fijas con zoom se ve a anuncio barato. Por eso son clips de video, mínimo cuatro.
- Los bancos de stock son flojos en nichos. Buscar con palabras cortas en inglés ("bread dough", no "shaping dough loaf hands") trae mejores resultados. Si para una escena no hay nada, se graba con el teléfono: 10 segundos, vertical.
- No poner cartel de "hecho con IA" adentro del video. La plataforma lo etiqueta sola.
- La voz con avatar hablando a cámara existe y la probamos: unos 6 dólares por 15 segundos. Para material educativo, los clips reales rindieron más.
