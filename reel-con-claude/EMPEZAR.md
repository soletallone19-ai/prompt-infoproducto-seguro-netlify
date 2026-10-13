# Para empezar

Antes de pegar nada, tres cosas:

1. Abrí Claude Code parado en esta carpeta (o la app de escritorio con esta carpeta conectada).
2. Copiá `.env.ejemplo` como `.env` y pegá tus claves de Pixabay y ElevenLabs.
3. Completá `ficha.md` con tu producto.

Después editá lo que está entre corchetes y pegá esto:

```
Leé CLAUDE.md y la skill reel-clips, y arrancamos.

Vendo [qué, en una frase: "un curso en PDF de pan casero para gente que nunca hizo pan"]. La ficha está en ficha.md.

Quiero llegar hasta tener los clips elegidos y bajados. La voz la hacemos después, cuando te dé el tope.

Antes de nada fijate que esté todo (Python, ffmpeg, las claves en .env, la ficha completa) y decímelo en una línea cada uno. Si falta algo, decime cómo lo consigo; no instales nada sin avisar.

Después proponeme el guion de 7 frases desde la ficha y esperá mi ok.
```

## Lo que viene después (lo escribís vos, como hablás)

Cuando te muestre el guion:
```
dale, va bien
```
o
```
cambiá la frase 3 por "..." y sacá lo de X, que no está en la ficha
```

Cuando te muestre los clips candidatos (va a proponer una elección):
```
dale, va tu propuesta
```
o
```
el del bloque 3 no me gusta, buscá de nuevo con otras palabras
```

Para la voz (acá se gasta, poco):
```
dale, seguimos. tope [600] créditos. proponeme una voz neutra latinoamericana y después armá el video entero
```

Si la verificación falla, no te va a entregar el video: te dice qué falta. Si pasa, te muestra una tira de 8 fotos y la ruta del mp4.

## Si se traba
- Dice que no ve la carpeta o la ficha → no conectaste la carpeta. Cerrá el chat, conectala y volvé a pegar.
- Dice que no llega a pixabay.com (error de red o 403) → estás en la app de escritorio, cuya red está filtrada. Hacé lo mismo en Claude Code abierto en la carpeta.
- Te pide una clave en el chat → no se la des. "Está en .env, leela de ahí."
- Propone imágenes en vez de clips, inventa un testimonio o quiere gastar sin tope → "Leé CLAUDE.md de nuevo."
