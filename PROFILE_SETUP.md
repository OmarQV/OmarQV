# Profile maintenance

The visible structure is **credential → introduction → recognition → practice
areas → stack → GitHub activity → background → contact**. It intentionally has
no featured-project list. The Stellar Elite poster is tucked into a collapsed
detail beneath the recognition table, so it does not dominate the profile.

## Evidence and wording

- The Rally Latinoamericano de Innovación certificate records **third place
  in the Innovation category for team a52 at the UMSA venue in Bolivia**. It
  does **not** establish a region-wide third-place result.
- A separate certificate records participation on **16–17 October 2026**;
  the certificates were issued **20 October 2026**.
- The Stellar Elite visual describes TilcAI and the closing of the BAF ×
  Stellar program. It is presented as cohort participation, not a prize.
- The certificates remain in Omar's private source folder and are not copied
  into this public repository. If public verification is later desired, first
  review their QR codes and personal information.

## Dynamic assets

- `profile.json` supplies the credential text and fallback GitHub numbers.
  `scripts/render_profile.py` creates desktop and mobile credential SVGs and the
  divider. `update-profile.yml` runs daily and on changes to the config or
  renderer. The field `current_focus` replaces the old featured-project field.
- `profile-3d.yml` generates the contribution graphic for dark/light themes.
- Both workflows use the built-in `GITHUB_TOKEN`; no personal token is needed.

Run locally: `python scripts/render_profile.py --offline`. This is useful for
layout checks, but the offline mode uses the initials and fallback numbers;
do not commit those preview assets in place of the live ones.

## GitHub account settings

The sidebar bio and pinned repositories are controlled in GitHub account
settings, outside this README. The README itself does not list projects.
