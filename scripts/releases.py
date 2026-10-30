"""Render one Catppuccin card per recent release and rewrite the README block between the releases markers.

Usage: python3 scripts/releases.py   (needs the gh CLI with a token in GH_TOKEN or a logged-in session)
"""
import datetime, json, os, re, subprocess

OWNER = "RobertDeRose"
# Active projects only, with descriptions short enough to fit a card.
PROJECTS = {
    "nixstasis": "IoT fleets, zero inbound ports",
    "atomixos": "NixOS for embedded devices",
    "container-runtime-krun": "libkrun runtime for container",
    "container-compose-plugin": "docker compose for container",
    "nix-hex-box": "Linux builder for nix-darwin",
}
MAX_CARDS = 6
NEW_DAYS = 14  # releases younger than this get a "new" tag
CARD_W, CARD_H = 268, 92
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


def card(p, name, desc, tag, published, is_new):
    date = published.strftime("%b %d")
    pill_w = len(tag) * 7.8 + 16
    new = (f'<rect x="{CARD_W - 54}" y="14" width="40" height="18" rx="9" fill="{p["peach"]}"/>'
           f'<text x="{CARD_W - 34}" y="27" text-anchor="middle" font-size="11" font-weight="700" fill="{p["base"]}">new</text>'
           if is_new else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CARD_W} {CARD_H}" width="{CARD_W}" height="{CARD_H}">
<style>text {{ font-family: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace; white-space: pre; }}</style>
<rect x="0.5" y="0.5" width="{CARD_W - 1}" height="{CARD_H - 1}" rx="10" fill="{p["base"]}" stroke="{p["crust"]}"/>
<text x="16" y="29" font-size="15" font-weight="700"><tspan fill="{p["mauve"]}">❄ </tspan><tspan fill="{p["text"]}">{name}</tspan></text>
{new}
<text x="16" y="51" font-size="12.5" fill="{p["subtext0"]}">{desc}</text>
<rect x="16" y="62" width="{pill_w:.1f}" height="20" rx="5" fill="{p["green"]}"/>
<text x="{16 + pill_w / 2:.1f}" y="76.5" text-anchor="middle" font-size="13" font-weight="700" fill="{p["base"]}">{tag}</text>
<text x="{16 + pill_w + 12:.1f}" y="76.5" font-size="13" fill="{p["overlay1"]}">◷ {date}</text>
</svg>
'''


def main():
    os.makedirs(CARD_DIR, exist_ok=True)
    for f in os.listdir(CARD_DIR):  # drop cards for projects that fell off the list
        os.remove(os.path.join(CARD_DIR, f))

    today = datetime.date.today()
    links = []
    for r in releases():
        rel = r["latestRelease"]
        tag, name = rel["tagName"], r["name"]
        published = datetime.datetime.fromisoformat(rel["publishedAt"].replace("Z", "+00:00")).date()
        is_new = (today - published).days <= NEW_DAYS
        for theme, p in PAL.items():
            with open(f"{CARD_DIR}/{name}-{theme}.svg", "w") as f:
                f.write(card(p, name, PROJECTS[name], tag, published, is_new))
        links.append(
            f'<a href="{r["url"]}/releases/tag/{tag}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="{CARD_DIR}/{name}-dark.svg">'
            f'<img alt="{name} {tag}, released {published:%b %d, %Y}" src="{CARD_DIR}/{name}-light.svg" width="{CARD_W}">'
            f'</picture></a>')

    block = "<!-- releases:start -->\n<p>\n" + "\n".join(links) + "\n</p>\n<!-- releases:end -->"
    with open("README.md") as f:
        readme = f.read()
    readme = re.sub(r"<!-- releases:start -->.*?<!-- releases:end -->", lambda _: block, readme, flags=re.S)
    with open("README.md", "w") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
