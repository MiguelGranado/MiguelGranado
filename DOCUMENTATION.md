# Profilo GitHub — MiguelGranado

Respaldo locale del README di profilo pubblicato su
https://github.com/MiguelGranado

## Contenuto

| Percorso | Ruolo |
|---|---|
| `readme-publicado/` | `README.md`, `dark.svg`, `light.svg` da pubblicare |
| `scripts/hero/build_hero.py` | Genera gli SVG del header |
| `scripts/hero/icons/` | Loghi stack (MIT) |
| `scripts/workflows/snake.yml` | Action della snake contributi |

## Pubblicare

1. Copiare `readme-publicado/*` nella root del repo `MiguelGranado/MiguelGranado`
2. Copiare `scripts/workflows/snake.yml` → `.github/workflows/snake.yml`
3. Commit + push su `main`

## Rigenerare l’header

```bash
cd scripts/hero
python3 build_hero.py
cp dark.svg light.svg ../../readme-publicado/
```

## Fonte dati

Profilo e certificazioni allineati a https://miguel.ulamander.com  
Lingua del README: **italiano** (come il portfolio).
