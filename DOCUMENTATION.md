# Perfil GitHub — MiguelGranado

Respaldo local del README de perfil (`github.com/MiguelGranado`).
Única documentación de esta carpeta. Actualizado: 2026-09-12.

## Estructura

```
readme-publicado/     → README.md, dark.svg, light.svg (lo que va al repo)
scripts/hero/         → build_hero.py + icons/ (genera los SVG)
scripts/workflows/    → snake.yml (Action de la serpiente de contribuciones)
DOCUMENTACION.md      → este archivo
```

## Regenerar el hero

```bash
cd scripts/hero
python3 build_hero.py
cp dark.svg light.svg ../../readme-publicado/
```

Paleta: slate + acento Ulamander `#fe702d` (sin marrón/ámbar mezclado).
Stats del hero: API real de GitHub (commits / PRs). Lenguajes: GraphQL real
(TypeScript dominante, no inventado).

## Publicar en GitHub

1. Copiar `readme-publicado/README.md`, `dark.svg`, `light.svg` a la raíz de
   `MiguelGranado/MiguelGranado`.
2. Copiar `scripts/workflows/snake.yml` → `.github/workflows/snake.yml`.
3. Commit y push a `main` (sin trailer `Co-Authored-By` de terceros).
4. El workflow regenera la snake en la rama `output`.

## Fuentes de datos (verificables)

| Bloque | Fuente |
|---|---|
| Hero / stack / proyectos | miguel.ulamander.com |
| Streak / views / followers | streak-stats, komarev, shields.io |
| Certificaciones Google | Skillshop / LinkedIn (11) |
| Claude Academy | academy.claude.com (19 badges con Verify) |
| Roadmap MS / Fortinet / GHAS | roadmap — no marcar como aprobadas sin examen |
| Achievements GitHub | solo Quickdraw + YOLO (ganadas de verdad) |

Email de contacto del perfil: `info@ulamander.com` (el del portafolio).

## Nota sobre contribuyentes

En Insights → Contributors del repo de perfil solo aparece **MiguelGranado**.
Varios commits antiguos llevan `Co-Authored-By: Claude Sonnet 5` en el mensaje;
eso no crea otro contributor en el gráfico, pero sí se ve en el detalle del commit.
Para borrarlo del historial hace falta reescribir `main` y force-push — no se hace
desde aquí sin confirmación explícita tuya.
