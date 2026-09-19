"""Placeholder suspension-trainer card illustrations."""

from pathlib import Path

SLUGS = {
    "row": ("#2E6B8A", "ROW"),
    "press": ("#C45C26", "PRESS"),
    "squat": ("#3D7A4A", "SQUAT"),
    "lunge": ("#6B4C9A", "LUNGE"),
    "plank": ("#B4532A", "PLANK"),
    "twist": ("#1F7A6B", "TWIST"),
    "curl": ("#A33B5D", "CURL"),
    "pull": ("#2F5F99", "PULL"),
    "chest-fly": ("#C46B3A", "CHEST FLY"),
    "core-crunch": ("#8A3A3A", "CRUNCH"),
    "hinge": ("#4A6B2E", "HINGE"),
    "jump": ("#C49A1A", "JUMP"),
    "stretch": ("#5A8A9A", "STRETCH"),
    "default": ("#5C6370", "EXERCISE"),
}


def svg_for(slug: str, color: str, label: str) -> str:
    pose = POSES.get(slug, POSES["default"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 400 560" role="img" aria-label="{label}">
  <rect width="400" height="560" rx="28" fill="{color}"/>
  <rect x="18" y="18" width="364" height="524" rx="20" fill="none" stroke="#ffffff" stroke-opacity="0.25" stroke-width="3"/>
  <text x="200" y="52" text-anchor="middle" fill="#ffffff" font-family="Helvetica, Arial, sans-serif" font-size="22" font-weight="700" letter-spacing="3">{label}</text>
  <g fill="none" stroke="#ffffff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">
    {pose}
  </g>
  <circle cx="200" cy="530" r="6" fill="#ffffff" fill-opacity="0.7"/>
</svg>
'''


POSES = {
    "row": """
    <line x1="120" y1="90" x2="280" y2="90"/>
    <line x1="150" y1="90" x2="150" y2="160"/>
    <line x1="250" y1="90" x2="250" y2="160"/>
    <circle cx="200" cy="230" r="22"/>
    <line x1="200" y1="252" x2="200" y2="360"/>
    <line x1="200" y1="290" x2="150" y2="160"/>
    <line x1="200" y1="290" x2="250" y2="160"/>
    <line x1="200" y1="360" x2="160" y2="470"/>
    <line x1="200" y1="360" x2="240" y2="470"/>
    """,
    "press": """
    <line x1="120" y1="90" x2="280" y2="90"/>
    <line x1="150" y1="90" x2="170" y2="210"/>
    <line x1="250" y1="90" x2="230" y2="210"/>
    <circle cx="200" cy="250" r="22"/>
    <line x1="200" y1="272" x2="200" y2="380"/>
    <line x1="200" y1="310" x2="170" y2="210"/>
    <line x1="200" y1="310" x2="230" y2="210"/>
    <line x1="200" y1="380" x2="155" y2="490"/>
    <line x1="200" y1="380" x2="245" y2="490"/>
    """,
    "squat": """
    <line x1="140" y1="90" x2="260" y2="90"/>
    <line x1="170" y1="90" x2="180" y2="200"/>
    <line x1="230" y1="90" x2="220" y2="200"/>
    <circle cx="200" cy="250" r="22"/>
    <line x1="200" y1="272" x2="200" y2="360"/>
    <line x1="200" y1="300" x2="180" y2="200"/>
    <line x1="200" y1="300" x2="220" y2="200"/>
    <line x1="200" y1="360" x2="140" y2="430"/>
    <line x1="200" y1="360" x2="260" y2="430"/>
    <line x1="140" y1="430" x2="130" y2="500"/>
    <line x1="260" y1="430" x2="270" y2="500"/>
    """,
    "lunge": """
    <line x1="150" y1="90" x2="250" y2="90"/>
    <line x1="180" y1="90" x2="185" y2="190"/>
    <line x1="220" y1="90" x2="215" y2="190"/>
    <circle cx="200" cy="230" r="22"/>
    <line x1="200" y1="252" x2="200" y2="340"/>
    <line x1="200" y1="290" x2="185" y2="190"/>
    <line x1="200" y1="290" x2="215" y2="190"/>
    <line x1="200" y1="340" x2="130" y2="500"/>
    <line x1="200" y1="340" x2="270" y2="420"/>
    <line x1="270" y1="420" x2="290" y2="500"/>
    """,
    "plank": """
    <circle cx="320" cy="250" r="20"/>
    <line x1="300" y1="250" x2="120" y2="250"/>
    <line x1="280" y1="250" x2="250" y2="310"/>
    <line x1="250" y1="310" x2="230" y2="310"/>
    <line x1="140" y1="250" x2="90" y2="250"/>
    <line x1="90" y1="250" x2="70" y2="310"/>
    """,
    "twist": """
    <line x1="140" y1="90" x2="260" y2="90"/>
    <circle cx="200" cy="230" r="22"/>
    <line x1="200" y1="252" x2="200" y2="370"/>
    <line x1="200" y1="300" x2="110" y2="250"/>
    <line x1="200" y1="300" x2="300" y2="330"/>
    <line x1="200" y1="370" x2="160" y2="490"/>
    <line x1="200" y1="370" x2="250" y2="490"/>
    """,
    "curl": """
    <line x1="130" y1="90" x2="270" y2="90"/>
    <line x1="160" y1="90" x2="155" y2="200"/>
    <line x1="240" y1="90" x2="245" y2="200"/>
    <circle cx="200" cy="250" r="22"/>
    <line x1="200" y1="272" x2="200" y2="380"/>
    <line x1="200" y1="310" x2="155" y2="200"/>
    <line x1="200" y1="310" x2="245" y2="200"/>
    <line x1="200" y1="380" x2="165" y2="490"/>
    <line x1="200" y1="380" x2="235" y2="490"/>
    """,
    "pull": """
    <line x1="110" y1="90" x2="290" y2="90"/>
    <line x1="140" y1="90" x2="120" y2="200"/>
    <line x1="260" y1="90" x2="280" y2="200"/>
    <circle cx="200" cy="240" r="22"/>
    <line x1="200" y1="262" x2="200" y2="370"/>
    <line x1="200" y1="300" x2="120" y2="200"/>
    <line x1="200" y1="300" x2="280" y2="200"/>
    <line x1="200" y1="370" x2="165" y2="490"/>
    <line x1="200" y1="370" x2="235" y2="490"/>
    """,
    "chest-fly": """
    <line x1="80" y1="140" x2="320" y2="140"/>
    <circle cx="200" cy="250" r="22"/>
    <line x1="200" y1="272" x2="200" y2="380"/>
    <line x1="200" y1="300" x2="90" y2="200"/>
    <line x1="200" y1="300" x2="310" y2="200"/>
    <line x1="200" y1="380" x2="160" y2="490"/>
    <line x1="200" y1="380" x2="240" y2="490"/>
    """,
    "core-crunch": """
    <circle cx="140" cy="280" r="20"/>
    <line x1="160" y1="280" x2="260" y2="300"/>
    <line x1="180" y1="285" x2="210" y2="360"/>
    <line x1="260" y1="300" x2="310" y2="250"/>
    <line x1="260" y1="300" x2="300" y2="360"/>
    """,
    "hinge": """
    <circle cx="150" cy="220" r="22"/>
    <line x1="168" y1="232" x2="250" y2="280"/>
    <line x1="250" y1="280" x2="250" y2="430"/>
    <line x1="210" y1="258" x2="170" y2="330"/>
    <line x1="250" y1="430" x2="200" y2="500"/>
    <line x1="250" y1="430" x2="300" y2="500"/>
    """,
    "jump": """
    <circle cx="200" cy="180" r="22"/>
    <line x1="200" y1="202" x2="200" y2="320"/>
    <line x1="200" y1="240" x2="140" y2="200"/>
    <line x1="200" y1="240" x2="260" y2="200"/>
    <line x1="200" y1="320" x2="150" y2="280"/>
    <line x1="200" y1="320" x2="260" y2="380"/>
    <line x1="80" y1="500" x2="320" y2="500"/>
    """,
    "stretch": """
    <line x1="160" y1="90" x2="240" y2="90"/>
    <circle cx="200" cy="220" r="22"/>
    <line x1="200" y1="242" x2="200" y2="360"/>
    <line x1="200" y1="280" x2="130" y2="160"/>
    <line x1="200" y1="280" x2="280" y2="200"/>
    <line x1="200" y1="360" x2="160" y2="490"/>
    <line x1="200" y1="360" x2="250" y2="490"/>
    """,
    "default": """
    <circle cx="200" cy="220" r="22"/>
    <line x1="200" y1="242" x2="200" y2="360"/>
    <line x1="200" y1="280" x2="140" y2="340"/>
    <line x1="200" y1="280" x2="260" y2="340"/>
    <line x1="200" y1="360" x2="160" y2="490"/>
    <line x1="200" y1="360" x2="240" y2="490"/>
    """,
}


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "static" / "illustrations"
    out.mkdir(parents=True, exist_ok=True)
    for slug, (color, label) in SLUGS.items():
        (out / f"{slug}.svg").write_text(svg_for(slug, color, label))
    print(f"wrote {len(SLUGS)} svgs to {out}")


if __name__ == "__main__":
    main()
