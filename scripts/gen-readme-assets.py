#!/usr/bin/env python3
"""README visuals for dsh-origin-rvc-check — derived from the plugin's real pipeline.

Two figures, both read off the shipped material rather than a generic template:

  hero 1440x576 (Pillow, 4 files: zh/en x light/dark)
      A balance for the one arithmetic the plugin actually performs. Left pan:
      FOB - VNM = 400 - 180 = 220. Right pan: declared RVC x FOB = 70% x 400 =
      280. The beam tips, the banner states the 15.00 percentage-point gap
      against the 0.50 tolerance, and the finding strip quotes the real report
      line for row 1 field rvc. Below it: issues[] 1 / skipped[] 2 and the
      verdict line that stays with the reviewer.

  flow 1100x660 (hand-written SVG, 2 files: light/dark)
      A calculation workbench, not a row of boxes: the rule pack sits above the
      bench with all seven rules and their run status; the left card is the
      read-only register after parseMaterial; the centre card is the formula
      gate (netValue / FOB x 100 = 55.00 against the declared 70.00) drawn as a
      0-100 ruler; the right card is the load-time severity staircase
      (direct -> error, derived-from-principle -> warn,
      institutional-configuration -> info); the bottom band is the two report
      channels issues[] and skipped[].

Text values come from the repository's own fixture and rule pack, not from
imagination:
  tests/fixtures/OR-002/OR-002-unsafe.json
      agreement RCEP, product 某型电子元件, fob 400, row 1: vnm 180,
      netValue 220, rvc 70.00, origin 日本, criteria RVC, description
      某型电子元件.
  rules/origin-rvc-check.yaml
      OR-001..OR-007 check kinds, fields, severities; threshold 0 and
      values [] ship unset, so OR-003 / OR-005 report themselves in skipped.
  a real run of lib/index.mjs against that fixture
      issues[] 1: OR-002 warn, row 1 field rvc, "填报 70 ... 应为 55";
      skipped[] 2: OR-003 threshold, OR-005 values.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import math
import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

RADIUS = 22
SHADOW = 26

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card_edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a",
        pill="#ece7f9", band="#f5f2fb", grid="#e7e4f0",
        mark="#b45309", mark_bg="#fdf3e9",
        shadow=(32, 26, 64), glow2="#7a68c9",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", card_edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950",
        pill="#242d42", band="#202839", grid="#262f42",
        mark="#d9a441", mark_bg="#2a2216",
        shadow=(0, 0, 0), glow2="#8496f5",
    ),
}

FONT_FILES = {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD,
              "mono": FONT_MONO, "mono_bold": FONT_MONO_BOLD}


def font(size: int, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.15 * (y / h) + 0.85 * (y / h) ** 1.35
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: tuple,
         alpha: int = 40) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(9, 0, -1):
        rr = r * i / 9
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 10)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def card(img: Image.Image, box: tuple, s: dict, radius: int = RADIUS,
         shadow: int = SHADOW, fill: str | None = None,
         edge: str | None = None) -> Image.Image:
    """A soft-shadowed rounded card on the gradient background."""
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -3):
        sd.rounded_rectangle([x0 - i // 5, y0 + i // 2, x1 + i // 5, y1 + i],
                             radius=radius + i // 5,
                             fill=s["shadow"] + (int(9 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["card_edge"]), width=2)
    return base.convert("RGB")


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str) -> float:
    return _SCRATCH.textlength(text, font=font(int(round(size)), kind))


def require_w(text: str, size: int, kind: str, max_w: float, what: str) -> None:
    """Fail loudly instead of shipping a clipped label."""
    w = measure(text, size, kind)
    if w > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs {w:.1f}px > {max_w}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: {text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> tuple[int, int]:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 30), int(y + h)


def chip(img: Image.Image, xy: tuple[int, int], text: str, fg: str, bg: str,
         size: int = 11, kind: str = "cjk_bold", padx: int = 9,
         height: int = 20) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + padx * 2, y + height],
                        radius=height // 2, fill=hx(bg))
    d.text((x + padx, y + height / 2), text, font=f, fill=hx(fg), anchor="lm")
    return int(w + padx * 2)


def dash_line(d: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int],
              color: str, width: int = 2, dash: int = 7, gap: int = 5) -> None:
    dist = math.hypot(b[0] - a[0], b[1] - a[1])
    n = int(dist // (dash + gap)) + 1
    width = max(1, int(round(width)))
    for i in range(n):
        t0 = i * (dash + gap) / dist
        t1 = min((i * (dash + gap) + dash) / dist, 1.0)
        if t0 >= 1:
            break
        d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
               fill=hx(color), width=width)


# --------------------------------------------------------------------------- hero
# Left column copy plus the labels used inside the balance panel. The numbers
# are the OR-002-unsafe fixture values; the finding text is a compression of
# the report line produced by lib/index.mjs for that fixture.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 核查器",
        value=["把 RVC 算式重算一遍", "差异落到行号与栏名"],
        sub=["按扣减法逐行重算区域价值成分；",
             "门槛与词表未配置就进 skipped，绝不静默通过。"],
        meta="OR-001…OR-007 · 规则包 2026.1 · issues[] / skipped[]",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        gate="算式闸门 · OR-002",
        reg="RCEP · 某型电子元件",
        nums="FOB 400 · VNM 180 · netValue 220",
        banner="Δ 15.00 个百分点 > 容差 0.50",
        banner_r="→ OR-002 warn",
        pleft="FOB − VNM", pleft_d="400 − 180 = 220",
        pright="RVC × FOB", pright_d="70% × 400 = 280",
        found="第 1 行「rvc」填报 70，按 netValue ÷ fob × 100 应为 55",
        issues="issues[] 1", skipped="skipped[] 2",
        verdict="结论留给审核人",
        note="只列差异 · 不判原产资格 · 原件永不修改",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · checker",
        value=["Recompute the RVC formula", "differences land on a cell"],
        sub=["Deduction-method arithmetic, row by row;",
             "unset threshold or vocabulary reports in skipped."],
        meta="OR-001…OR-007 · ruleset 2026.1 · issues[] / skipped[]",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        gate="FORMULA GATE · OR-002",
        reg="RCEP · some electronic component",
        nums="FOB 400 · VNM 180 · net value 220",
        banner="Δ 15.00 pp > tolerance 0.50",
        banner_r="→ OR-002 warn",
        pleft="FOB − VNM", pleft_d="400 − 180 = 220",
        pright="RVC × FOB", pright_d="70% × 400 = 280",
        found="Row 1 · rvc: declared 70, netValue ÷ fob × 100 gives 55",
        issues="issues[] 1", skipped="skipped[] 2",
        verdict="the verdict stays human",
        note="differences only · no origin verdict · the original is never modified",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    H = HERO[lang]
    W, HT = 1440, 576
    img = gradient(W, HT, s["bg_from"], s["bg_to"])
    img = glow(img, 1180, 20, 420, hx(s["accent"]),
               24 if skin == "light" else 38)
    img = glow(img, 80, 580, 300, hx(s["glow2"]),
               10 if skin == "light" else 16)

    d = ImageDraw.Draw(img)
    m = 64
    col_w = 596

    # ---- left column: kicker / title / value / sub / meta / footer -----------
    pill(img, (m, 56), H["kicker"], s, size=17)
    d = ImageDraw.Draw(img)
    d.line([m, 110, m + 4, 172], fill=hx(s["accent"]), width=4)

    title = "dsh-origin-rvc-check"
    title_size = fit(title, "mono_bold", col_w - 18, 58, 48)
    d.text((m + 14, 110), title, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))

    vf = fit_lines(H["value"], "cjk_bold", col_w, 42, 34)
    for i, line in enumerate(H["value"]):
        require_w(line, vf, "cjk_bold", col_w, "hero value")
        d.text((m, 208 + i * 56), line, font=font(vf, "cjk_bold"),
               fill=hx(s["text"]))

    for i, line in enumerate(H["sub"]):
        require_w(line, 22, "cjk", col_w, "hero sub")
        d.text((m + 1, 340 + i * 34), line, font=font(22, "cjk"),
               fill=hx(s["sub"]))

    require_w(H["meta"], 19, "cjk", col_w, "hero meta")
    require_w(H["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 430), H["meta"], font=font(19, "cjk"), fill=hx(s["faint"]))
    d.line([m + 1, 480, m + col_w - 4, 480], fill=hx(s["grid"]), width=2)
    d.text((m + 1, 494), H["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- right: balance panel ------------------------------------------------
    img = card(img, (688, 40, 1376, 540), s, radius=RADIUS, shadow=SHADOW)
    d = ImageDraw.Draw(img)

    d.text((712, 58), H["gate"], font=font(15, "cjk_bold"),
           fill=hx(s["accent"]))
    chip(img, (1290, 52), "warn", s["accent"], s["pill"], size=11)
    d = ImageDraw.Draw(img)

    d.text((712, 86), H["reg"], font=font(13, "cjk"), fill=hx(s["sub"]))
    require_w(H["reg"], 13, "cjk", 380, "hero register")
    nw = measure(H["nums"], 11.5, "mono")
    require_w(H["nums"], 11.5, "mono", 300, "hero numbers")
    d.text((1352 - nw, 88), H["nums"], font=font(11, "mono"),
           fill=hx(s["faint"]))
    d.line([712, 112, 1352, 112], fill=hx(s["grid"]), width=2)

    # the gap banner
    d.rounded_rectangle([712, 118, 1352, 150], radius=10, fill=hx(s["mark_bg"]))
    d.text((724, 124), H["banner"], font=font(14, "cjk_bold"),
           fill=hx(s["mark"]))
    require_w(H["banner"], 14, "cjk_bold", 470, "hero banner")
    bw = measure(H["banner_r"], 12, "cjk_bold")
    d.text((1340 - bw, 126), H["banner_r"], font=font(12, "cjk_bold"),
           fill=hx(s["mark"]))

    # the balance: beam, strings, pans, stand
    pivot = (1032, 200)
    left = (822, 182)
    right = (1242, 218)
    d.line([pivot, (1032, 372)], fill=hx(s["sub"]), width=5)
    d.rounded_rectangle([972, 372, 1092, 386], radius=7, fill=hx(s["sub"]))
    d.line([left, (left[0], 232)], fill=hx(s["sub"]), width=2)
    d.line([right, (right[0], 268)], fill=hx(s["sub"]), width=2)
    d.line([left, (left[0] - 58, 232)], fill=hx(s["faint"]), width=1)
    d.line([left, (left[0] + 58, 232)], fill=hx(s["faint"]), width=1)
    d.line([right, (right[0] - 58, 268)], fill=hx(s["faint"]), width=1)
    d.line([right, (right[0] + 58, 268)], fill=hx(s["faint"]), width=1)

    def pan(cx: int, top: int) -> None:
        poly = [(cx - 75, top), (cx + 75, top),
                (cx + 55, top + 20), (cx - 55, top + 20)]
        d.polygon(poly, fill=hx(s["band"]), outline=hx(s["card_edge"]))
        d.line([(cx - 75, top), (cx + 75, top)], fill=hx(s["accent"]), width=2)

    pan(822, 232)
    pan(1242, 268)

    d.line([left, right], fill=hx(s["text"]), width=6)
    d.ellipse([left[0] - 6, left[1] - 6, left[0] + 6, left[1] + 6],
              fill=hx(s["accent"]))
    d.ellipse([right[0] - 6, right[1] - 6, right[0] + 6, right[1] + 6],
              fill=hx(s["accent"]))
    d.ellipse([pivot[0] - 10, pivot[1] - 10, pivot[0] + 10, pivot[1] + 10],
              fill=hx(s["accent"]))
    dash_line(d, (1032, 210), (1032, 258), s["faint"], width=1.5)

    d.text((822, 280), "220", font=font(26, "cjk_bold"),
           fill=hx(s["accent"]), anchor="ms")
    d.text((822, 302), H["pleft"], font=font(12, "cjk"), fill=hx(s["sub"]),
           anchor="ms")
    d.text((822, 320), H["pleft_d"], font=font(11, "mono"), fill=hx(s["faint"]),
           anchor="ms")
    d.text((1242, 316), "280", font=font(26, "cjk_bold"),
           fill=hx(s["mark"]), anchor="ms")
    d.text((1242, 338), H["pright"], font=font(12, "cjk"), fill=hx(s["sub"]),
           anchor="ms")
    d.text((1242, 356), H["pright_d"], font=font(11, "mono"), fill=hx(s["faint"]),
           anchor="ms")

    # finding strip: the real OR-002 line for row 1 field rvc
    d.rounded_rectangle([712, 402, 1352, 444], radius=12, fill=hx(s["band"]))
    chip(img, (724, 412), "OR-002", s["accent"], s["pill"], size=11,
         kind="mono_bold")
    d = ImageDraw.Draw(img)
    require_w(H["found"], 12.5, "cjk", 490, "hero finding")
    d.text((792, 414), H["found"], font=font(12, "cjk"), fill=hx(s["text"]))
    chip(img, (1290, 412), "warn", s["accent"], s["pill"], size=11)
    d = ImageDraw.Draw(img)

    d.text((712, 462), H["issues"], font=font(13, "cjk_bold"),
           fill=hx(s["accent"]))
    d.text((812, 462), H["skipped"], font=font(13, "cjk_bold"),
           fill=hx(s["sub"]))
    d.text((1352, 462), H["verdict"], font=font(13, "cjk_bold"),
           fill=hx(s["accent2"]), anchor="ra")
    require_w(H["verdict"], 13, "cjk_bold", 200, "hero verdict")
    require_w(H["note"], 11.5, "cjk", 600, "hero note")
    d.text((712, 492), H["note"], font=font(11, "cjk"), fill=hx(s["faint"]))

    name = f"dsh-origin-rvc-check-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}x{HT})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", edge="#e6e2ef", band="#f5f2fb", band2="#faf8fe",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a", amber="#b45309",
        amber_bg="#fdf3e9", rule="#dcd8ea", grid="#e7e4f0",
        pill="#ece7f9", shadow="0.10",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", edge="#2e374b", band="#202839", band2="#1e2534",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950", amber="#d9a441",
        amber_bg="#2a2216", rule="#2b3348", grid="#262f42",
        pill="#242d42", shadow="0.45",
    ),
}

FONT_CSS_CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
                "'Source Han Sans SC',sans-serif")
FONT_CSS_MONO = ("'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace")

# (id, severity, check kind and field, run status in the OR-002 fixture run)
RULES = [
    ("OR-001", "warn", "headerPresence · agreement+product", "ok"),
    ("OR-002", "warn", "formula · rvc ← netValue / fob", "issue"),
    ("OR-003", "info", "thresholdBelow · rvc · threshold 0", "skip"),
    ("OR-004", "warn", "presence · origin", "ok"),
    ("OR-005", "info", "enum · criteria · values [ ]", "skip"),
    ("OR-006", "warn", "unique · itemNo", "ok"),
    ("OR-007", "warn", "containsAny · description", "ok"),
]


def svg_measure(text: str, size: float, mono: bool, bold: bool) -> float:
    kind = "mono" if mono else "cjk"
    if bold:
        kind += "_bold"
    return measure(text, size, kind)


def check_svg(text: str, size: float, maxw: float, mono: bool, bold: bool,
              what: str) -> None:
    w = svg_measure(text, size, mono, bold)
    if w > maxw - 2:
        raise SystemExit(
            f"FATAL: flow text overflows {maxw}px ({w:.1f}): {what} {text!r}")


def stext(x: float, y: float, text: str, size: float, fill: str,
          mono: bool = False, bold: bool = False, anchor: str = "start",
          opacity: float | None = None) -> str:
    fam = FONT_CSS_MONO if mono else FONT_CSS_CJK
    weight = ' font-weight="700"' if bold else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<text x="{x:g}" y="{y:g}" fill="{fill}" font-family="{fam}" '
            f'font-size="{size:g}"{weight} text-anchor="{anchor}"{op}>'
            f'{escape(text)}</text>')


def srect(x: float, y: float, w: float, h: float, rx: float, fill: str,
          stroke: str | None = None, sw: float = 1.2,
          dash: str | None = None, shadow: bool = False) -> str:
    stroke_attr = (f' stroke="{stroke}" stroke-width="{sw:g}"'
                   if stroke else "")
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    filt = ' filter="url(#soft)"' if shadow else ""
    return (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'rx="{rx:g}" fill="{fill}"{stroke_attr}{dash_attr}{filt}/>')


def spath(d: str, stroke: str, width: float = 1.6, dash: str | None = None,
          marker: bool = False) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    mark = ' marker-end="url(#arr)"' if marker else ""
    return (f'<path d="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width:g}" stroke-linecap="round"'
            f'{dash_attr}{mark}/>')


def scallout(x: float, y: float, label: str, size: float,
             fg: str, bg: str, mono: bool = False) -> tuple[str, float]:
    padx = 8.0
    tw = svg_measure(label, size, mono, True)
    sw = tw + padx * 2
    h = size + 10
    body = (srect(x, y, sw, h, h / 2, bg)
            + stext(x + padx, y + h / 2 + size * 0.35, label, size, fg,
                    mono=mono, bold=True))
    return body, sw


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    E: list[str] = []
    E.append('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
             'viewBox="0 0 1100 660" role="img" aria-label="dsh-origin-rvc-check '
             '结构图：规则包、只读台账、算式闸门、依据封顶阶梯与 issues/skipped 两条报告通道">')
    E.append('<title>dsh-origin-rvc-check 核算台</title>')
    E.append('<defs>')
    E.append(f'<linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">'
             f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
             f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    E.append(f'<filter id="soft" x="-30%" y="-30%" width="160%" height="170%">'
             f'<feDropShadow dx="0" dy="7" stdDeviation="9" '
             f'flood-color="#16122c" flood-opacity="{s["shadow"]}"/></filter>')
    E.append(f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
             f'markerWidth="6.4" markerHeight="6.4" orient="auto-start-reverse">'
             f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    E.append('</defs>')
    E.append('<rect width="1100" height="660" fill="url(#bg)"/>')

    # ---- header -------------------------------------------------------------
    E.append(stext(44, 54, "dsh-origin-rvc-check", 28, s["text"], mono=True,
                   bold=True))
    check_svg("dsh-origin-rvc-check", 28, 600, True, True, "title")
    sub = "origin_rvc_check：一份台账 × 一条算式 × 七条规则；差异回到行号与栏名。"
    check_svg(sub, 15, 760, False, False, "subtitle")
    E.append(stext(44, 82, sub, 15, s["sub"]))

    lab1 = "rules 2026.1 · 7 条"
    w1 = svg_measure(lab1, 11.5, False, True) + 20
    lab2 = "read-only"
    w2 = svg_measure(lab2, 11, True, True) + 20
    x2 = 1056 - w2
    x1 = x2 - 8 - w1
    E.append(srect(x1, 32, w1, 26, 13, s["band"]))
    E.append(stext(x1 + 10, 49.2, lab1, 11.5, s["accent"], bold=True))
    E.append(srect(x2, 32, w2, 26, 13, s["band"]))
    E.append(stext(x2 + 10, 49.2, lab2, 11, s["sub"], mono=True, bold=True))

    # ---- rule pack ----------------------------------------------------------
    E.append(srect(44, 104, 1012, 136, 20, s["panel"], s["edge"], 1.5,
                   shadow=True))
    check_svg("② 规则包 · 加载期校验", 14.5, 210, False, True, "rules title")
    E.append(stext(62, 128, "② 规则包 · 加载期校验", 14.5, s["text"], bold=True))
    p = "rules/origin-rvc-check.yaml · 2026.1"
    check_svg(p, 12, 360, True, False, "rules path")
    E.append(stext(258, 128, p, 12, s["sub"], mono=True))
    chip_body, _cw = scallout(936, 112, "7 条 · 固定版本", 11, s["accent"],
                              s["pill"])
    E.append(chip_body)

    plates = [(60, 144), (310, 144), (560, 144), (810, 144),
              (60, 188), (310, 188), (560, 188)]
    for idx, (rule, sev, desc, status) in enumerate(RULES):
        x, y = plates[idx]
        edge = s["amber"] if status == "issue" else s["edge"]
        sw = 1.6 if status == "issue" else 1.1
        dash = "5 4" if status == "skip" else None
        E.append(srect(x, y, 238, 38, 10, s["band"], edge, sw, dash=dash))
        check_svg(rule, 13.5, 70, True, True, "rule id")
        E.append(stext(x + 12, y + 17, rule, 13.5, s["text"], mono=True,
                       bold=True))
        sev_fg = s["accent"] if sev == "warn" else s["faint"]
        E.append(scallout(x + 70, y + 5, sev, 11, sev_fg, s["panel"])[0])
        check_svg(desc, 11, 212, True, False, "rule desc")
        E.append(stext(x + 12, y + 33, desc, 11, s["sub"], mono=True))
        if status == "skip":
            E.append(f'<circle cx="{x + 222}" cy="{y + 19}" r="5" fill="none" '
                     f'stroke="{s["faint"]}" stroke-width="1.6"/>')
        else:
            fill = s["accent2"] if status == "ok" else s["amber"]
            E.append(f'<circle cx="{x + 222}" cy="{y + 19}" r="5" '
                     f'fill="{fill}"/>')

    # ---- ledger -------------------------------------------------------------
    E.append(srect(44, 252, 294, 254, 20, s["panel"], s["edge"], 1.5,
                   shadow=True))
    check_svg("① 材料 → 台账", 14.5, 120, False, True, "ledger title")
    E.append(stext(62, 276, "① 材料 → 台账", 14.5, s["text"], bold=True))
    E.append(scallout(250, 262, "JSON/YAML", 11, s["accent"], s["band"],
                      mono=True)[0])
    E.append(stext(62, 296, "parseMaterial · 只读 · 别名归一", 11, s["faint"]))
    check_svg("parseMaterial · 只读 · 别名归一", 11, 244, False, False,
              "ledger subtitle")

    def field(label: str, value: str, x: float, y: float, value_fill: str | None = None,
              value_mono: bool = True) -> None:
        check_svg(label, 11, 112, True, False, "field label")
        E.append(stext(x, y, label, 11, s["faint"], mono=True))
        check_svg(value, 13, 112, value_mono, False, "field value")
        E.append(stext(x, y + 16, value, 13, value_fill or s["text"],
                       mono=value_mono))

    field("agreement", "RCEP", 62, 318)
    field("fob", "400", 200, 318)
    field("product", "某型电子元件", 62, 352, value_mono=False)
    field("currency", "USD", 200, 352)
    E.append(f'<line x1="62" y1="382" x2="320" y2="382" stroke="{s["rule"]}"/>')
    E.append(stext(62, 400, "rows[0] · 料件 1", 11.5, s["faint"]))

    # the one cell read by OR-002: a fill behind the text plus a left rule, so
    # no border ever crosses the 11px label
    E.append(srect(57, 461, 129, 37, 9, s["amber_bg"]))
    E.append(srect(57, 461, 4, 37, 2, s["amber"]))
    field("序号", "1", 62, 414)
    field("原产国", "日本", 200, 414, value_mono=False)
    field("非原产材料价值", "180", 62, 442)
    field("净价值", "220", 200, 442)
    field("区域价值成分", "70.00", 62, 470, value_fill=s["amber"])
    field("原产地标准", "RVC", 200, 470)

    # ---- formula gate -------------------------------------------------------
    E.append(srect(354, 252, 406, 254, 20, s["panel"], s["edge"], 1.5,
                   shadow=True))
    check_svg("③ 算式闸门", 14.5, 110, False, True, "formula title")
    E.append(stext(372, 276, "③ 算式闸门", 14.5, s["text"], bold=True))
    check_svg("OR-002 · formula", 11.5, 130, True, False, "formula tag")
    E.append(stext(470, 276, "OR-002 · formula", 11.5, s["accent"], mono=True))

    f1 = "RVC = 净价值 ÷ FOB × 100"
    check_svg(f1, 16.5, 368, False, True, "formula")
    E.append(stext(372, 304, f1, 16.5, s["text"], bold=True))
    f2 = "（400 − 180）÷ 400 × 100 = 55.00"
    check_svg(f2, 13, 368, True, False, "substitution")
    E.append(stext(372, 330, f2, 13, s["sub"], mono=True))

    E.append(stext(372, 356, "重算 55.00", 13, s["accent"], bold=True))
    E.append(stext(742, 356, "填报 70.00", 13, s["amber"], bold=True,
                   anchor="end"))
    # 0-100 ruler: 370px wide, 3.7px per point
    E.append(srect(372, 368, 370, 8, 4, s["grid"]))
    E.append(f'<rect x="{372 + 3.7 * 54.5:.1f}" y="365" width="3.7" height="14" '
             f'rx="1.5" fill="{s["accent"]}" opacity="0.28"/>')
    E.append(f'<circle cx="{372 + 3.7 * 55:.1f}" cy="372" r="6" '
             f'fill="{s["accent"]}" stroke="{s["panel"]}" stroke-width="2"/>')
    E.append(f'<circle cx="{372 + 3.7 * 70:.1f}" cy="372" r="6" '
             f'fill="{s["amber"]}"/>')
    E.append(spath(f"M{372 + 3.7 * 55:.1f} 386 H{372 + 3.7 * 70:.1f}",
                   s["amber"], 1.2))
    E.append(f'<line x1="{372 + 3.7 * 55:.1f}" y1="382" x2="{372 + 3.7 * 55:.1f}" '
             f'y2="390" stroke="{s["amber"]}" stroke-width="1.2"/>')
    E.append(f'<line x1="{372 + 3.7 * 70:.1f}" y1="382" x2="{372 + 3.7 * 70:.1f}" '
             f'y2="390" stroke="{s["amber"]}" stroke-width="1.2"/>')
    E.append(stext(372 + 3.7 * 62.5, 400, "Δ 15.00", 11, s["amber"],
                   anchor="middle", bold=True))
    E.append(stext(372, 416, "0", 11, s["faint"], mono=True))
    E.append(stext(742, 416, "100", 11, s["faint"], mono=True,
                   anchor="end"))
    threshold = "门槛 0 = 未配置 → OR-003 skipped"
    check_svg(threshold, 11.5, 368, False, False, "threshold")
    E.append(stext(372, 442, threshold, 11.5, s["sub"]))
    E.append(stext(372, 466, "OR-002 · warn · 第 1 行 · rvc", 11.5, s["sub"]))
    finding = "填报 70 → 重算 55（Δ 15.00 > 0.50）"
    check_svg(finding, 13, 368, False, False, "finding")
    E.append(stext(372, 486, finding, 13, s["text"]))
    E.append(stext(372, 500, "容差 0.5 个百分点 · 只报差异", 11, s["faint"]))

    # ---- severity staircase -------------------------------------------------
    E.append(srect(776, 252, 280, 254, 20, s["panel"], s["edge"], 1.5,
                   shadow=True))
    check_svg("④ 依据封顶", 14.5, 120, False, True, "ladder title")
    E.append(stext(794, 276, "④ 依据封顶", 14.5, s["text"], bold=True))
    check_svg("loadRuleset · MAX_SEVERITY_BY_KIND", 11, 244, True, False,
              "ladder tag")
    E.append(stext(794, 294, "loadRuleset · MAX_SEVERITY_BY_KIND", 11,
                   s["faint"], mono=True))

    # three bottom-aligned steps: info (short) -> warn -> error (tall)
    E.append(srect(794, 356, 72, 40, 8, s["band"], s["edge"], 1.1))
    E.append(srect(866, 338, 72, 58, 8, s["amber_bg"], s["amber"], 1.5))
    E.append(srect(938, 320, 72, 76, 8, s["band"], s["edge"], 1.1,
                   dash="5 4"))
    E.append(f'<line x1="794" y1="396" x2="1010" y2="396" stroke="{s["rule"]}"/>')
    E.append(stext(830, 378, "info", 13, s["faint"], bold=True,
                   anchor="middle"))
    E.append(stext(830, 392, "2 条", 11, s["faint"], anchor="middle"))
    E.append(stext(902, 366, "warn", 13, s["amber"], bold=True,
                   anchor="middle"))
    E.append(stext(902, 382, "7/7", 11, s["amber"], anchor="middle"))
    E.append(stext(974, 352, "error", 13, s["faint"], bold=True,
                   anchor="middle"))
    E.append(stext(974, 368, "未用", 11, s["faint"], anchor="middle"))

    E.append(stext(794, 424, "direct → error", 11, s["sub"], mono=True))
    E.append(stext(794, 440, "derived-from-principle → warn", 11, s["amber"],
                   mono=True, bold=True))
    E.append(stext(794, 456, "institutional-configuration → info", 11,
                   s["sub"], mono=True))
    E.append(stext(794, 478, "本包 7 条均 derived-from-principle，", 11,
                   s["faint"]))
    E.append(stext(794, 494, "severity 超过封顶即加载失败。", 11, s["faint"]))
    check_svg("derived-from-principle → warn", 11, 244, True, True,
              "ladder legend")
    check_svg("institutional-configuration → info", 11, 244, True, False,
              "ladder legend")

    # ---- two report channels ------------------------------------------------
    E.append(srect(44, 522, 502, 98, 18, s["panel"], s["edge"], 1.5,
                   shadow=True))
    check_svg("⑤ buildView → issues[]", 14.5, 300, False, True, "issues title")
    E.append(stext(62, 546, "⑤ buildView → issues[]", 14.5, s["accent"],
                   bold=True))
    E.append(scallout(486, 532, "1 条", 11, s["accent"], s["band"])[0])
    E.append(stext(62, 570, "OR-002 · warn · 第 1 行 · rvc", 11.5, s["sub"],
                   mono=True))
    msg = "填报 70 → 重算 55（Δ 15.00 > 0.50）"
    check_svg(msg, 13, 466, False, False, "issues message")
    E.append(stext(62, 590, msg, 13, s["text"]))
    E.append(stext(62, 608, "locator：row + column；found / expected 成对", 11,
                   s["faint"]))

    E.append(srect(560, 522, 496, 98, 18, s["panel"], s["edge"], 1.5,
                   shadow=True))
    check_svg("skipped[]", 14.5, 120, False, True, "skipped title")
    E.append(stext(578, 546, "skipped[]", 14.5, s["sub"], bold=True))
    E.append(scallout(986, 532, "2 条", 11, s["sub"], s["band"])[0])
    check_svg("OR-003 · threshold 未配置（0）", 13, 456, True, False,
              "skipped entry")
    check_svg("OR-005 · values 未配置（[]）", 13, 456, True, False,
              "skipped entry")
    E.append(stext(578, 570, "OR-003 · threshold 未配置（0）", 13, s["text"],
                   mono=True))
    E.append(stext(578, 590, "OR-005 · values 未配置（[]）", 13, s["text"],
                   mono=True))
    E.append(stext(578, 608, "空 issues ≠ 没问题：两条通道一起读", 11,
                   s["faint"]))

    # ---- connectors ---------------------------------------------------------
    E.append(spath("M557 240 V250", s["accent"], 1.6, marker=True))
    E.append(spath("M916 240 V250", s["accent"], 1.4, dash="5 4", marker=True))
    E.append(spath("M338 380 H352", s["accent"], 1.6, marker=True))
    E.append(spath("M557 506 V514 M300 514 H800", s["accent"], 1.6))
    E.append(spath("M300 514 V520", s["accent"], 1.6, marker=True))
    E.append(spath("M800 514 V520", s["accent"], 1.6, marker=True))

    # ---- footer legend ------------------------------------------------------
    E.append(f'<line x1="44" y1="630" x2="1056" y2="630" stroke="{s["rule"]}"/>')
    E.append(f'<circle cx="48" cy="644" r="4.5" fill="{s["accent2"]}"/>')
    E.append(stext(56, 648, "已执行无差异", 11.5, s["sub"]))
    E.append(f'<circle cx="150" cy="644" r="4.5" fill="{s["amber"]}"/>')
    E.append(stext(158, 648, "差异", 11.5, s["sub"]))
    E.append(f'<circle cx="200" cy="644" r="4.5" fill="none" '
             f'stroke="{s["faint"]}" stroke-width="1.6"/>')
    E.append(stext(208, 648, "未执行", 11.5, s["sub"]))
    E.append(stext(560, 648, "read-only · no network · no model call", 11,
                   s["faint"], mono=True))
    E.append(stext(1056, 648, "结论留给审核人 · 原件永不修改", 11.5, s["sub"],
                   anchor="end"))

    E.append('</svg>')
    return "\n".join(E) + "\n"


# --------------------------------------------------------------------------- main
def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        name = f"dsh-origin-rvc-check-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100x660)")
    print("done: 4 hero webp + 2 flow svg")


if __name__ == "__main__":
    main()
