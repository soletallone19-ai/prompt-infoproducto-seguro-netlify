# reel-con-claude · guía rápida

Un video vertical de anuncio para tu infoproducto, armado por tu Claude: clips reales, voz, subtítulos, precio. Vos escribís cinco líneas y contestás "dale".

## Una sola vez
1. Instalá Claude Code (o usá la app de escritorio de Claude).
2. Cuenta en **Pixabay** → clave de API (gratis). Cuenta en **ElevenLabs** → clave de API (gratis para probar).
3. Copiá `.env.ejemplo` como `.env` y pegá las dos claves.
4. Si no tenés Python o ffmpeg, Claude te dice cómo instalarlos cuando arranques.

## Cada video
1. Completá `ficha.md` (qué es, formato, qué incluye, precio, para quién).
2. Abrí Claude Code en esta carpeta y pegá el prompt de `EMPEZAR.md`.
3. Contestá: aprobás el guion, aprobás los clips, das el tope para la voz.
4. Te entrega `reel/final/reel.mp4` y una tira de 8 fotos para que lo mires antes de subirlo.

## Cuánto cuesta
Clips: nada. Voz: centavos por video (el ejemplo de la clase costó 147 créditos de ElevenLabs, unos 2 centavos de dólar). Claude no gasta nada sin que le des un tope.

## Archivos
| Archivo | Para qué |
|---|---|
| `EMPEZAR.md` | El prompt para arrancar, con los mensajes que siguen |
| `ficha.md` | Tu producto, en cinco líneas. Lo único que el video puede afirmar |
| `CLAUDE.md` | Las reglas que Claude sigue en esta carpeta. No hace falta que lo leas |
| `HABILIDAD_VIDEO.md` | Copialo a tu segundo cerebro: así tu Claude sabe guiarte desde cualquier chat |
| `.claude/skills/reel-clips/` | El procedimiento paso a paso. Lo lee Claude |
| `.env.ejemplo` | Dónde van las claves |

## Si algo no anda
Mirá "Si se traba" al final de `EMPEZAR.md`. Los dos casos de siempre: la carpeta no está conectada, o estás en la app de escritorio y su red no llega a Pixabay (usá Claude Code).
