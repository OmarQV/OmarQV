# Profile maintenance

The README keeps the original identity → practice → recognition → stack →
direction → activity → background → contact structure. It intentionally has
**no featured-project section**.

## Account settings outside this repository

GitHub's sidebar bio, website, location and pinned repositories are separate
account settings. Editing this repository cannot change them. Suggested bio:

> Developer building verifiable systems across AI agents, Web3 and security · La Paz, Bolivia

Website: `https://omidev.vercel.app/` · Location: `La Paz, Bolivia`.

If you also want fewer repositories shown on the profile page, review
**Customize your pins** while signed in to GitHub. The README does not list or
link to individual projects.

## Dynamic elements

- The header uses `readme-typing-svg` for a short animated introduction.
- Technology logos come from `skillicons.dev`; social badges come from
  `shields.io`.
- `.github/workflows/profile-3d.yml` uses
  `yoshi389111/github-profile-3d-contrib` to generate the 3D contribution
  graph each day. It commits a night-view SVG for dark mode and a Southern
  Hemisphere seasonal SVG for light mode, using the built-in `GITHUB_TOKEN`.
- The activity graphic reports contributions, not ability. Real-world awards
  and roles are stated separately in the Milestones section.

The public GitHub Readme Stats endpoint was deliberately not used: its
availability and rate limits can leave broken cards in a profile. Metrics
requires setting up a separate personal access token for a useful account-wide
render. Keep the profile dependent on as few services as possible.
