# Documentación de mantenimiento — MiguelGranado/MiguelGranado

Este documento explica **cómo está armado todo este repositorio**, de dónde sale cada dato
que aparece en el perfil, y cómo tocar cada pieza sin romper nada. Está pensado para que
cualquiera (tú, otra sesión de Claude, Cursor, quien sea) pueda continuar el trabajo sin
tener que re-descubrir todo desde cero.

Última verificación completa en vivo: **2026-09-12**, sobre `main` en el commit que mergeó
el PR #18.

---

## 1. Qué es este repositorio

`MiguelGranado/MiguelGranado` es un repo especial de GitHub: como el nombre del repo es
igual al nombre de usuario, GitHub muestra automáticamente su `README.md` en la página de
perfil (`github.com/MiguelGranado`). Todo lo que hay aquí existe para eso — no es un
proyecto de software normal.

Estructura actual del repo (rama `main`):

```
README.md              ← el contenido que se ve en el perfil
dark.svg                ← tarjeta "hero" (tema oscuro), generada con scripts/hero/build_hero.py
light.svg               ← tarjeta "hero" (tema claro), generada con scripts/hero/build_hero.py
scripts/hero/
  build_hero.py         ← script que genera dark.svg y light.svg
  icons/*.svg           ← logos de Python/TypeScript/React/PostgreSQL/Azure (MIT, xandemon/developer-icons)
.github/workflows/
  snake.yml             ← Action que genera la "serpiente" que se come el grid de contribuciones
```

Rama `output` (separada de `main`, la genera el workflow automáticamente):

```
snake-dark.svg
snake-light.svg
```

**Importante:** hasta el commit de este documento, `scripts/hero/build_hero.py` y sus
iconos **no estaban en el repositorio** — solo existían en el scratchpad temporal de esta
sesión de Claude Code, que se borra al cerrar la sesión. Si alguien hubiera necesitado
regenerar `dark.svg`/`light.svg` mañana, el script ya no habría existido en ningún lado.
Se corrigió como parte de este mismo commit: ahora el script vive en `scripts/hero/` y se
verificó (`diff`) que reproduce byte-a-byte los `dark.svg`/`light.svg` ya publicados.

---

## 2. Cómo regenerar la tarjeta "hero" (dark.svg / light.svg)

```bash
cd scripts/hero
python3 build_hero.py
cp dark.svg light.svg ../../
```

Requiere Python 3 con la librería estándar únicamente (no usa Pillow ni ninguna dependencia
externa — eso cambió cuando se quitó la foto, ver sección 4).

### Estructura del script

- `ICON_FILES`: mapea nombre → ruta del SVG del logo (Python, TypeScript, React,
  PostgreSQL, Azure). Estos 5 son los únicos con icono real; el resto del stack
  (`EXTRA_STACK_TAGS`) son chips de solo texto.
- `load_icon_inner()`: limpia el `<svg>` externo de cada icono y renombra sus `id="..."`
  con un prefijo único (`ic_{nombre}_{id}`) para que no choquen entre sí al combinarlos en
  un solo documento SVG.
- `stack_chip()` / `stack_row()`: dibujan los 5 chips con icono (fila superior del STACK).
- `EXTRA_STACK_TAGS`: lista de texto plano — **copiada directamente de la sección
  "Certificazioni" de miguel.ulamander.com**. Si el portafolio cambia esa lista, hay que
  actualizar esta constante a mano.
- `text_chip_row()`: envuelve una lista de tags en chips de texto, respetando un ancho
  máximo (`max_w`), y devuelve también cuánta altura ocupó — esa altura se usa para
  recalcular dinámicamente dónde empieza todo lo de abajo (`shift` en `build()`).
- `LANG_STATS` / `lang_bar()` / `lang_legend()`: la barra de "Most Used Languages"
  (porcentajes fijos a mano — no se leen de la API de GitHub en este script; si los
  lenguajes reales cambian mucho, hay que actualizar `LANG_STATS`).
- `build(theme)`: arma el SVG completo. Los `text` con coordenadas `y_...` se calculan
  todos en cascada a partir de `shift` y de los gaps `g1..g4`, así que si agregás o quitás
  una sección, **no tocás números fijos** — solo agregás la sección en la cadena de
  cálculo de `y_*` y todo lo de abajo se re-acomoda solo.

