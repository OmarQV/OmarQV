# Profile maintenance (OQV 2.0)

Structure: **credential → whoami → milestones → build log → stack →
activity → background → contact**, separated by an animated gradient divider.

## What updates itself

| Piece | Source | Workflow |
| :-- | :-- | :-- |
| `assets/credential-dark.svg` / `-light.svg` | `scripts/render_profile.py` + `profile.json` + GitHub API (avatar, public repos, followers) | `update-profile.yml`, daily 05:41 La Paz |
| `assets/buildlog-dark.svg` / `-light.svg` | `timeline` in `profile.json` | same |
| `assets/divider.svg` | fixed brand gradient | same |
| `profile-3d-contrib/*.svg` | yoshi389111/github-profile-3d-contrib | `profile-3d.yml`, daily |

Both workflows use only the built-in `GITHUB_TOKEN`; no secrets to configure.
The renderer is standard-library Python and falls back to `profile.json`
values and an initials avatar if the API is unreachable, so the card never
shows as a broken image.

## What you edit by hand

- **Card text** (role, track, status, latest project, hackathon count, 1st
  places): `profile.json`. Pushing it re-renders the card automatically.
- **Milestones**: only verifiable wins or roles; team wins stay credited as team wins.
- **Build log**: add an item to `timeline` in `profile.json`
  (`[event, project, description]`, add `true` as a 4th value for a 1st place).
  Push, and the workflow redraws the SVG.

Run locally without network: `python scripts/render_profile.py --offline`.

## Account settings outside this repository

- **Bio:** `Building verifiable systems · AI agents × Web3 × security · La Paz, Bolivia`
- **Website:** `https://omidev.vercel.app/` · **Location:** `La Paz, Bolivia`
- **Pins (6):** your strongest projects (Vector52, Pay-per-Thought, AIni Pay, AndesMaaS…), each with a one-line
  description, 3–5 topics and the demo URL in the repo's *Website* field.

## Deliberately not used

Public GitHub Readme Stats / streak endpoints (rate limits leave broken
cards), and games driven by Issues (noise in notifications). The credential
card covers the same numbers without depending on a third-party service.
