"""Render one Catppuccin card per recent release and rewrite the README block between the releases markers.

Usage: python3 scripts/releases.py   (needs the gh CLI with a token in GH_TOKEN or a logged-in session)
"""
import datetime, hashlib, json, os, re, subprocess

OWNER = "RobertDeRose"
# Active projects only, with descriptions short enough to fit a card.
PROJECTS = {
    "nixstasis": "IoT fleets, zero inbound ports",
    "atomixos": "NixOS for embedded devices",
    "container-krun-runtime": "libkrun runtime for container",
    "container-compose-plugin": "docker compose for container",
    "nix-hex-box": "Linux builder for nix-darwin",
}
MAX_CARDS = 4
CARD_W, CARD_H = 400, 96  # two per row fill the README column; an odd last card spans both
WIDE_W = 2 * CARD_W + 4
CARD_DIR = "cards"

PAL = {
    "dark": dict(base="#24273a", crust="#181926", surface0="#363a4f", text="#cad3f5", subtext0="#a5adcb",
                 overlay1="#8087a2", green="#a6da95", mauve="#c6a0f6", peach="#f5a97f"),
    "light": dict(base="#eff1f5", crust="#dce0e8", surface0="#ccd0da", text="#4c4f69", subtext0="#6c6f85",
                  overlay1="#8c8fa1", green="#40a02b", mauve="#8839ef", peach="#fe640b"),
}


def releases():
    out = subprocess.run(
        ["gh", "repo", "list", OWNER, "--source", "--visibility=public", "--limit", "200",
         "--json", "name,url,latestRelease"],
        check=True, capture_output=True, text=True).stdout
    repos = [r for r in json.loads(out) if r["latestRelease"] and r["name"] in PROJECTS]
    repos.sort(key=lambda r: r["latestRelease"]["publishedAt"], reverse=True)
    return repos[:MAX_CARDS]


def card(p, name, desc, tag, published, w):
    date = published.strftime("%b %d, %Y")
    pill_w = len(tag) * 7.8 + 16
    pill_x = w - 16 - pill_w
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {CARD_H}" width="{w}" height="{CARD_H}">
<style>text {{ font-family: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace; white-space: pre; }}</style>
<rect x="0.5" y="0.5" width="{w - 1}" height="{CARD_H - 1}" rx="10" fill="{p["base"]}" stroke="{p["crust"]}"/>
<text x="18" y="34" font-size="16" font-weight="700"><tspan fill="{p["mauve"]}">❄ </tspan><tspan fill="{p["text"]}">{name}</tspan></text>
<rect x="{pill_x:.1f}" y="17" width="{pill_w:.1f}" height="22" rx="11" fill="{p["green"]}"/>
<text x="{pill_x + pill_w / 2:.1f}" y="32.5" text-anchor="middle" font-size="13" font-weight="700" fill="{p["base"]}">{tag}</text>
<text x="18" y="60" font-size="13" fill="{p["subtext0"]}">{desc}</text>
<text x="18" y="82" font-size="12" fill="{p["overlay1"]}">released {date}</text>
</svg>
'''


def main():
    os.makedirs(CARD_DIR, exist_ok=True)
    for f in os.listdir(CARD_DIR):  # drop cards for projects that fell off the list
        os.remove(os.path.join(CARD_DIR, f))

    repos = releases()
    links = []
    for i, r in enumerate(repos):
        w = WIDE_W if i == len(repos) - 1 and len(repos) % 2 else CARD_W
        rel = r["latestRelease"]
        tag, name = rel["tagName"], r["name"]
        published = datetime.datetime.fromisoformat(rel["publishedAt"].replace("Z", "+00:00")).date()
        files = {}
        for theme, p in PAL.items():
            svg = card(p, name, PROJECTS[name], tag, published, w)
            # Content hash in the filename: GitHub's image proxy caches by URL, so a redesign needs a new URL.
            files[theme] = f"{CARD_DIR}/{name}-{theme}-{hashlib.sha1(svg.encode()).hexdigest()[:8]}.svg"
            with open(files[theme], "w") as f:
                f.write(svg)
        links.append(
            f'<a href="{r["url"]}/releases/tag/{tag}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="{files["dark"]}">'
            f'<img alt="{name} {tag}, released {published:%b %d, %Y}" src="{files["light"]}" width="{w}">'
            f'</picture></a>')

    block = "<!-- releases:start -->\n<p>\n" + "\n".join(links) + "\n</p>\n<!-- releases:end -->"
    with open("README.md") as f:
        readme = f.read()
    readme = re.sub(r"<!-- releases:start -->.*?<!-- releases:end -->", lambda _: block, readme, flags=re.S)
    with open("README.md", "w") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