### Layout (después de quitar la foto — PR #16, 2026-09-12)

Antes había una foto pixelada a la izquierda (`x=36..436`) y el panel de texto ocupaba
solo la mitad derecha (`x=500..1132`). Se quitó la foto por pedido explícito del usuario.
Ahora:

- `X = 60` — margen izquierdo único para todo el contenido.
- `PANEL_W = 1080` — el panel usa casi todo el ancho del canvas (1180px total).
- `VAL_X = X + 120` — columna donde arrancan los valores de CONTACT (a la derecha de sus
  labels "Grid.Portfolio", etc.).

Esto también significa que `generate_pixel_portrait.py` (el script que generaba los puntos
del retrato) **ya no se usa** — quedó en el scratchpad de la sesión, no se copió al repo,
y no hace falta a menos que se quiera volver a poner una foto en el futuro.

### Colores / tema

Cada color tiene una versión light y una dark definida al principio de `build(theme)`
(`accent1`, `panel_bg_top`, `heading_color`, etc.). El mismo `build()` se llama dos veces
(`build("dark")` y `build("light")`) al final del archivo.

---

## 3. Mapa del README — de dónde sale cada dato

Esta es la parte más importante para "que no haya ningún error": para cada sección, de
dónde sale el dato y cómo volver a verificarlo.

| Sección | Fuente real | Cómo re-verificar |
|---|---|---|
| Hero (dark.svg/light.svg) | Generado localmente, ver sección 2 | Abrir el SVG en un navegador |
| Links (Portfolio/LinkedIn/Claude Academy/Google Skillshop/Email) | URLs reales del usuario | Click en cada botón |
| Tech Stack (badges) | Stack real declarado por el usuario | — |
| **Featured Projects** | Copiado 1:1 de la sección "Progetti in Evidenza" de miguel.ulamander.com (el usuario pegó el texto completo de su web el 2026-09-12) | Volver a visitar miguel.ulamander.com/#proyectos |
| GitHub Stats (streak) | `streak-stats.demolab.com` con el usuario `MiguelGranado`, dato real vía la API de GitHub que usa ese servicio | Ver sección 5 — **tenía un bug, ya corregido** |
| Profile Views / Followers / Public Repos | `komarev.com` y `img.shields.io`, ambos consultan la API real de GitHub en vivo | Se actualizan solos, no hace falta tocar nada |
| Snake animation | Generado por `.github/workflows/snake.yml`, ver sección 6 | Ver Actions tab del repo |
| Certification roadmap | Certificaciones que el usuario **todavía no tiene** (roadmap a futuro) — nunca marcar como completadas sin el examen aprobado | — |
| Microsoft Learn progress | Nivel 15, 773K+ XP, 8 learning paths — del transcript público: https://learn.microsoft.com/en-us/users/miguelvictorgranadosmasias-2225/ | Visitar esa URL |
| Google Ads Certifications | Google Skillshop, 6 reales confirmadas visualmente + "AI-Powered Performance Ads" marcada "✅ Completed" **por un commit externo a esta sesión** (`97ce7ea`, fuera de un PR) — no verificado independientemente por Claude | Ver sección 7 — pendiente de confirmación del usuario |
| Claude Academy Training | Las 19 insignias reales, extraídas directamente del DOM de `academy.claude.com/dashboard` (cuenta logueada del usuario) el 2026-09-12 | Cada fila tiene su propio link "Verify" público (`academy.claude.com/badges/{uuid}`) |
| GitHub Achievements | Solo Quickdraw y YOLO — las únicas ganadas legítimamente con acciones reales mínimas (un PR real mergeado, un issue real cerrado rápido). Imágenes oficiales de `github.githubassets.com` | — |

---

## 4. Historial de cambios reales de esta sesión (2026-09-12)

En orden, con número de PR:

1. **#11–#14**: iteraciones del hero (panel más rico, animación de aparición punto por
   punto del retrato, más espacio entre secciones).
