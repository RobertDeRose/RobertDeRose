"""Render banner-dark.svg and banner-light.svg: an animated terminal in the Catppuccin Starship prompt.

Usage: python3 scripts/banner.py [output-dir]   (stamps today's date in the prompt clock)
"""
import sys, os, datetime
out = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = datetime.date.today().strftime("%b %d")
PAL = {
 "dark": dict(base="#24273a", crust="#181926", surface0="#363a4f", surface1="#494d64", surface2="#5b6078", overlay0="#6e738d",
              text="#cad3f5", subtext1="#b8c0e0", subtext0="#a5adcb", blue="#8aadf4", green="#a6da95", mauve="#c6a0f6",
              rosewater="#f4dbd6", sapphire="#7dc4e4", peach="#f5a97f"),
 "light": dict(base="#eff1f5", crust="#dce0e8", surface0="#ccd0da", surface1="#bcc0cc", surface2="#acb0be", overlay0="#9ca0b0",
              text="#4c4f69", subtext1="#5c5f77", subtext0="#6c6f85", blue="#1e66f5", green="#40a02b", mauve="#8839ef",
              rosewater="#dc8a78", sapphire="#209fb5", peach="#fe640b"),
}
FS, CW, SEG_H, LH, W, PADX = 17, 17 * 0.62, 28, 30, 880, 24
ICONS = set("❄▸⎇◷")

def hide_until(t):
    # Visible by default; hidden from 0s until t. Viewers without SMIL see the finished frame.
    return f'<set attributeName="opacity" to="0" begin="0s" dur="{t:.2f}s"/>' if t > 0 else ""

def prompt(p, y, clock, t):
    """Starship 'maison' prompt line 1 at baseline y, revealed at time t."""
    top, x = y - 20, PADX + 42
    parts = [f'<text x="{PADX}" y="{y}" fill="{p["overlay0"]}">╭─</text>',
             f'<circle cx="{x}" cy="{top + SEG_H/2}" r="{SEG_H/2}" fill="{p["surface0"]}"/>']
    segs = [("surface0", [("❄", "mauve")]),
            ("surface1", [("▸ ", "blue"), ("~ ", "text"), ("⎇ ", "green"), ("main", "text")]),
            ("surface2", [("◷ ", "rosewater"), (clock, "text")])]
    for i, (bg, items) in enumerate(segs):
        cx, spans = x + 12, []
        for txt, col in items:
            spans.append(f'<tspan x="{cx:.1f}" fill="{p[col]}">{txt}</tspan>')
            cx += len(txt) * CW + (CW * 0.6 if txt.strip() in ICONS else 0)
        w = cx - x + 6
        parts.append(f'<rect x="{x:.1f}" y="{top}" width="{w:.1f}" height="{SEG_H}" fill="{p[bg]}"/>')
        parts.append(f'<text y="{y}">{"".join(spans)}</text>')
        x += w
        if i + 1 < len(segs):
            parts.append(f'<rect x="{x:.1f}" y="{top}" width="14" height="{SEG_H}" fill="{p[segs[i+1][0]]}"/>')
        parts.append(f'<path d="M{x:.1f} {top} L{x+14:.1f} {top + SEG_H/2} L{x:.1f} {top + SEG_H} Z" fill="{p[bg]}"/>')
    return f'<g>{hide_until(t)}{"".join(parts)}</g>'

def command(p, y, cmd, t, speed=0.06):
    """'╰─$ cmd' with cmd typed out starting at time t. Returns svg, finish time."""
    x0 = PADX + 42
    n = len(cmd)
    end = t + n * speed
    full = n * CW + 24
    vals = ["0"] + [f"{i * CW:.1f}" for i in range(1, n)] + [f"{full:.1f}"]
    keys = ["0"] + [f"{(t + (i - 1) * speed) / end:.4f}" for i in range(1, n + 1)]
    cid = f"c{y}"
    svg = (f'<g>{hide_until(t)}<text x="{PADX}" y="{y}" fill="{p["overlay0"]}">╰─<tspan fill="{p["green"]}" font-weight="700">$</tspan></text>'
           f'<clipPath id="{cid}"><rect x="{x0}" y="{y - 20}" height="{LH}" width="{full:.1f}">'
           f'<animate attributeName="width" begin="0s" dur="{end:.2f}s" values="{";".join(vals)}" keyTimes="{";".join(keys)}" calcMode="discrete"/></rect></clipPath>'
           f'<text x="{x0}" y="{y}" fill="{p["text"]}" clip-path="url(#{cid})">{cmd}</text></g>')
    return svg, end

def line(p, y, spans, t):
    body = "".join(f'<tspan x="{x:.1f}" fill="{p[c]}"{" font-weight=\"700\"" if b else ""}>{s}</tspan>' for x, s, c, b in spans)
    return f'<text y="{y}">{hide_until(t)}{body}</text>'

TREE = [  # prefix, name, description, name color
    ("", "github:RobertDeRose", "", "subtext0"),
    ("├───", "fleet", "", "green"),
    ("│   ├───", "nixstasis", "fleet monitoring, zero inbound ports", "text"),
    ("│   └───", "atomixos", "NixOS for embedded devices", "text"),
    ("└───", "darwin", "", "blue"),
    ("    ├───", "container-compose-plugin", "docker compose for Apple container", "text"),
    ("    ├───", "container-krun-runtime", "libkrun VM runtime for Apple container", "text"),
    ("    └───", "nix-hex-box", "Linux builder for nix-darwin", "text"),
]

for name, p in PAL.items():
    els, y, t = [], 46, 0.0
    els.append(prompt(p, y, STAMP, 0)); y += LH + 4
    s, t = command(p, y, "whoami", 0.6); els.append(s); y += LH
    t += 0.25
    els.append(line(p, y, [(PADX + 42, "Embedded Linux · nix · nix-darwin · IoT · containers", "text", False)], t)); y += LH + 14
    t += 0.4
    els.append(prompt(p, y, STAMP, t)); y += LH + 4
    s, t = command(p, y, "nix flake show github:RobertDeRose", t + 0.4, 0.045); els.append(s); y += LH
    t += 0.3
    desc_x = PADX + 42 + 35 * CW
    for pre, nm, desc, col in TREE:
        nx = PADX + 42 + len(pre) * CW
        spans = [(PADX + 42, pre, "overlay0", False), (nx, nm, col, col in ("green", "blue"))] if pre else [(PADX + 42, nm, col, False)]
        if desc:
            spans.append((desc_x, desc, "subtext0", False))
        els.append(line(p, y, spans, t)); y += LH - 4; t += 0.09
    y += 18; t += 0.3
    els.append(prompt(p, y, STAMP, t)); y += LH + 4
    els.append(f'<g>{hide_until(t)}<text x="{PADX}" y="{y}" fill="{p["overlay0"]}">╰─<tspan fill="{p["green"]}" font-weight="700">$</tspan></text>'
               f'<rect x="{PADX + 42}" y="{y - 15}" width="{CW:.1f}" height="19" fill="{p["text"]}">'
               f'<animate attributeName="opacity" begin="{t:.2f}s" dur="1s" values="1;0" calcMode="discrete" repeatCount="indefinite"/></rect></g>')
    H = y + 26
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>text {{ font-family: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace; font-size: {FS}px; white-space: pre; }}</style>
<rect width="{W}" height="{H}" rx="12" fill="{p["base"]}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="11.5" fill="none" stroke="{p["crust"]}"/>
''' + "\n".join(els) + "\n</svg>\n"
    open(os.path.join(out, f"banner-{name}.svg"), "w").write(svg)
print("ok")
