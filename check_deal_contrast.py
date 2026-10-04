"""DealFinder SA design-token check. stdlib only: python check_deal_contrast.py
Fails loudly if a text/background pair drops below WCAG AA, which is how
--ink-30 (2.29:1) and --signal-as-button-bg (3.96:1) slipped through."""
import re, sys, pathlib

def lum(c):
    ch = [int(c[i:i+2], 16) / 255 for i in (1, 3, 5)]
    f = lambda u: u / 12.92 if u <= 0.03928 else ((u + 0.055) / 1.055) ** 2.4
    return .2126 * f(ch[0]) + .7152 * f(ch[1]) + .0722 * f(ch[2])

def cr(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)

css = pathlib.Path(__file__).parent.joinpath("assets/css/site.css").read_text("utf-8")
T = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{3,6})", css))
assert T, "no tokens parsed"

CHECKS = [("ink on paper", "ink", "paper", 4.5), ("body on paper", "ink-60", "paper", 4.5),
          ("fine print on paper", "ink-30", "paper", 4.5), ("white on button", "#ffffff", "signal-solid", 4.5),
          ("paper on ink", "paper", "ink", 4.5)]
bad = []
for label, fg, bg, need in CHECKS:
    f = "#ffffff" if fg == "#ffffff" else T.get(fg)
    ratio = cr(f, T[bg])
    ok = ratio >= need
    print(f"{'PASS' if ok else 'FAIL'}  {label:<22} {ratio:5.2f}  (need {need})")
    if not ok:
        bad.append(label)

# display-only token is allowed to sit between 3:1 and 4.5:1 (large-text rule)
d = cr(T["signal"], T["paper"])
print(f"{'PASS' if 3 <= d < 4.5 else 'FAIL'}  {'signal display-only':<22} {d:5.2f}  (need >=3)")
if not (3 <= d < 4.5):
    bad.append("signal display-only")
if "border-radius" in css and "focus-visible" not in css:
    bad.append("radius outside focus ring")

sys.exit("FAILED: " + ", ".join(bad) if bad else 0)
