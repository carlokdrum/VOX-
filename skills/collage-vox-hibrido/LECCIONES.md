# Lecciones aprendidas

Formato: `- [fecha] [área] lección → regla nueva`

## Proyecto 1: El viernes que desapareció (Samoa)

- [2026-10-29] [estilo] La primera prueba con fondo azul liso y texto vectorial no gustó → siempre periódico, revista, recortes y semitonos.
- [2026-10-29] [estilo] Analicé la referencia como blanco y negro, pero era a todo color → revisar la hoja de cuadros antes de definir la paleta.
- [2026-10-29] [estilo] Los recortes pequeños en los bordes no lucen → recortes grandes, del 30 al 90 % del alto, solapados.
- [2026-10-29] [estilo] Una hoja de calendario vacía "no dice nada" → el elemento principal siempre lleva la información (mes, año, número, día).
- [2026-10-29] [estilo] Al usuario le encanta el fuego real sobre papel y el "2011" dentro del agujero quemado → repetir la idea de física real con texto integrado en cada bloque.
- [2026-10-29] [estilo] El usuario quiere un híbrido: stop motion a saltos en los recortes, cámara fluida y cinematográfica, textos en hyper motion integrados (no karaoke).
- [2026-10-29] [prompts] Soul Cinema escribe mal los textos → los textos exactos se hacen en ChatGPT, con un prompt que fije medidas y proporción para no tener que recortar.
- [2026-10-29] [prompts] "Familia durmiendo" y "familia samoana" dispararon el filtro NSFW → usar "adults standing in a row, fully clothed".
- [2026-10-29] [créditos] El usuario quiere ahorrar al máximo → plan Ahorro (IA de video solo en 2–3 momentos, Kling Pro en vez de Seedance, reutilizar clips pagados).
- [2026-10-29] [créditos] Estimé 30 créditos para Seedance y eran 70 → nunca estimar sin `get_cost: true`.
- [2026-10-29] [montaje] Un `putalpha` sobre una capa compartida la fue borrando cuadro a cuadro → siempre `layer.copy()`.
- [2026-10-29] [montaje] Al imprimir sobre un clip ya generado, el papel que se enrosca muestra la cuadrícula original → aceptarlo y taparlo con fuego o humo, o generar el clip con la imagen ya impresa si el usuario paga.
- [2026-10-29] [flujo] El usuario exige confirmación antes de cada acción → pedir permiso y dar el costo exacto antes de generar.
- [2026-10-29] [flujo] El usuario se confundió al ver la capa base de IA sin montar → explicar que la IA es solo una capa y mostrar el bloque terminado.
