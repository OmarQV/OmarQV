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


def render_card(theme: str, data: dict, today: dt.date) -> str:
    p = PALETTES[theme]
    W, H = 880, 336
    t = lambda s: escape(str(s))  # noqa: E731

    # avatar (photo or initials)
    initials = "".join(w[0] for w in CONFIG["name"].split()[:2])
    if data["avatar"]:
        avatar = (f'<image href="{data["avatar"]}" x="56" y="106" width="128" height="128" '
                  f'clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        avatar = (f'<circle cx="120" cy="170" r="64" fill="{p["panel"]}"/>'
                  f'<text x="120" y="182" text-anchor="middle" font-family="{SANS}" font-size="36" '
                  f'font-weight="700" fill="{p["accent"]}">{t(initials)}</text>')

    hues = [p["accent"], p["purple"], p["accent2"], p["orange"]]
    parts = CONFIG["tagline"].split(" × ")
    tagline = f'<tspan fill="{p["muted"]}"> × </tspan>'.join(
        f'<tspan fill="{hues[i % len(hues)]}">{t(w)}</tspan>' for i, w in enumerate(parts))

    rows = []
    for i, (k, v) in enumerate(CONFIG["rows"]):
        y = 184 + i * 25
        rows.append(
            f'<text x="226" y="{y}" font-family="{MONO}" font-size="11.5" fill="{hues[i % len(hues)]}" '
            f'letter-spacing="1">{t(k)}</text>'
            f'<text x="306" y="{y}" font-family="{MONO}" font-size="12.5" fill="{p["text"]}">{t(v)}</text>')

    stats = [
        (data["public_repos"], "PUBLIC REPOS"), (data["followers"], "FOLLOWERS"),
        (CONFIG["hackathons"], "HACKATHONS"), (CONFIG["first_places"], "1ST PLACES"),
    ]
    stat_svg = []
    for i, (val, label) in enumerate(stats):
        cx = 676 + (i % 2) * 96
        cy = 118 + (i // 2) * 66
        stat_svg.append(
            f'<text x="{cx}" y="{cy}" font-family="{SANS}" font-size="26" font-weight="700" '
            f'fill="{[p["accent"], p["purple"], p["pink"], p["gold"]][i]}">{t(val)}</text>'
            f'<text x="{cx}" y="{cy + 17}" font-family="{MONO}" font-size="9.5" letter-spacing="1" '
            f'fill="{p["muted"]}">{t(label)}</text>')

    sync = today.strftime("%d %b %Y").upper()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">{t(CONFIG["name"])} — developer credential</title>
<desc id="desc">{t(CONFIG["tagline"])}. {t(" · ".join(v for _, v in CONFIG["rows"]))}. Status {t(CONFIG["status"])}, latest project {t(CONFIG["latest_project"])}.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["accent"]}"/><stop offset=".5" stop-color="{p["purple"]}"/><stop offset="1" stop-color="{p["accent2"]}"/></linearGradient>
  <linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["accent"]}"/><stop offset=".35" stop-color="{p["purple"]}"/><stop offset=".7" stop-color="{p["pink"]}"/><stop offset="1" stop-color="{p["orange"]}"/></linearGradient>
  <linearGradient id="glow" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["purple"]}" stop-opacity=".22"/><stop offset=".6" stop-color="{p["purple"]}" stop-opacity="0"/></linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["accent"]}" stop-opacity="0"/><stop offset="1" stop-color="{p["accent"]}" stop-opacity=".16"/></linearGradient>
  <pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{p["grid"]}" stroke-opacity=".07"/></pattern>
  <clipPath id="av"><circle cx="120" cy="170" r="64"/></clipPath>
  <clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/></clipPath>
  <style>
    .spin{{transform-origin:120px 170px;animation:spin 18s linear infinite}}
    .scan{{animation:scan 5.5s ease-in-out infinite}}
    .pulse{{animation:pulse 2s ease-in-out infinite}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
    @keyframes scan{{0%{{transform:translateY(-60px)}}100%{{transform:translateY({H}px)}}}}
    @keyframes pulse{{50%{{opacity:.35}}}}
    @media (prefers-reduced-motion:reduce){{.spin,.scan,.pulse{{animation:none}}}}
  </style>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>
  <rect x="0" y="0" width="{W}" height="4" fill="url(#brand)"/>
  <rect class="scan" x="0" y="0" width="{W}" height="60" fill="url(#scan)"/>
</g>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="none" stroke="url(#brand)" stroke-opacity=".7" stroke-width="1.5"/>
<path d="M18 1H90M1 18V90" stroke="{p["accent"]}" stroke-width="2" fill="none" transform="translate(0.5 0.5)"/>
<path d="M{W-90} {H-1}H{W-18}M{W-1} {H-90}V{H-18}" stroke="{p["pink"]}" stroke-width="2" fill="none"/>

<!-- header -->
<text x="32" y="42" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="2" fill="{p["accent"]}">OQV://IDENTITY</text>
<text x="190" y="42" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{p["muted"]}">SMART DEVELOPER CREDENTIAL</text>
<rect x="{W-138}" y="24" width="106" height="26" rx="13" fill="{p["accent2"]}" fill-opacity=".12" stroke="{p["accent2"]}" stroke-opacity=".5"/>
<circle class="pulse" cx="{W-120}" cy="37" r="4" fill="{p["accent2"]}"/>
<text x="{W-108}" y="41" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{p["accent2"]}">VERIFIED</text>
<line x1="32" y1="64" x2="{W-32}" y2="64" stroke="{p["border"]}"/>

<!-- avatar -->
<circle cx="120" cy="170" r="76" fill="none" stroke="url(#ring)" stroke-width="2" stroke-dasharray="3 7" class="spin"/>
<circle cx="120" cy="170" r="68" fill="none" stroke="url(#ring)" stroke-width="3"/>
{avatar}

<!-- identity -->
<text x="224" y="112" font-family="{SANS}" font-size="27" font-weight="800" letter-spacing=".5" fill="url(#brand)">{t(CONFIG["name"])}</text>
<text x="226" y="138" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.2">{tagline}</text>
<line x1="226" y1="156" x2="610" y2="156" stroke="{p["border"]}" stroke-dasharray="2 4"/>
{"".join(rows)}

<!-- stats panel -->
<rect x="650" y="84" width="198" height="190" rx="12" fill="{p["panel"]}" fill-opacity=".85" stroke="{p["border"]}"/>
{"".join(stat_svg)}
<line x1="666" y1="222" x2="832" y2="222" stroke="{p["border"]}"/>
<circle class="pulse" cx="672" cy="241" r="4" fill="{p["accent2"]}"/>
<text x="682" y="245" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1" fill="{p["accent2"]}">{t(CONFIG["status"])}</text>
<text x="666" y="262" font-family="{MONO}" font-size="10" fill="{p["muted"]}">latest › <tspan fill="{p["text"]}">{t(CONFIG["latest_project"])}</tspan></text>

<!-- footer -->
<line x1="32" y1="290" x2="{W-32}" y2="290" stroke="{p["border"]}"/>
{barcode(USER + CONFIG["credential_id"], 32, 302, 18, p["muted"], 150)}
<text x="200" y="316" font-family="{MONO}" font-size="11" letter-spacing="1" fill="{p["muted"]}">ID <tspan fill="{p["text"]}">{t(CONFIG["credential_id"])}</tspan>   ·   github.com/{t(USER)}</text>
<text x="{W-32}" y="316" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="1" fill="{p["muted"]}">LAST SYNC <tspan fill="{p["text"]}">{sync}</tspan></text>
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
