# How this profile is built

Every visual block of the profile README is a generated SVG that follows one design
system (`scripts/hero/design.py`: palette, fonts, window chrome, helpers).

| Block | Generator | Output |
|---|---|---|
| Hero | `scripts/hero/build_hero.py` | `assets/hero-{dark,light}[-mobile].svg` |
| Contact buttons | `scripts/hero/build_contact.py` | `assets/contact-{portfolio,linkedin,email}-{dark,light}.svg` |
| About | `scripts/hero/build_about.py` | `assets/about-{dark,light}[-mobile].svg` |
| Credentials | `scripts/hero/build_credentials.py` | `assets/credentials-{dark,light}[-mobile].svg` |
| Projects | `.github/scripts/generate_projects.py` (CI) | `projects` branch: `projects[-light][-mobile].svg` |

```bash
python3 scripts/build_all.py                      # hero, contact, about, credentials
python3 .github/scripts/refresh_languages.py      # real language bytes -> projects.json (needs gh auth)
```

Rules:

- **Real data only.** Language splits come from the GitHub API (`refresh_languages.py`);
  credentials are listed only when a public record exists.
- **Desktop + mobile.** Desktop canvases are 960 wide, mobile 480 wide. The README picks
  one with `<picture>`: mobile sources are written as `(prefers-color-scheme:dark)`
  *without a space* so GitHub's theme switcher does not rewrite them.
- **Hosting.** Images are served from `raw.githubusercontent.com` (5-minute cache), so a
  merge is visible within minutes — no CDN purge needed.
- **CI check.** `.github/workflows/check-assets.yml` regenerates `assets/` and fails if
  the committed files differ from the generators.