2. **#13**: el stack de texto (`EXTRA_STACK_TAGS`) se hizo copiando la lista real de
   miguel.ulamander.com en vez de inventar tags.
3. **97ce7ea** (commit directo a `main`, sin PR — no hecho por Claude en esta sesión):
   marcó "AI-Powered Performance Ads" como completado. **Ver sección 7.**
4. **#15 — Featured Projects**: se agregó la sección con los 8 proyectos reales
   (5 públicos con URL, 3 privados de cliente marcados como tal), copiados del texto
   completo que el usuario pegó de su propia web.
5. **#16 — Remove photo**: se quitó el retrato pixelado del hero por pedido explícito
   ("quita la foto, ya no la quiero"). El panel de texto pasó a usar todo el ancho.
6. **#17 — Full Claude Academy list**: se reemplazó "8 insignias + resumen de 11 más" por
   las 19 insignias reales, cada una con su link de verificación individual.
7. **#18 — Fix streak-stats**: bug real encontrado en verificación en vivo — los números
   del widget de racha de contribuciones no se veían (quedaban en `opacity:0`). Corregido
   agregando `&disable_animations=true` a la URL del widget. Ver sección 5.
8. **Este commit — Documentación + script del hero versionado**: este archivo, más mover
   `build_hero.py` e `icons/` al repo real (antes solo vivían en el scratchpad de la
   sesión, ver sección 1).

---

## 5. Bug real encontrado y corregido: streak-stats invisible

**Síntoma:** en la página pública del perfil, la caja de "GitHub Stats" se veía casi
vacía — solo el fondo oscuro y dos líneas divisorias verticales, sin ningún número.

**Causa raíz:** el SVG que genera `streak-stats.demolab.com` dibuja cada número/texto con
`style="opacity: 0; animation: fadein 0.5s ... forwards"` — es decir, el estado *base* es
invisible, y depende de que la animación CSS realmente se ejecute para hacerse visible.
Cuando GitHub embebe ese SVG externo vía `<img>` dentro de un README, esa animación no se
dispara — el resultado es que el estado base (invisible) es el único que se ve.

Esto es **el problema opuesto** al patrón seguro que ya se había usado para el retrato
pixelado (antes de quitarlo): ahí cada punto se dibujaba con su opacidad final ya puesta
como atributo base, y la animación solo interpolaba *desde* 0 — así que aunque la
animación no corriera, el dibujo se veía bien igual. `streak-stats` hace justo lo
contrario, y por eso fallaba.

**Fix:** el proyecto `DenverCoder1/github-readme-streak-stats` (que es lo que corre detrás
de `streak-stats.demolab.com`) tiene un parámetro documentado exactamente para este caso:
`&disable_animations=true`. Se agregó a las dos URLs (dark y light) en el README. Se
verificó con `curl` directo a la URL que, con ese parámetro, el SVG devuelve
`opacity: 1` fijo en vez de depender de la animación — y se confirmó en vivo en GitHub que
ahora se ven los tres números reales: **1,194 contribuciones totales · racha actual 3 días
(10–12 sep) · racha más larga 8 días (29 may – 5 jun)**.

**Lección para el futuro:** cualquier badge/widget externo que dependa de animación CSS
para mostrarse debe probarse específicamente embebido en GitHub (no alcanza con abrir la
URL sola en el navegador, ahí si anima bien) — y hay que preferir widgets que empiecen
visibles por defecto, o que tengan un flag para desactivar la animación como este.

---

## 6. GitHub Actions — snake.yml

```yaml
on:
  schedule: "0 */12 * * *"   # cada 12 horas
  workflow_dispatch:          # manual desde la pestaña Actions
  push:
    branches: [main]          # también corre en cada push a main
```

Usa `Platane/snk/svg-only@v3` para generar `dist/snake-dark.svg` y `dist/snake-light.svg`
a partir del grid real de contribuciones del usuario, y `crazy-max/ghaction-github-pages@v3.1.0`
para publicarlos en la rama `output` (commit automático "Update snake animation [skip ci]",
hecho por `github-actions[bot]`).

