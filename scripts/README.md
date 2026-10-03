# How this profile is built

Every visual block of the profile README is a generated SVG that follows one design
system (`scripts/hero/design.py`: palette, fonts, window chrome, helpers).

| Block | Generator | Output |
|---|---|---|
| Hero | `scripts/hero/build_hero.py` | `assets/hero-{dark,light}[-mobile].svg` |
| Contact buttons | `scripts/hero/build_contact.py` | `assets/contact-{portfolio,linkedin,email}-{dark,light}.svg` |
| About | `scripts/hero/build_about.py` | `assets/about-{dark,light}[-mobile].svg` |
| Expertise (6 pillars) | `scripts/hero/build_expertise.py` | `assets/expertise-{dark,light}[-mobile].svg` |
| Services + method | `scripts/hero/build_services.py` | `assets/services-{dark,light}[-mobile].svg` |
| Credentials | `scripts/hero/build_credentials.py` | `assets/credentials-{dark,light}[-mobile].svg` |
| Projects | `.github/scripts/generate_projects.py` (CI) | `projects` branch: `projects[-light][-mobile].svg` |
| Contribution activity + snake | `scripts/hero/build_activity.py` (CI, daily, GitHub GraphQL) | `output` branch: `activity-{dark,light}[-mobile].svg` |
| GitHub achievements (with tiers) | `scripts/hero/build_achievements.py` (CI, daily, read from the profile) | `output` branch: `achievements-{dark,light}[-mobile].svg` |

```bash
python3 scripts/build_all.py                      # hero, contact, about, expertise, services, credentials
python3 .github/scripts/refresh_languages.py      # real language bytes -> projects.json (needs gh auth)
```

Rules:

- **Real data only.** Language splits come from the GitHub API (`refresh_languages.py`);
  credentials are listed only when a public record exists.
- **Desktop + mobile, dark + light.** Desktop canvases are 960 wide, mobile 480 wide.
  Each panel is written twice inside links ending in `#gh-dark-mode-only` /
  `#gh-light-mode-only` (GitHub hides the one that doesn't match the visitor's theme);
  inside each, `<source media="(max-width: 1099px)">` picks the mobile file.
- **Hosting.** Images are served from `raw.githubusercontent.com` (5-minute cache), so a
  merge is visible within minutes — no CDN purge needed.
- **CI check.** `.github/workflows/check-assets.yml` regenerates `assets/` and fails if
  the committed files differ from the generators.
