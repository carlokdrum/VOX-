---
name: collage-vox-hibrido
description: Produce explicativos verticales estilo Vox en collage de periódico y revista con stop motion fluido, elementos reales (fuego, agua) y letras recortadas, gastando el mínimo de créditos de Higgsfield. Aprende de cada proyecto.
---

# Collage Vox híbrido (autodidacta)

Video vertical 9:16 (~60 s, 6 bloques de 10 s) para TikTok o Reels. Estilo: collage físico de papel (periódico, revista, kraft, cinta, semitonos) animado en stop motion fluido, con **física real generada por IA** solo donde impacta (fuego, agua, ceniza, humo) y **tipografía de letras recortadas integrada en la escena**. Todo lo demás se hace por código, gratis.

## 0. Antes de empezar: aprende de proyectos anteriores

1. Lee `LECCIONES.md` (junto a este SKILL.md, o en el repo del usuario). Aplica cada lección.
2. Lee las preferencias del usuario. Si exige confirmación antes de actuar, **pide permiso antes de cada generación paga, búsqueda o lectura de archivos**, y di el costo exacto (`get_cost: true`) antes de gastar.

## 1. Guion y voz

- Guion de ~55 s con gancho en los primeros 3 s, re-gancho hacia el segundo 25 y un final que conecte en loop con el inicio. Verifica los datos con búsqueda.
- Voz en ElevenLabs con `eleven_v4` y etiquetas de audio (`[curious]`, `[dramatically]`, `[short pause]`, `[long pause]`, `[slowly]`), con MAYÚSCULAS para el énfasis. Pide **una sola toma** si el usuario quiere ahorrar.
- Corta los bloques con `ffmpeg silencedetect=n=-35dB:d=0.25`. Las pausas marcan dónde golpea cada texto o efecto.

## 2. Plan de créditos (plan Ahorro por defecto)

| Recurso | Herramienta | Costo aprox. |
|---|---|---|
| Recortes y texturas | Higgsfield `soul_cinematic`, 2K (sale a 1080×2048) | 0,12 por imagen |
| Física real (fuego, agua, ceniza) | Higgsfield `kling3_0` modo `pro`, `sound: off`, `start_image` | 15 por 10 s (std: 12,5) |
| Alternativa premium | `seedance_2_5` | 70 por 10 s, solo para planos críticos |
| Texto exacto (calendarios, carteles) | ChatGPT (gratis para el usuario) o `gpt_image_2_5` | — |
| Cámara, stop motion, letras, sonidos y mezcla | Código (Python + PIL + numpy + ffmpeg) | 0 |

Reglas: IA de video solo en 2–3 momentos del video total. **Reutiliza clips ya pagados** y quítales el fondo con una llave de color. Usa clips de 5 s y estíralos con la cámara por código. Si Higgsfield intercepta con una recomendación de preset, reenvía con `declined_preset_id`.

## 3. Generar recortes que se puedan llavear