El README referencia esos archivos directo desde la rama `output` vía
`raw.githubusercontent.com`. **Nunca hay que commitear snake-*.svg a mano** — se
regeneran solos. Verificado en vivo (2026-09-12): 13 corridas del workflow, todas en
verde, la última disparada por el merge del PR #18, snake-dark.svg/snake-light.svg
actualizados hace minutos en la rama `output`.

---

## 7. Cosas pendientes / que requieren al usuario, no a Claude

- **"AI-Powered Performance Ads" marcado como completado**: este cambio (commit `97ce7ea`)
  se hizo directamente sobre `main`, fuera de esta sesión de Claude Code (probablemente
  desde otra sesión o directo en GitHub). Claude nunca vio una prueba (captura con fecha
  visible, o acceso a la segunda cuenta mencionada) de que ese examen esté realmente
  aprobado, y lo dejó tal cual está por respeto a que es una edición directa del usuario
  sobre su propio repo — **no porque esté verificado**. Si no es correcto, hay que
  revertir esa línea a "⏳ In progress" en el README.
- **Insignias visuales de Claude Academy (capturas)**: el usuario pidió capturas de las
  19 insignias reales. No se pudieron generar como archivos de imagen reales: la imagen
  de cada insignia se dibuja en vivo por la app de Claude Academy (no existe como archivo
  estático en ningún lado), y la única forma de capturarla headless sin usar la sesión
  interactiva del navegador habría requerido extraer las cookies de sesión guardadas del
  Chrome real del usuario — algo que no se hizo por ser demasiado invasivo (esas cookies
  dan acceso a *todas* las cuentas logueadas en ese Chrome, no solo Claude Academy). En
  vez de eso, el README lista las 19 con su link de verificación pública individual
  (`academy.claude.com/badges/{uuid}`), agrupadas por categoría. Si el usuario de verdad
  quiere las imágenes reales, la única vía segura es que él mismo entre a
  `academy.claude.com/dashboard`, haga clic en cada insignia y guarde la imagen
  ("clic derecho → guardar imagen") — es un proceso de ~2 minutos que solo él puede hacer
  sin el riesgo de exponer sus cookies de sesión.

---

## 8. Convención de trabajo usada (branch + PR)

Todo cambio en este repo, sin excepción, siguió este flujo:

```bash
git fetch origin main --quiet
git checkout main && git reset --hard origin/main
git checkout -b <nombre-descriptivo-de-la-rama>
# ... cambios ...
git add <archivos>
git commit -m "mensaje descriptivo + Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
git push -u origin <nombre-de-la-rama>
gh pr create --repo MiguelGranado/MiguelGranado --title "..." --body "..."
gh pr merge --repo MiguelGranado/MiguelGranado <rama> --merge --delete-branch
```

Siempre partiendo de `origin/main` fresco (nunca de una rama local vieja) — esto evitó
pisar cambios que se hicieron fuera de esta sesión (como el commit `97ce7ea` de la
sección 7), porque cada rama nueva arrancó desde el último estado real de GitHub.

---

## 9. Si algo se ve raro en el futuro — checklist rápido

1. **¿Un widget externo no se ve?** Revisar si depende de animación CSS/JS para
   mostrarse (ver sección 5) — buscar un flag `disable_animations` o similar.
2. **¿El snake no se actualiza?** Revisar la pestaña Actions del repo — el workflow debe
   estar en verde. Si falla, el problema está en `Platane/snk` o en permisos del token,
   no en el README.
3. **¿Cambiaste el stack o las certificaciones reales?** Actualizá `EXTRA_STACK_TAGS` en
   `scripts/hero/build_hero.py` **y** regenerá `dark.svg`/`light.svg` (sección 2) — son
   dos lugares separados que hay que mantener sincronizados a mano.
4. **¿Agregaste un proyecto nuevo al portafolio?** Actualizá la tabla "Featured Projects"
   del README a mano — no hay ningún script que la genere automáticamente.
5. **Antes de marcar cualquier certificación/logro como "completado"**: verificar
   visualmente la fuente real (Microsoft Learn, Skillshop, Claude Academy, LinkedIn) antes
   de tocar el README. Nunca inflar commits, PRs o certificaciones no aprobadas — eso es
   lo primero que alguien chequea en una entrevista.
