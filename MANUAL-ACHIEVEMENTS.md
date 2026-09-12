# Manual: GitHub Achievements (insignias)

Para Miguel + compañeros (3–4). Criterios según guías de la comunidad GitHub (GitHub no publica todos los umbrales oficiales; pueden cambiar).

**Settings:** Profile → **Show Achievements on my profile** = ON (ya activado).

---

## Qué tienes / qué falta (referencia arifhaxn)

arifhaxn muestra tipicamente: **Starstruck**, **Quickdraw**, **Pull Shark**.

| Insignia | Cómo se gana | Umbral base | Qué pedir a compañeros |
|---|---|---|---|
| **Pull Shark** | PRs **mergeados** (no solo abiertos) | 2 → 16 → 128 → 1024 | Abrir PRs reales a un repo vuestro; Miguel hace merge |
| **Quickdraw** | Cerrar issue o PR en **≤ 5 min** de abrirlo | 1 vez | Alguien abre issue → Miguel (u otro) lo cierra al momento |
| **YOLO** | Mergear un PR **sin review** | 1 vez | PR en repo propio → merge directo sin pedir review |
| **Pair Extraordinaire** | Commit **co-authored** en un PR mergeado | 1 → 10 → 24 → 48 | Pair: commit con trailer `Co-authored-by:` (ver abajo) |
| **Starstruck** | Un repo **tuyo** llega a N stars | 16 → 128 → 512 → 4096 | Compañeros + red: star a un repo público útil |
| **Galaxy Brain** | Respuestas **aceptadas** en Discussions | 2 → 8 → 16 → 32 | Difícil vía Community; mejor Discussions de un repo vuestro |
| **Public Sponsor** | Patrocinar a alguien (público) | 1 vez | Opcional (cuesta dinero) |

Históricos / no farmables ahora: Arctic Code Vault, Mars 2020, etc.

---

## Scripts listos para el equipo (legítimos)

Haced trabajo real en repos de Ulamander (docs, fix typo, feature pequeña). No hace falta spam.

### 1) Pull Shark (todos)

1. Repo público o privado del equipo (ej. `MiguelGranado/...` o org).
2. Cada compañero: branch → cambio pequeño → **Pull Request**.
3. Miguel (o mantainer): **Merge**.
4. Tras **2 merges** → Pull Shark. Seguid mergeando para tiers.

### 2) Quickdraw (Miguel + 1 compañero)

1. Compañero abre un issue: “chore: close-me-quickdraw”.
2. En **menos de 5 minutos**, Miguel lo cierra.
3. Listo (una vez).

### 3) YOLO (Miguel)

1. Abrís un PR en un repo vuestro.
2. Merge **sin** pedir review / sin reviewers.
3. Listo.

### 4) Pair Extraordinaire (Miguel + 1 compañero)

En el commit del PR:

```bash
git commit -m "$(cat <<'EOF'
docs: update README together

Co-authored-by: NAME <email-github@users.noreply.github.com>
EOF
)"
```

- `NAME` = nombre del compañero en GitHub  
- email = el de su cuenta (Settings → Emails → `...@users.noreply.github.com`)  
- El PR debe **mergearse**  
- Ambos usan su cuenta real (no cuentas fake)

### 5) Starstruck (estrellas en un repo)

1. Elegid **un** repo público con README claro (herramienta / template).
2. Pedid a los 3–4 compañeros + contactos: **Star** ese repo.
3. Base = **16 stars**. Más stars = tiers.

### 6) Galaxy Brain (opcional)

1. Activad **Discussions** en un repo.
2. Alguien pregunta; otro responde bien; marcar **Accepted answer**.
3. Hacen falta **2** aceptadas (umbral base).

---

## Mensaje corto para WhatsApp / Slack

```
Chicos, 15 min en GitHub para badges del equipo:

1) Entrad a [REPO] → dad Star
2) Fork/branch → cambiad 1 línea en docs → abrid PR
3) Yo hago merge (Pull Shark)
4) Uno abre un issue “quickdraw” y lo cierro en 5 min
5) Un commit juntos con Co-authored-by (Pair)

Cuentas reales, cambios reales. Gracias.
```

---

## Checklist Miguel

- [x] Show Achievements = ON  
- [ ] 2+ PRs mergeados → Pull Shark  
- [ ] Quickdraw (issue cerrado &lt; 5 min)  
- [x] YOLO (self-merge sin review)  
- [ ] 1 PR co-authored mergeado → Pair  
- [ ] Repo público ≥ 16 stars → Starstruck  
- [ ] (Opcional) Discussions aceptadas → Galaxy Brain  

---

## Qué NO hacer

- Cuentas falsas / bots para stars o PRs  
- Spam de issues vacíos  
- Comprar stars  

GitHub puede anular actividad fraudulenta. Con 3–4 compañeros haciendo PRs/docs reales alcanza para las insignias base.

<!-- yolo 2026-09-12T17:35:34Z -->

- [x] Pair Extraordinaire kickoff with @alpacaserranagaming-eng (2026-09-12)
