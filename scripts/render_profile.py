#!/usr/bin/env python3
"""Render the OQV profile assets: smart credential and build log (dark + light
SVG) plus the gradient divider.

Standard library only, so it runs on a bare GitHub Actions runner.
Every network call has a fallback: if GitHub is unreachable the card is still
rendered with the values in profile.json and an initials avatar.

Usage:
    python scripts/render_profile.py            # uses GITHUB_TOKEN if present
    python scripts/render_profile.py --offline  # no network (local preview)
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
USER = os.environ.get("USERNAME_OVERRIDE") or CONFIG["username"]
OFFLINE = "--offline" in sys.argv
TOKEN = os.environ.get("GITHUB_TOKEN", "")

PALETTES = {
    "dark": {
        "bg1": "#0d1117", "bg2": "#111a2b", "panel": "#161b22", "border": "#30363d",
        "grid": "#1f6feb", "accent": "#58a6ff", "accent2": "#3fb950",
        "text": "#e6edf3", "muted": "#8b949e", "warn": "#d29922",
        "purple": "#a371f7", "pink": "#f778ba", "orange": "#f0883e", "gold": "#e3b341",
    },
    "light": {
        "bg1": "#ffffff", "bg2": "#eef4fc", "panel": "#f6f8fa", "border": "#d0d7de",
        "grid": "#0969da", "accent": "#0969da", "accent2": "#1a7f37",
        "text": "#1f2328", "muted": "#59636e", "warn": "#9a6700",
        "purple": "#8250df", "pink": "#bf3989", "orange": "#bc4c00", "gold": "#9a6700",
    },
}

MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


# --------------------------------------------------------------------------- data
def fetch(url: str, raw: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile-renderer"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read()
        return (body, resp.headers.get_content_type()) if raw else json.loads(body)


def collect() -> dict:
    data = {
        "public_repos": CONFIG["fallback"]["public_repos"],
        "followers": CONFIG["fallback"]["followers"],
        "avatar": None,
    }
    if OFFLINE:
        return data
    try:
        user = fetch(f"https://api.github.com/users/{USER}")
        data["public_repos"] = str(user.get("public_repos", data["public_repos"]))
        data["followers"] = str(user.get("followers", data["followers"]))
    except Exception as exc:  # noqa: BLE001 - keep rendering with fallbacks
        print(f"warn: user stats unavailable ({exc})", file=sys.stderr)
    try:
        body, ctype = fetch(f"https://github.com/{USER}.png?size=240", raw=True)
        data["avatar"] = f"data:{ctype};base64,{base64.b64encode(body).decode()}"
    except Exception as exc:  # noqa: BLE001
        print(f"warn: avatar unavailable ({exc})", file=sys.stderr)
    return data


# --------------------------------------------------------------------------- svg
def barcode(seed: str, x: float, y: float, h: float, color: str, width: float) -> str:
    digest = hashlib.sha256(seed.encode()).digest() * 4
    out, cx, i = [], x, 0
    while cx < x + width and i < len(digest):
        w = 1 + digest[i] % 3
        if digest[i] % 5:
            out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
        cx += w + 1 + (digest[i] >> 6)
        i += 1
    return "".join(out)


HACK = {
    "bg1": "#04100b", "bg2": "#0a2419", "green": "#3fb68b", "dim": "#16392b",
    "text": "#c3e2d4", "muted": "#5b8c78", "cyan": "#6fb2b0", "amber": "#c4a46a",
    "magenta": "#a98fb8", "red": "#c07078",
}
RAIN = "01ABCDEF0123456789アイウエオカキクケコサシスセソタチツテト#$%&<>/\\"


def matrix_rain(W: int, H: int, color: str) -> str:
    """Deterministic falling-glyph columns (no randomness → stable diffs)."""
    out = []
    seed = hashlib.sha256(f"{USER}-rain".encode()).digest() * 8
    cols = W // 22
    for c in range(cols):
        b = seed[c * 5: c * 5 + 5]
        x = 8 + c * 22 + b[0] % 6
        n = 8 + b[1] % 10
        glyphs = "".join(RAIN[(b[2] + k * 7 + b[3] * k) % len(RAIN)] for k in range(n))
        dur = 7 + b[4] % 9
        delay = -(b[2] % dur)
        op = .05 + (b[3] % 5) / 70
        tsp = "".join(
            f'<tspan x="{x}" dy="15" fill-opacity="{(k + 1) / n:.2f}">{escape(g)}</tspan>'
            for k, g in enumerate(glyphs))
        out.append(
            f'<text class="rain" style="animation-duration:{dur}s;animation-delay:{delay}s" '
            f'y="{-n * 15}" font-size="12" fill="{color}" opacity="{op:.2f}">{tsp}</text>')
    return "".join(out)


def render_card(theme: str, data: dict, today: dt.date) -> str:
    # Hacker terminal look for both themes: a terminal is dark by nature.
    h = HACK
    W, H = 880, 336
    t = lambda s: escape(str(s))  # noqa: E731

    initials = "".join(w[0] for w in CONFIG["name"].split()[:2])
    if data["avatar"]:
        avatar = (f'<image href="{data["avatar"]}" x="56" y="110" width="128" height="128" '
                  f'clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>'
                  f'<rect x="56" y="110" width="128" height="128" clip-path="url(#av)" fill="{h["green"]}" fill-opacity=".06"/>'
                  )
    else:
        avatar = (f'<circle cx="120" cy="174" r="64" fill="{h["bg2"]}"/>'
                  f'<text x="120" y="187" text-anchor="middle" font-family="{MONO}" font-size="38" '
                  f'font-weight="700" fill="{h["green"]}" filter="url(#glow)">{t(initials)}</text>')

    hues = [h["cyan"], h["amber"], h["green"], h["magenta"]]
    parts = CONFIG["tagline"].split(" × ")
    tagline = f'<tspan fill="{h["muted"]}"> :: </tspan>'.join(
        f'<tspan fill="{hues[i % len(hues)]}">{t(w.replace(" ", "_"))}</tspan>' for i, w in enumerate(parts))

    rows = []
    for i, (k, v) in enumerate(CONFIG["rows"]):
        y = 190 + i * 24
        rows.append(
            f'<text x="226" y="{y}" font-family="{MONO}" font-size="12" fill="{h["muted"]}">'
            f'<tspan fill="{hues[i % len(hues)]}">$</tspan> {t(k.lower())}</text>'
            f'<text x="316" y="{y}" font-family="{MONO}" font-size="12.5" fill="{h["text"]}">{t(v)}</text>')

    stats = [
        (data["public_repos"], "PUBLIC_REPOS", h["cyan"]), (data["followers"], "FOLLOWERS", h["green"]),
        (CONFIG["hackathons"], "HACKATHONS", h["magenta"]), (CONFIG["first_places"], "1ST_PLACES", h["amber"]),
    ]
    stat_svg = []
    for i, (val, label, col) in enumerate(stats):
        cx = 674 + (i % 2) * 96
        cy = 124 + (i // 2) * 64
        stat_svg.append(
            f'<text x="{cx}" y="{cy}" font-family="{MONO}" font-size="25" font-weight="700" '
            f'fill="{col}" filter="url(#glow)">{t(val)}</text>'
            f'<text x="{cx}" y="{cy + 16}" font-family="{MONO}" font-size="9" letter-spacing=".5" '
            f'fill="{h["muted"]}">{t(label)}</text>')

    digest = hashlib.sha256(f'{USER}{CONFIG["credential_id"]}{today}'.encode()).hexdigest()
    sync = today.strftime("%Y-%m-%d")
    name = t(CONFIG["name"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">{name} — developer credential</title>
<desc id="desc">{t(CONFIG["tagline"])}. {t(" · ".join(v for _, v in CONFIG["rows"]))}. Status {t(CONFIG["status"])}, latest project {t(CONFIG["latest_project"])}.</desc>
<defs>
  <radialGradient id="bg" cx=".3" cy=".35" r="1"><stop offset="0" stop-color="{h["bg2"]}"/><stop offset="1" stop-color="{h["bg1"]}"/></radialGradient>
  <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".65"/></radialGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{h["green"]}"/><stop offset=".5" stop-color="{h["cyan"]}"/><stop offset="1" stop-color="{h["magenta"]}"/></linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{h["green"]}" stop-opacity="0"/><stop offset="1" stop-color="{h["green"]}" stop-opacity=".06"/></linearGradient>
  <pattern id="scanlines" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity=".2"/></pattern>
  <filter id="glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="1" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="av"><circle cx="120" cy="174" r="64"/></clipPath>
  <clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath>
  <style>
    text{{font-family:{MONO}}}
    .rain{{animation:rain linear infinite}}
    .spin{{transform-origin:120px 174px;animation:spin 16s linear infinite}}
    .sweep{{animation:sweep 4.5s linear infinite}}
    .blink{{animation:blink 1.1s steps(1) infinite}}
    .g1{{animation:g1 3.2s infinite}} .g2{{animation:g2 3.2s infinite}}
    @keyframes rain{{to{{transform:translateY({H + 220}px)}}}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
    @keyframes sweep{{0%{{transform:translateY(-70px)}}100%{{transform:translateY({H}px)}}}}
    @keyframes blink{{50%{{opacity:0}}}}
    @keyframes g1{{0%,88%,100%{{transform:none;opacity:0}}90%{{transform:translate(-3px,1px);opacity:.35}}93%{{transform:translate(2px,-1px);opacity:.35}}96%{{transform:translate(-1px,0);opacity:.25}}}}
    @keyframes g2{{0%,88%,100%{{transform:none;opacity:0}}90%{{transform:translate(3px,-1px);opacity:.35}}93%{{transform:translate(-2px,1px);opacity:.35}}96%{{transform:translate(1px,0);opacity:.25}}}}
    @media (prefers-reduced-motion:reduce){{.rain,.spin,.sweep,.blink,.g1,.g2{{animation:none}}}}
  </style>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  {matrix_rain(W, H, h["green"])}
  <rect width="{W}" height="{H}" fill="url(#scanlines)"/>
  <rect class="sweep" width="{W}" height="70" fill="url(#sweep)"/>
  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <!-- title bar -->
  <rect width="{W}" height="36" fill="#000" fill-opacity=".55"/>
  <line x1="0" y1="36" x2="{W}" y2="36" stroke="{h["dim"]}"/>
</g>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="none" stroke="url(#edge)" stroke-width="1.2" stroke-opacity=".7"/>
<circle cx="22" cy="18" r="5" fill="{h["red"]}"/><circle cx="40" cy="18" r="5" fill="{h["amber"]}"/><circle cx="58" cy="18" r="5" fill="{h["green"]}"/>
<text x="{W/2}" y="23" text-anchor="middle" font-size="11.5" fill="{h["muted"]}">root@oqv:~ — ssh {t(USER.lower())}@github.com</text>
<text x="{W-20}" y="23" text-anchor="end" font-size="10.5" font-weight="700" letter-spacing="1" fill="{h["green"]}"><tspan class="blink">●</tspan> ACCESS_GRANTED</text>

<!-- prompt -->
<text x="32" y="64" font-size="12.5" fill="{h["green"]}">root@oqv<tspan fill="{h["muted"]}">:</tspan><tspan fill="{h["cyan"]}">~</tspan><tspan fill="{h["muted"]}">#</tspan> <tspan fill="{h["text"]}">./identity --verify --user {t(USER)}</tspan></text>
<text x="32" y="84" font-size="11" fill="{h["muted"]}">[<tspan fill="{h["green"]}"> OK </tspan>] signature valid · sha256:{digest[:24]}…</text>

<!-- avatar -->
<circle cx="120" cy="174" r="76" fill="none" stroke="{h["green"]}" stroke-width="1.5" stroke-dasharray="2 6" class="spin" opacity=".8"/>
<circle cx="120" cy="174" r="68" fill="none" stroke="url(#edge)" stroke-width="2.5" filter="url(#glow)"/>
<path d="M120 94v10M120 244v10M40 174h10M190 174h10" stroke="{h["green"]}" stroke-width="2"/>
{avatar}

<!-- identity with glitch -->
<g font-size="26" font-weight="800" letter-spacing="1">
  <text class="g1" x="224" y="128" fill="{h["red"]}">{name}</text>
  <text class="g2" x="224" y="128" fill="{h["cyan"]}">{name}</text>
  <text x="224" y="128" fill="{h["green"]}">{name}</text>
</g>
<text x="226" y="152" font-size="11.5" font-weight="700" letter-spacing=".8"><tspan fill="{h["muted"]}">&gt; </tspan>{tagline}<tspan class="blink" fill="{h["green"]}"> █</tspan></text>
<line x1="226" y1="166" x2="620" y2="166" stroke="{h["dim"]}" stroke-dasharray="3 3"/>
{"".join(rows)}

<!-- stats panel -->
<rect x="650" y="96" width="200" height="176" rx="8" fill="#000" fill-opacity=".55" stroke="{h["dim"]}"/>
<text x="662" y="90" font-size="9.5" letter-spacing="1" fill="{h["muted"]}">┌─ sys.stats</text>
{"".join(stat_svg)}
<line x1="664" y1="220" x2="836" y2="220" stroke="{h["dim"]}" stroke-dasharray="3 3"/>
<text x="664" y="241" font-size="11" font-weight="700" letter-spacing="1" fill="{h["green"]}"><tspan class="blink">▶</tspan> {t(CONFIG["status"])}</text>
<text x="664" y="260" font-size="10" fill="{h["muted"]}">latest › <tspan fill="{h["amber"]}">{t(CONFIG["latest_project"])}</tspan></text>

<!-- footer -->
<line x1="32" y1="290" x2="{W-32}" y2="290" stroke="{h["dim"]}"/>
{barcode(USER + CONFIG["credential_id"], 32, 302, 18, h["green"], 140)}
<text x="190" y="316" font-size="11" fill="{h["muted"]}">ID <tspan fill="{h["green"]}">{t(CONFIG["credential_id"])}</tspan>  ·  github.com/<tspan fill="{h["text"]}">{t(USER)}</tspan></text>
<text x="{W-32}" y="316" text-anchor="end" font-size="11" fill="{h["muted"]}">last_sync=<tspan fill="{h["cyan"]}">{sync}</tspan></text>
</svg>
"""


