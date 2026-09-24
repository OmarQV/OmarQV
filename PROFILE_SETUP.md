# Profile settings and maintenance

The README and its visual assets are maintained in this repository. GitHub's
profile sidebar and pinned repositories are separate account settings.

## Suggested public profile fields

- **Bio:** `Building verifiable software across AI agents, Web3 and security · La Paz, Bolivia`
- **Website:** `https://omidev.vercel.app/`
- **Location:** `La Paz, Bolivia`
- **Social:** LinkedIn and X links already used in `README.md`.

## Pinned repositories

Start with [`vector52`](https://github.com/OmarQV/vector52). Its public README
documents the project. Most other recent repositories have no README yet, so
prepare those before pinning them. In particular, `omidev` and `stellar-build`
could become strong pins after adding a clear description, setup instructions,
screenshots or a demo, and an honest current status. Do not fill six slots with
old coursework merely to use every slot.

Pay-per-Thought and AIni Pay currently have working project/demo links in the
profile, but no confirmed public repository on this account to pin.

Use GitHub's **Customize your pins** control on the profile page. GitHub pins
cannot be changed by editing this repository.

## Visual assets

- `python scripts/render_hero.py` generates the desktop and mobile heroes for
  dark and light themes. The SVGs include subtle animation and static content
  that remains legible when motion is reduced.
- `python scripts/render_profile.py` queries GitHub's Languages API for four
  selected public repositories. It generates the desktop and mobile code
  footprint charts. The chart counts language bytes, not expertise.
- `.github/workflows/update-profile.yml` refreshes the footprint daily and
  commits only when the chart changes. It uses the built-in `GITHUB_TOKEN` and
  needs repository Actions to have write permission for contents.

If a project changes scope, edit its description in `README.md`. If the chart's
sample should change, edit `REPOSITORIES` in `scripts/render_profile.py`.
