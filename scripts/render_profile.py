#!/usr/bin/env python3
"""Render the OQV profile assets: smart credential (dark + light SVG)
plus the gradient divider.

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
<desc id="desc">{t(CONFIG["tagline"])}. {t(" · ".join(v for _, v in CONFIG["rows"]))}. Status {t(CONFIG["status"])}, current focus {t(CONFIG["current_focus"])}.</desc>
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
<text x="664" y="260" font-size="10" fill="{h["muted"]}">focus › <tspan fill="{h["amber"]}">{t(CONFIG["current_focus"])}</tspan></text>

<!-- footer -->
<line x1="32" y1="290" x2="{W-32}" y2="290" stroke="{h["dim"]}"/>
{barcode(USER + CONFIG["credential_id"], 32, 302, 18, h["green"], 140)}
<text x="190" y="316" font-size="11" fill="{h["muted"]}">ID <tspan fill="{h["green"]}">{t(CONFIG["credential_id"])}</tspan>  ·  github.com/<tspan fill="{h["text"]}">{t(USER)}</tspan></text>
<text x="{W-32}" y="316" text-anchor="end" font-size="11" fill="{h["muted"]}">last_sync=<tspan fill="{h["cyan"]}">{sync}</tspan></text>
</svg>
"""


def render_mobile_card(data: dict, today: dt.date) -> str:
    """A portrait credential that stays legible at phone width."""
    h = HACK
    t = lambda value: escape(str(value))  # noqa: E731
    words = CONFIG["name"].split()
    first_line = t(" ".join(words[:2]))
    second_line = t(" ".join(words[2:]))
    initials = t("".join(word[0] for word in words[:2]))
    if data["avatar"]:
        avatar = (f'<image href="{data["avatar"]}" x="31" y="91" width="100" height="100" '
                  'clip-path="url(#mobile-avatar)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        avatar = (f'<circle cx="81" cy="141" r="50" fill="{h["bg2"]}"/>'
                  f'<text x="81" y="155" text-anchor="middle" font-size="33" '
                  f'font-weight="700" fill="{h["green"]}">{initials}</text>')
    stats = [
        (data["public_repos"], "REPOS"),
        (data["followers"], "FOLLOWERS"),
        (CONFIG["hackathons"], "HACKATHONS"),
        (CONFIG["first_places"], "1ST PLACES"),
    ]
    stat_svg = "".join(
        f'<text x="{48 + i * 96}" y="415" font-size="23" font-weight="700" fill="{h["cyan"]}">{t(value)}</text>'
        f'<text x="{48 + i * 96}" y="432" font-size="9" fill="{h["muted"]}">{label}</text>'
        for i, (value, label) in enumerate(stats)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="530" viewBox="0 0 420 530" role="img" aria-labelledby="mobile-title mobile-desc">
<title id="mobile-title">{t(CONFIG["name"])} — developer credential</title>
<desc id="mobile-desc">AI agents, Web3 and information security in La Paz. Current focus: {t(CONFIG["current_focus"])}.</desc>
<defs><clipPath id="mobile-avatar"><circle cx="81" cy="141" r="50"/></clipPath></defs>
<style>text{{font-family:{MONO}}}</style>
<rect x="1" y="1" width="418" height="528" rx="14" fill="{h["bg1"]}" stroke="{h["green"]}"/>
<rect x="2" y="2" width="416" height="35" rx="13" fill="#071a10"/>
<circle cx="20" cy="19" r="5" fill="{h["red"]}"/><circle cx="38" cy="19" r="5" fill="{h["amber"]}"/><circle cx="56" cy="19" r="5" fill="{h["green"]}"/>
<text x="210" y="23" text-anchor="middle" font-size="11" fill="{h["muted"]}">OQV://IDENTITY</text>
<text x="28" y="67" font-size="12" fill="{h["green"]}">&gt; ./identity --verify</text>
<circle cx="81" cy="141" r="54" fill="none" stroke="{h["green"]}" stroke-width="2"/>
{avatar}
<text x="150" y="119" font-size="21" font-weight="800" fill="{h["green"]}">{first_line}</text>
<text x="150" y="146" font-size="21" font-weight="800" fill="{h["green"]}">{second_line}</text>
<text x="150" y="176" font-size="11" fill="{h["muted"]}">LA PAZ, BOLIVIA</text>
<line x1="28" y1="205" x2="392" y2="205" stroke="{h["dim"]}"/>
<text x="28" y="228" font-size="11" font-weight="700" fill="{h["cyan"]}">AI AGENTS × WEB3 × INFORMATION SECURITY</text>
<text x="28" y="267" font-size="12" fill="{h["muted"]}">ROLE</text><text x="111" y="267" font-size="13" fill="{h["text"]}">Software Engineer · Builder</text>
<text x="28" y="295" font-size="12" fill="{h["muted"]}">BASE</text><text x="111" y="295" font-size="13" fill="{h["text"]}">La Paz, Bolivia</text>
<text x="28" y="323" font-size="12" fill="{h["muted"]}">TRACK</text><text x="111" y="323" font-size="12.5" fill="{h["text"]}">Informatics · InfoSec (UMSA)</text>
<text x="28" y="351" font-size="12" fill="{h["muted"]}">METHOD</text><text x="111" y="351" font-size="13" fill="{h["text"]}">Build · Trace · Verify</text>
<rect x="28" y="382" width="364" height="67" rx="8" fill="#071a10" stroke="{h["dim"]}"/>
{stat_svg}
<text x="29" y="483" font-size="12" font-weight="700" fill="{h["green"]}">● {t(CONFIG["status"])} <tspan fill="{h["muted"]}"> · FOCUS:</tspan> {t(CONFIG["current_focus"])}</text>
<line x1="28" y1="500" x2="392" y2="500" stroke="{h["dim"]}"/>
<text x="28" y="518" font-size="10" fill="{h["muted"]}">github.com/{t(USER)}</text>
<text x="392" y="518" text-anchor="end" font-size="10" fill="{h["muted"]}">{today.isoformat()}</text>
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
    for theme in ("dark", "light"):
        (assets / f"credential-{theme}.svg").write_text(render_card(theme, data, today), encoding="utf-8")
    (assets / "credential-mobile.svg").write_text(render_mobile_card(data, today), encoding="utf-8")
    (assets / "divider.svg").write_text(render_divider(), encoding="utf-8")
    print(f"rendered profile assets for {USER}: repos={data['public_repos']} "
          f"followers={data['followers']} avatar={'yes' if data['avatar'] else 'initials'}")


if __name__ == "__main__":
    main()