# --------------------------------------------------------------------------- build log
def render_timeline(theme: str) -> str:
    p = PALETTES[theme]
    t = lambda s: escape(str(s))  # noqa: E731
    lanes = CONFIG["timeline"]
    W, top, row, head = 880, 64, 27, 46
    H = top + sum(head + len(l["items"]) * row + 22 for l in lanes) - 14
    out, y = [], top
    for li, lane in enumerate(lanes):
        c1, c2 = p[lane["colors"][0]], p[lane["colors"][1]]
        gid = f"lane{li}"
        n = len(lane["items"])
        y0, y1 = y + 18, y + head + (n - 1) * row + 4
        out.append(
            f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{c2}"/></linearGradient>'
            f'<rect x="84" y="{y0}" width="3" height="{y1 - y0}" rx="1.5" fill="url(#{gid})"/>'
            f'<rect x="24" y="{y + 2}" width="52" height="24" rx="12" fill="{c1}" fill-opacity=".16" stroke="{c1}" stroke-opacity=".6"/>'
            f'<text x="50" y="{y + 19}" text-anchor="middle" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{c1}">{t(lane["year"])}</text>'
            f'<circle cx="85.5" cy="{y + 14}" r="7" fill="{p["bg1"]}" stroke="{c1}" stroke-width="3"/>'
            f'<text x="104" y="{y + 19}" font-family="{SANS}" font-size="15" font-weight="700" fill="{p["text"]}">{t(lane["title"])}</text>')
        for k, item in enumerate(lane["items"]):
            event, project, desc = item[:3]
            win = len(item) > 3 and item[3]
            iy = y + head + k * row
            frac = k / max(n - 1, 1)
            col = c1 if frac < .5 else c2
            out.append(
                f'<circle cx="85.5" cy="{iy - 4}" r="4.5" fill="{col}"/>'
                f'<text x="104" y="{iy}" font-family="{MONO}" font-size="12" font-weight="700" fill="{col}">{t(event)}</text>'
                f'<text x="316" y="{iy}" font-family="{SANS}" font-size="13" font-weight="600" fill="{p["text"]}">{t(project)}</text>'
                f'<text x="516" y="{iy}" font-family="{MONO}" font-size="11.5" fill="{p["muted"]}">{t(desc)}</text>')
            if win:
                out.append(
                    f'<rect x="{W - 84}" y="{iy - 15}" width="58" height="20" rx="10" fill="{p["gold"]}" fill-opacity=".18" stroke="{p["gold"]}"/>'
                    f'<text x="{W - 55}" y="{iy - 1}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="{p["gold"]}">1ST</text>')
        y += head + n * row + 22
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="bt">
<title id="bt">Build log: hackathons and projects by year</title>
<defs><linearGradient id="bb" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["accent"]}"/><stop offset=".35" stop-color="{p["purple"]}"/><stop offset=".7" stop-color="{p["pink"]}"/><stop offset="1" stop-color="{p["orange"]}"/></linearGradient></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{p["bg1"]}" stroke="{p["border"]}"/>
<rect x="1" y="1" width="{W-2}" height="4" rx="2" fill="url(#bb)"/>
<text x="24" y="38" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="2" fill="{p["accent"]}">OQV://BUILD_LOG</text>
<text x="{W-24}" y="38" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="1" fill="{p["muted"]}">EVENT · PROJECT · WHAT IT DOES</text>
{"".join(out)}
</svg>
"""


def render_divider() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="880" height="12" viewBox="0 0 880 12" role="presentation">
<defs><linearGradient id="d" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">
<stop offset="0" stop-color="#58a6ff"/><stop offset=".33" stop-color="#a371f7"/><stop offset=".66" stop-color="#f778ba"/><stop offset="1" stop-color="#3fb950"/>
<animate attributeName="x1" values="0;1;0" dur="8s" repeatCount="indefinite"/><animate attributeName="x2" values="1;2;1" dur="8s" repeatCount="indefinite"/>
</linearGradient></defs>
<rect x="0" y="4" width="880" height="4" rx="2" fill="url(#d)"/>
</svg>
"""


def main() -> None:
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=-4))).date()  # La Paz time
    data = collect()
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme in PALETTES:
        (assets / f"credential-{theme}.svg").write_text(render_card(theme, data, today), encoding="utf-8")
        (assets / f"buildlog-{theme}.svg").write_text(render_timeline(theme), encoding="utf-8")
    (assets / "divider.svg").write_text(render_divider(), encoding="utf-8")
    print(f"rendered profile assets for {USER}: repos={data['public_repos']} "
          f"followers={data['followers']} avatar={'yes' if data['avatar'] else 'initials'}")


if __name__ == "__main__":
    main()