- **Elementos sueltos** (personajes, palmeras, luna, reloj): `"Paper cutout of a vintage halftone printed color photograph of …, cut out with scissors with a thin white paper border following the silhouette, isolated on a solid pure chroma green background, flat lighting, sharp edges"`.
- **Fondo:** `"Flat top-down macro photograph of a dense handmade paper collage background: overlapping aged yellowed newspaper pages with dense columns of tiny print and halftone photos, crumpled kraft paper, torn magazine strips in cobalt blue and burnt orange, masking tape, coffee stains, nothing in the center"`.
- **Banco de letras:** `"grid of many torn glossy magazine and newspaper scraps of different solid colors and printed textures… no readable text"`. De aquí salen los papeles de las letras recortadas.
- **Elemento principal que arderá o se moverá con IA:** sobre **azul cobalto liso (#0A3CDC)**, para quitar el fondo después junto con el fuego.
- **Filtro NSFW falso:** palabras como "familia" o "durmiendo de noche" lo disparan. Usa "adults standing in a row, fully clothed, wearing …", sin niños ni camas.
- **Texto exacto:** nunca con Soul Cinema, porque escribe mal. Pide al usuario que lo haga en ChatGPT con un prompt que fije las medidas: "1024×1536, page fills FULL HEIGHT, exactly N px wide and centered, flat front-facing scan, no perspective, no shadow, sides solid cobalt blue". Luego recorta automáticamente por columnas no azules y escala a la medida de la hoja en el clip.

## 4. Clip de física real (Kling 3.0 Pro)

Estructura del prompt: ESTILO → tramos de tiempo (0–3 s / 3 s / 3–7 s / 7–10 s) → CÁMARA → AVOID.
Ejemplo base: `"Mixed media paper collage animation. The grayscale cutout hand holds the cream paper calendar page on the flat cobalt blue background, slight stop-motion paper jitter. Fast camera crash zoom toward the page. The hand tears the page off with a snappy jerk; the torn edge catches fire and real photorealistic flames spread across the flat paper cutout, the paper curls, blackens and glows orange at the edges, embers and smoke rise. The camera keeps pushing forward and flies straight through the burning hole in the paper into darkness lit by fire. Static flat paper cutouts contrasted with realistic fire physics. No text, no letters, no numbers."`

Al descargarlo, mide dónde está el elemento con una máscara de color (crema: `r>175, g>165, b>120, r-b<70`) para saber dónde imprimir encima.

## 5. Montaje por código (el motor, ver `scripts/comp2.py`)

Lienzo de 1080×1920 a 24 fps, con salida por tubería a `ffmpeg libx264 -preset veryfast`.

1. **Llaves de color.** Verde: `g>r+30 & g>b+30`, erosión `MinFilter(3)` y despill limitando G a `max(R,B)+10`. Azul del clip: `alpha = 1 - clip(((b - max(r,g)) - 40)/50)`, con despill de B a `max(R,G)+5` para quitar el borde violeta.
2. **Sombra de papel en cada recorte:** copia negra desplazada (9, 12) px y desenfocada 7 px, al 55 % de opacidad.
3. **Capas con parallax 2.5D:** fondo con profundidad 0,55, recortes del medio 0,8, elemento principal 1,0 y texto 0,35. `zoom_capa = 1 + (zoom - 1) * profundidad`.
4. **Stop motion fluido:** el tiempo de los recortes se cuantiza a 12 fps (`floor(t*12)/12`), con temblor aleatorio de ±4 px y ±1,2° por paso. La cámara va fluida a 24 fps. El clip de IA va en pasos de dos cuadros antes del evento físico y fluido después.
5. **Cámara:** crash zoom de entrada (1,5 → 1,0 en 0,45 s), empuje lento, impacto con overshoot (`ease_back`) y temblor amortiguado en cada golpe de la voz, dolly con giro lento y atravesar al final (el zoom sube a ~3). Motion blur mezclando el cuadro anterior al 45 % solo en los movimientos rápidos.
6. **Tamaño de los recortes:** **grandes**, del 30 al 90 % del alto del cuadro, solapados entre sí y con la hoja principal. Nunca pequeños en los bordes.
7. **Impresión sobre papel que arde:** diseña el impreso o usa la foto de ChatGPT y aplícalo solo donde el clip tiene papel crema (máscara de color). Multiplica por la luminancia del original (`shade = lum/225`) para que herede las sombras. Así se quema solo cuando llegan las llamas.
8. **Texto dentro del agujero:** compone el texto y muéstralo solo donde la luminancia es menor de 90, de modo que aparece en el hueco quemado, detrás de las llamas. Con parpadeo `0.9 + 0.1*sin(t*31)`.
9. **Letras recortadas (no karaoke):** cada letra va en un pedazo aleatorio del banco de revista, con polígono de tijera irregular, tipografía y tinta aleatorias que contrasten con el papel, grano, sombra y rotación de ±9°. Entran de una en una en stop motion (`drop` o `slam`) y al salir se las lleva el aire caliente: suben, giran, se oscurecen hacia naranja y se desvanecen. Ajusta cada palabra con `maxw` para que nunca se corte, y saca del espacio de cámara los textos que aparecen con zoom alto.
10. **El fuego afecta al collage:** el periódico se chamusca con una elipse oscura que crece, los recortes suben con el aire caliente y se tiñen de naranja, y la luz cálida se derrama por la imagen.
11. **Sonidos sintetizados con numpy:** whoosh (ruido filtrado con envolvente), golpe de bajo (seno con barrido de frecuencia), papel rasgado (ruido entrecortado), ignición y cama de chisporroteo. Mezcla con `amix normalize=0`, la voz al 100 %, los efectos al 55 % y `alimiter 0.95`.

## 6. Verificación obligatoria

Después de cada render: hoja de cuadros con `ffmpeg -vf "fps=1.5,scale=160:-1,tile=8x2"`, y léela. Revisa:
- que ninguna palabra quede cortada y que la ortografía y las fechas sean correctas;
- que el elemento principal se entienda solo (un calendario debe parecer un calendario y decir algo);
- que los recortes sean grandes y llenen el cuadro;
- que no haya fondo liso, texto vectorial, bordes violetas ni cuadrícula fantasma;
- que no haya fallos de alfa compuesto. **Copia siempre la capa antes de cambiarle el alfa** (`layer.copy()`): un `putalpha` sobre el objeto compartido lo va borrando cuadro a cuadro.

## 7. Errores que ya cometimos (no repetir)

- Confundir la referencia con blanco y negro: **analiza la hoja de cuadros con cuidado**, porque el color suele ser saturado.
- Pasar de collage a diseño plano: fondo azul liso y texto vectorial **no** es estilo Vox. Siempre debe haber periódico, revista, recortes y semitonos.
- Estimar créditos sin `get_cost`. Seedance cuesta 70, no 30.
- Una hoja de calendario vacía no comunica: el elemento principal debe llevar la información (mes, año, número, día).
- Generar sin preguntar cuando el usuario exige confirmación.

## 8. Autoaprendizaje (al cerrar cada bloque o proyecto)

1. Pregunta al usuario qué le gustó y qué no.
2. Añade a `LECCIONES.md` una línea por lección con este formato: `- [fecha] [área: prompts|créditos|montaje|estilo|flujo] lección → regla nueva`.
3. Si una lección contradice este SKILL.md, propón una mejora del skill con `propose_skills` (de tipo improvement), con el SKILL.md completo actualizado, e incluye la lección en la sección 7.
4. Guarda los scripts nuevos o mejorados en `scripts/` y súbelos al repositorio del proyecto si existe.
