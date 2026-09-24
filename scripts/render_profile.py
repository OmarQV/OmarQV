#!/usr/bin/env python3
"""Generate the profile's language footprint from public GitHub repositories.

Uses only Python's standard library. The chart reports GitHub language bytes,
not skill levels or time spent. A failed API request leaves existing SVGs intact.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OWNER = "OmarQV"
REPOSITORIES = (
    "vector52",
    "stellar-build",
    "auditchain",
    "cocadena-smart-contract",
)

THEMES = {
    "dark": {
        "background": "#07111E", "surface": "#0D1B2D", "line": "#28435C",
        "ink": "#EFF7FF", "muted": "#A9BFD0", "accent": "#83E6D2",
        "track": "#1A344A",
    },
    "light": {
        "background": "#EEF5F9", "surface": "#FFFFFF", "line": "#C5D9E5",
        "ink": "#14283B", "muted": "#4A6478", "accent": "#087B74",
        "track": "#DBE8EF",
    },
}

LANGUAGE_COLORS = {
    "Python": "#E9B85E",
    "TypeScript": "#5A98E3",
    "CSS": "#9B82D4",
    "Solidity": "#56BBAF",
    "JavaScript": "#DBCF63",
    "HTML": "#DB8B69",
    "Rust": "#BC896C",
    "Vyper": "#76CDB1",
}


def github_languages(repository: str) -> dict[str, int]:
    safe_repo = urllib.parse.quote(repository, safe="")
    url = f"https://api.github.com/repos/{OWNER}/{safe_repo}/languages"
    headers = {
        "User-Agent": "OmarQV-profile-chart",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)
    if not isinstance(data, dict) or not all(
        isinstance(name, str) and isinstance(size, int) and size >= 0
        for name, size in data.items()
    ):
        raise ValueError(f"Invalid language data for {repository}")
    return data


def collect() -> Counter[str]:
    totals: Counter[str] = Counter()
    for repository in REPOSITORIES:
        totals.update(github_languages(repository))
    totals.pop("Procfile", None)
    if not totals or sum(totals.values()) == 0:
        raise ValueError("No language bytes returned by GitHub")
    return totals


def render(totals: Counter[str], theme: str) -> str:
    p = THEMES[theme]
    rows = sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:5]
    total_bytes = sum(totals.values())
    max_bytes = rows[0][1]
    body: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="350" '
        'viewBox="0 0 1120 350" role="img" aria-labelledby="title desc">',
        '<title id="title">OQV code footprint</title>',
        '<desc id="desc">Language bytes in four selected public repositories, '
        'generated from the GitHub Languages API.</desc>',
        '<style>text{font-family:Segoe UI,Arial,sans-serif}'
        '.mono{font-family:Cascadia Code,Consolas,monospace}</style>',
        f'<rect width="1120" height="350" rx="18" fill="{p["background"]}"/>',
        f'<rect x="18" y="18" width="1084" height="314" rx="12" '
        f'fill="{p["surface"]}" stroke="{p["line"]}"/>',
        f'<circle cx="48" cy="54" r="5" fill="{p["accent"]}"/>',
        f'<text class="mono" x="63" y="59" fill="{p["accent"]}" '
        'font-size="13" font-weight="700" letter-spacing="1.4">OQV / CODE FOOTPRINT</text>',
        f'<text class="mono" x="1074" y="59" text-anchor="end" '
        f'fill="{p["muted"]}" font-size="11" letter-spacing="0.8">'
        '4 SELECTED PUBLIC REPOSITORIES</text>',
        f'<path d="M 44 78 H 1076" stroke="{p["line"]}"/>',
    ]
    for index, (language, size) in enumerate(rows):
        y = 116 + index * 42
        bar_width = max(3, round(676 * size / max_bytes))
        share = size / total_bytes * 100
        color = LANGUAGE_COLORS.get(language, p["accent"])
        body.extend(
            [
                f'<text class="mono" x="47" y="{y}" fill="{p["ink"]}" '
                f'font-size="13" font-weight="700">{escape(language)}</text>',
                f'<rect x="257" y="{y - 12}" width="676" height="14" '
                f'rx="7" fill="{p["track"]}"/>',
                f'<rect x="257" y="{y - 12}" width="{bar_width}" height="14" '
                f'rx="7" fill="{color}"/>',
                f'<text class="mono" x="1073" y="{y}" text-anchor="end" '
                f'fill="{p["ink"]}" font-size="13" font-weight="700">{share:.1f}%</text>',
            ]
        )
    body.extend(
        [
            f'<path d="M 44 308 H 1076" stroke="{p["line"]}"/>',
            f'<text class="mono" x="47" y="326" fill="{p["muted"]}" '
            'font-size="10">GITHUB LANGUAGES API · BYTES OF CODE, NOT PROFICIENCY</text>',
            f'<text class="mono" x="1073" y="326" text-anchor="end" '
            f'fill="{p["accent"]}" font-size="10">BUILD · TRACE · VERIFY</text>',
            '</svg>',
        ]
    )
    return "\n".join(body) + "\n"


def render_mobile(totals: Counter[str], theme: str) -> str:
    p = THEMES[theme]
    rows = sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:5]
    total_bytes = sum(totals.values())
    max_bytes = rows[0][1]
    body: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="490" '
        'viewBox="0 0 640 490" role="img" aria-labelledby="title desc">',
        '<title id="title">OQV code footprint</title>',
        '<desc id="desc">Language bytes in four selected public repositories, '
        'generated from the GitHub Languages API.</desc>',
        '<style>text{font-family:Segoe UI,Arial,sans-serif}'
        '.mono{font-family:Cascadia Code,Consolas,monospace}</style>',
        f'<rect width="640" height="490" rx="18" fill="{p["background"]}"/>',
        f'<rect x="16" y="16" width="608" height="458" rx="12" '
        f'fill="{p["surface"]}" stroke="{p["line"]}"/>',
        f'<circle cx="40" cy="47" r="5" fill="{p["accent"]}"/>',
        f'<text class="mono" x="55" y="52" fill="{p["accent"]}" '
        'font-size="13" font-weight="700">OQV / CODE FOOTPRINT</text>',
        f'<text class="mono" x="590" y="52" text-anchor="end" '
        f'fill="{p["muted"]}" font-size="11">4 PUBLIC REPOS</text>',
        f'<path d="M 38 72 H 602" stroke="{p["line"]}"/>',
    ]
    for index, (language, size) in enumerate(rows):
        y = 113 + index * 67
        bar_width = max(3, round(552 * size / max_bytes))
        share = size / total_bytes * 100
        color = LANGUAGE_COLORS.get(language, p["accent"])
        body.extend(
            [
                f'<text class="mono" x="42" y="{y}" fill="{p["ink"]}" '
                f'font-size="16" font-weight="700">{escape(language)}</text>',
                f'<text class="mono" x="594" y="{y}" text-anchor="end" '
                f'fill="{p["ink"]}" font-size="16" font-weight="700">{share:.1f}%</text>',
                f'<rect x="42" y="{y + 12}" width="552" height="16" '
                f'rx="8" fill="{p["track"]}"/>',
                f'<rect x="42" y="{y + 12}" width="{bar_width}" height="16" '
                f'rx="8" fill="{color}"/>',
            ]
        )
    body.extend(
        [
            f'<path d="M 38 448 H 602" stroke="{p["line"]}"/>',
            f'<text class="mono" x="40" y="466" fill="{p["muted"]}" '
            'font-size="10">GITHUB API · CODE BYTES, NOT PROFICIENCY</text>',
            '</svg>',
        ]
    )
    return "\n".join(body) + "\n"


def main() -> None:
    totals = collect()
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        for suffix, renderer in (("", render), ("-mobile", render_mobile)):
            svg = renderer(totals, theme)
            path = ASSETS / f"footprint{suffix}-{theme}.svg"
            if not path.exists() or path.read_text(encoding="utf-8") != svg:
                path.write_text(svg, encoding="utf-8")
            print(f"{path.relative_to(ROOT)}: {', '.join(totals)}")


if __name__ == "__main__":
    main()
