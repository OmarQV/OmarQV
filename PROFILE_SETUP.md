# Profile maintenance (OQV 2.0)

Structure: **credential → whoami → proof of work → milestones → build log →
live repos → stack → activity → background → contact.**

## What updates itself

| Piece | Source | Workflow |
| :-- | :-- | :-- |
| `assets/credential-dark.svg` / `-light.svg` | `scripts/render_profile.py` + `profile.json` + GitHub API (avatar, public repos, followers) | `update-profile.yml`, daily 05:41 La Paz |
| `<!--LIVE:START-->` block in README | Latest pushed public repos (no forks, no archived, no `OmarQV`) | same |
| `profile-3d-contrib/*.svg` | yoshi389111/github-profile-3d-contrib | `profile-3d.yml`, daily |

Both workflows use only the built-in `GITHUB_TOKEN`; no secrets to configure.
The renderer is standard-library Python and falls back to `profile.json`
values and an initials avatar if the API is unreachable, so the card never
shows as a broken image.

## What you edit by hand

- **Card text** (role, track, status, latest project, hackathon count, 1st
  places): `profile.json`. Pushing it re-renders the card automatically.
- **Proof of work**: the six project cells in `README.md`. Each has an
  `<!-- add: [Repo](...) -->` comment. Replace it with real repo/demo links.
- **Milestones**: only verifiable wins or roles; team wins stay credited as team wins.
- **Build log**: add a line when you finish a hackathon.

Run locally without network: `python scripts/render_profile.py --offline`.

## Account settings outside this repository

- **Bio:** `Building verifiable systems · AI agents × Web3 × security · La Paz, Bolivia`
- **Website:** `https://omidev.vercel.app/` · **Location:** `La Paz, Bolivia`
- **Pins (6):** the same projects as *Proof of work*, each with a one-line
  description, 3–5 topics and the demo URL in the repo's *Website* field.

## Deliberately not used

Public GitHub Readme Stats / streak endpoints (rate limits leave broken
cards), and games driven by Issues (noise in notifications). The credential
card covers the same numbers without depending on a third-party service.
