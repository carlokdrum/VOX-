# El viernes que desapareció — explicativo estilo Vox

Video vertical (9:16, ~60 s) para TikTok sobre cómo Samoa se saltó el viernes 30 de diciembre de 2011 al cruzar la línea internacional de cambio de fecha.

**Estilo:** collage de técnica mixta (periódico, revistas, recortes con sombra y semitonos) en stop motion fluido, con elementos reales (fuego, agua) y tipografía de letras recortadas integrada en la escena.

## Estructura

| Carpeta | Contenido |
|---|---|
| `bloque1/` | Bloque 1 terminado (`bloque1-final-v4.mp4`), su hoja de cuadros y todo lo necesario para rehacerlo |
| `bloque1/assets/` | Recortes de Soul Cinema (fondo, palmeras, luna, reloj, familia, revista), calendario impreso, imagen inicial, clip de fuego de Kling 3.0 Pro y sonidos |
| `bloque1/scripts/` | `comp2.py`: montaje del collage (parallax, stop motion, letras recortadas, 2011 en el agujero, cámara). `comp-v1-plano.py`: primera versión con texto plano (descartada) |
| `voz/` | Narración de ElevenLabs con la voz AD-berto. `toma3-gancho.mp3` es la toma aprobada con ganchos |
| `clips/` | Prueba inicial con el preset Mixed Media de Higgsfield |
| `referencias/` | Hoja de cuadros del video de referencia |
| `prototipo/` | Prototipo en HTML/SVG del estilo Vox |

## Guion (voz AD-berto)

> Hay un viernes que nunca existió. Y no fue un error. En 2011, un país entero se fue a dormir un jueves… y despertó el sábado. Fue Samoa, y lo decidió su gobierno. Existe una línea invisible en el Pacífico: a un lado es HOY… al otro es MAÑANA. Samoa estaba en el lado "ayer" desde 1892, para comerciar con Estados Unidos. Pero entonces… el comercio cambió. Sus socios ahora eran Australia y Nueva Zelanda, del lado "mañana". Cuando Samoa tenía viernes, ellos ya estaban en sábado. Solo cuatro días laborables en común por semana. Así que movieron el país al otro lado de la línea. A medianoche del 29 de diciembre, saltaron directo al 31. Y por eso, un jueves, un país entero se fue a dormir… y nunca vivió ese viernes.

## Cómo renderizar el bloque 1

Requisitos: Python 3 con `numpy` y `Pillow`, y `ffmpeg`.

Los scripts usan rutas absolutas de la sesión de trabajo original. Para ejecutarlos, cambia las variables `D` y `O` al principio de `comp2.py` para que apunten a este repositorio. Después:

```bash
python3 bloque1/scripts/comp2.py   # genera mudo.mp4 (video sin audio)
ffmpeg -i mudo.mp4 -i voz/toma3-gancho.mp3 -i bloque1/assets/sfx.wav \
  -filter_complex "[1:a]atrim=0:10.45,afade=t=out:st=10.3:d=0.15[v];[2:a]volume=0.55[s];[v][s]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v libx264 -crf 21 -c:a aac -shortest bloque1.mp4
```

## Plan de producción (plan Ahorro, ~25 créditos)

1. **Gancho** — calendario que arde con fuego real (hecho).
2. **Samoa** — costa con oleaje real y noche en el fale.
3. **La línea** — globo de papel y línea de luz que divide HOY y MAÑANA.
4. **Comercio** — velero, grúas y avión con estela.
5. **El salto** — reloj a medianoche; el 30 se desintegra en ceniza real.
6. **Cierre** — pull back largo a negro y frase final en círculo.
