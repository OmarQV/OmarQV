#!/usr/bin/env python3
"""Render the two self-contained profile hero SVGs (stdlib only)."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PALETTES = {
    "dark": {
        "BG": "#07111E", "PANEL": "#0D1B2D", "PANEL2": "#102338",
        "LINE": "#28435C", "GRID": "#3B5870", "INK": "#EFF7FF",
        "MUTED": "#A9BFD0", "ACCENT": "#83E6D2", "BLUE": "#A6C2FF",
        "GOLD": "#F1C77B", "SHADOW": "#020A13",
    },
    "light": {
        "BG": "#EEF5F9", "PANEL": "#FFFFFF", "PANEL2": "#EAF3F8",
        "LINE": "#C5D9E5", "GRID": "#CFDFE8", "INK": "#14283B",
        "MUTED": "#4A6478", "ACCENT": "#087B74", "BLUE": "#365F9E",
        "GOLD": "#996219", "SHADOW": "#A1BCCB",
    },
}

TEMPLATE = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="470" viewBox="0 0 1120 470" role="img" aria-labelledby="title description">
  <title id="title">Omar Quispe Vargas — OQV</title>
  <desc id="description">Developer profile. AI agents, Web3 and security. Build, trace, verify.</desc>
  <defs>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M 28 0 L 0 0 0 28" fill="none" stroke="__GRID__" stroke-width="0.7" opacity="0.35"/>
    </pattern>
    <linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="__PANEL__"/>
      <stop offset="1" stop-color="__PANEL2__"/>
    </linearGradient>
    <linearGradient id="orbit" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="__ACCENT__"/>
      <stop offset="1" stop-color="__BLUE__"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-15%" width="120%" height="135%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="__SHADOW__" flood-opacity="0.22"/>
    </filter>
    <clipPath id="orbit-clip"><rect x="686" y="72" width="406" height="354" rx="13"/></clipPath>
  </defs>
  <style>
    text { font-family: 'Segoe UI', Arial, sans-serif; }
    .mono { font-family: 'Cascadia Code', 'Consolas', monospace; }
    @media (prefers-reduced-motion: reduce) { .motion { display: none; } }
  </style>

  <rect width="1120" height="470" rx="22" fill="__BG__"/>
  <rect width="1120" height="470" rx="22" fill="url(#grid)"/>
  <rect x="18" y="18" width="1084" height="434" rx="17" fill="none" stroke="__LINE__"/>
  <rect x="18" y="18" width="1084" height="5" rx="2.5" fill="url(#orbit)"/>

  <circle cx="43" cy="46" r="5" fill="__ACCENT__"/>
  <circle class="motion" cx="43" cy="46" r="5" fill="__ACCENT__" opacity="0.7">
    <animate attributeName="r" values="5;10;5" dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0;0.7" dur="2.6s" repeatCount="indefinite"/>
  </circle>
  <text class="mono" x="58" y="50" fill="__MUTED__" font-size="12" letter-spacing="2.2">OQV / DEVELOPER PROFILE</text>
  <text class="mono" x="1073" y="50" fill="__MUTED__" text-anchor="end" font-size="12" letter-spacing="1.1">LA PAZ, BOLIVIA / ONLINE</text>

  <rect x="28" y="72" width="638" height="354" rx="13" fill="url(#wash)" stroke="__LINE__" filter="url(#shadow)"/>
  <path d="M 51 96 h 88" stroke="__ACCENT__" stroke-width="3" stroke-linecap="round"/>
  <text class="mono" x="52" y="126" fill="__ACCENT__" font-size="13" font-weight="700" letter-spacing="2.2">BUILD / TRACE / VERIFY</text>

  <text x="49" y="199" fill="__INK__" font-size="65" font-weight="800" letter-spacing="-2.2">OMAR</text>
  <text x="49" y="263" fill="__INK__" font-size="55" font-weight="800" letter-spacing="-2">QUISPE VARGAS</text>
  <path d="M 52 282 h 568" stroke="__LINE__" stroke-width="1"/>
  <text class="mono" x="52" y="309" fill="__BLUE__" font-size="14" font-weight="700" letter-spacing="1.1">AI AGENTS  ×  WEB3  ×  SECURITY</text>
  <text x="52" y="341" fill="__MUTED__" font-size="17">I build systems whose decisions can be traced</text>
  <text x="52" y="365" fill="__MUTED__" font-size="17">and whose results can be verified.</text>
  <rect x="52" y="385" width="265" height="24" rx="12" fill="__PANEL2__" stroke="__LINE__"/>
  <text class="mono" x="65" y="401" fill="__ACCENT__" font-size="10" font-weight="700" letter-spacing="0.7">INFORMATION SECURITY / UMSA</text>
  <text class="mono" x="620" y="401" fill="__MUTED__" font-size="11" text-anchor="end">ID: OQV://001</text>

  <rect x="686" y="72" width="406" height="354" rx="13" fill="__PANEL__" stroke="__LINE__" filter="url(#shadow)"/>
  <g clip-path="url(#orbit-clip)">
    <rect x="686" y="72" width="406" height="354" fill="url(#grid)" opacity="0.8"/>
    <circle cx="889" cy="248" r="132" fill="none" stroke="__LINE__" stroke-width="1" stroke-dasharray="3 7"/>
    <circle cx="889" cy="248" r="109" fill="none" stroke="__GRID__" stroke-width="1.5"/>
    <circle cx="889" cy="248" r="78" fill="none" stroke="__LINE__" stroke-width="13" opacity="0.65"/>
    <circle cx="889" cy="248" r="78" fill="none" stroke="url(#orbit)" stroke-width="13" stroke-dasharray="196 295" stroke-linecap="round" transform="rotate(-105 889 248)"/>
    <circle cx="889" cy="248" r="52" fill="__PANEL2__" stroke="__ACCENT__" stroke-width="1.5"/>
    <text class="mono" x="889" y="257" fill="__INK__" text-anchor="middle" font-size="30" font-weight="800" letter-spacing="2">OQV</text>
    <g class="motion">
      <path d="M 889 116 V 148" stroke="__ACCENT__" stroke-width="2" opacity="0.65"/>
      <circle cx="889" cy="116" r="5" fill="__ACCENT__"/>
      <animateTransform attributeName="transform" type="rotate" from="0 889 248" to="360 889 248" dur="18s" repeatCount="indefinite"/>
    </g>
    <path d="M 711 183 h 47 M 1020 183 h 47 M 711 313 h 47 M 1020 313 h 47" stroke="__LINE__"/>
    <text class="mono" x="718" y="166" fill="__MUTED__" font-size="10" letter-spacing="1">01 / BUILD</text>
    <text class="mono" x="992" y="166" fill="__MUTED__" font-size="10" letter-spacing="1">02 / TRACE</text>
    <text class="mono" x="719" y="334" fill="__MUTED__" font-size="10" letter-spacing="1">03 / VERIFY</text>
    <text class="mono" x="982" y="334" fill="__MUTED__" font-size="10" letter-spacing="1">04 / SHIP</text>
    <rect class="motion" x="700" y="116" width="378" height="1.5" fill="__ACCENT__" opacity="0.45">
      <animate attributeName="y" values="116;402;116" dur="8s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.45;0" dur="8s" repeatCount="indefinite"/>
    </rect>
  </g>

  <text class="mono" x="43" y="447" fill="__MUTED__" font-size="10" letter-spacing="1.4">SECURE SYSTEMS · PROGRAMMABLE VALUE · DIGITAL EVIDENCE</text>
  <text class="mono" x="1075" y="447" fill="__ACCENT__" text-anchor="end" font-size="10" letter-spacing="1">GITHUB.COM/OMARQV</text>
</svg>
'''

MOBILE_TEMPLATE = r'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="700" viewBox="0 0 640 700" role="img" aria-labelledby="title description">
  <title id="title">Omar Quispe Vargas — OQV</title>
  <desc id="description">Developer in Bolivia. AI agents, Web3 and security. Build, trace, verify.</desc>
  <defs>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="__GRID__" stroke-width="0.7" opacity="0.38"/>
    </pattern>
    <linearGradient id="orbit" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="__ACCENT__"/>
      <stop offset="1" stop-color="__BLUE__"/>
    </linearGradient>
  </defs>
  <style>
    text { font-family: 'Segoe UI', Arial, sans-serif; }
    .mono { font-family: 'Cascadia Code', 'Consolas', monospace; }
    @media (prefers-reduced-motion: reduce) { .motion { display: none; } }
  </style>
  <rect width="640" height="700" rx="22" fill="__BG__"/>
  <rect width="640" height="700" rx="22" fill="url(#grid)"/>
  <rect x="16" y="16" width="608" height="668" rx="16" fill="none" stroke="__LINE__"/>
  <rect x="16" y="16" width="608" height="5" rx="2.5" fill="url(#orbit)"/>

  <circle cx="43" cy="44" r="5" fill="__ACCENT__"/>
  <circle class="motion" cx="43" cy="44" r="5" fill="__ACCENT__" opacity="0.6">
    <animate attributeName="r" values="5;10;5" dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.6;0;0.6" dur="2.6s" repeatCount="indefinite"/>
  </circle>
  <text class="mono" x="58" y="48" fill="__MUTED__" font-size="12" letter-spacing="1.5">OQV / PROFILE</text>
  <text class="mono" x="597" y="48" fill="__MUTED__" text-anchor="end" font-size="12">BOLIVIA / ONLINE</text>

  <rect x="29" y="69" width="582" height="324" rx="14" fill="__PANEL__" stroke="__LINE__"/>
  <path d="M 50 95 h 86" stroke="__ACCENT__" stroke-width="3" stroke-linecap="round"/>
  <text class="mono" x="50" y="125" fill="__ACCENT__" font-size="14" font-weight="700" letter-spacing="2">BUILD / TRACE / VERIFY</text>
  <text x="47" y="207" fill="__INK__" font-size="77" font-weight="800" letter-spacing="-2">OMAR</text>
  <text x="47" y="276" fill="__INK__" font-size="68" font-weight="800" letter-spacing="-2">QUISPE</text>
  <text x="47" y="343" fill="__INK__" font-size="68" font-weight="800" letter-spacing="-2">VARGAS</text>
  <text class="mono" x="49" y="375" fill="__BLUE__" font-size="14" font-weight="700">AI AGENTS  ×  WEB3  ×  SECURITY</text>

  <rect x="29" y="408" width="582" height="235" rx="14" fill="__PANEL__" stroke="__LINE__"/>
  <circle cx="320" cy="519" r="94" fill="none" stroke="__LINE__" stroke-dasharray="3 6"/>
  <circle cx="320" cy="519" r="73" fill="none" stroke="__GRID__" stroke-width="11"/>
  <circle cx="320" cy="519" r="73" fill="none" stroke="url(#orbit)" stroke-width="11" stroke-dasharray="185 274" stroke-linecap="round" transform="rotate(-105 320 519)"/>
  <circle cx="320" cy="519" r="48" fill="__PANEL2__" stroke="__ACCENT__"/>
  <text class="mono" x="320" y="529" fill="__INK__" text-anchor="middle" font-size="29" font-weight="800">OQV</text>
  <g class="motion">
    <circle cx="320" cy="425" r="5" fill="__ACCENT__"/>
    <animateTransform attributeName="transform" type="rotate" from="0 320 519" to="360 320 519" dur="18s" repeatCount="indefinite"/>
  </g>
  <text class="mono" x="49" y="462" fill="__MUTED__" font-size="10">01 / BUILD</text>
  <text class="mono" x="485" y="462" fill="__MUTED__" font-size="10">02 / TRACE</text>
  <text class="mono" x="49" y="591" fill="__MUTED__" font-size="10">03 / VERIFY</text>
  <text class="mono" x="491" y="591" fill="__MUTED__" font-size="10">04 / SHIP</text>
  <text x="320" y="628" fill="__MUTED__" text-anchor="middle" font-size="16">Systems whose results can be verified.</text>

  <text class="mono" x="31" y="672" fill="__MUTED__" font-size="10">INFORMATION SECURITY / UMSA</text>
  <text class="mono" x="606" y="672" fill="__ACCENT__" text-anchor="end" font-size="10">GITHUB.COM/OMARQV</text>
</svg>
'''


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for theme, palette in PALETTES.items():
        for suffix, template in (("", TEMPLATE), ("-mobile", MOBILE_TEMPLATE)):
            svg = template
            for key, value in palette.items():
                svg = svg.replace(f"__{key}__", value)
            if "__" in svg:
                raise ValueError(f"Unfilled SVG token in {theme}{suffix} hero")
            path = ASSETS / f"hero{suffix}-{theme}.svg"
            if not path.exists() or path.read_text(encoding="utf-8") != svg:
                path.write_text(svg, encoding="utf-8")
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
