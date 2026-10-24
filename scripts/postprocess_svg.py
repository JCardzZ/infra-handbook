"""Post-process the Graphviz SVGs written by the "diagrams" library.

1. Inline the PNG icons as base64 data URIs. diagrams references icon files
   inside its own Python package (absolute local paths), which do not exist on
   any other machine or on the published site.
2. Express the SVG width and height in px instead of pt. Browsers render
   1pt as 1.33px, so a pt-sized SVG shown at natural size is a third larger
   than designed; in px the text renders at its design size.
3. Move each edge label next to its own line. With orthogonal routing
   Graphviz leaves labels where it reserved room for them, which can be far
   from the routed line; the label goes beside the longest straight run of its
   edge instead, on a background in the color of the box it sits in.
4. Give a cluster title or node name a background when a line crosses it, so
   the line passes under the text instead of striking through it.

Usage: python scripts/postprocess_svg.py docs/assets/diagrams/*.svg
"""

import base64
import html
import mimetypes
import re
import sys
from pathlib import Path

HREF = re.compile(r'(xlink:href|href)="([^"]+\.(?:png|jpg|jpeg|svg))"')
SIZE = re.compile(r'<svg width="([0-9.]+)pt" height="([0-9.]+)pt"')
GROUP = re.compile(r'<g id="[^"]*" class="(cluster|edge)">(.*?)</g>', re.S)
CLUSTER_PATH = re.compile(r'<path fill="([^"]+)"[^>]* d="([^"]+)"')
TEXT = re.compile(r'<text [^>]*text-anchor="(\w+)" x="([-0-9.]+)" y="([-0-9.]+)"[^>]*font-size="([0-9.]+)"[^>]*>(.*?)</text>')
NUMBER = re.compile(r"-?[0-9.]+")
LABELS_MARK = '<g class="hb-labels">'

# Average Helvetica glyph width as a fraction of the font size.
CHAR_WIDTH = 0.52


def embed_images(svg_path: Path, text: str) -> tuple[str, int]:
    count = 0

    def embed(match: re.Match) -> str:
        nonlocal count
        attr, ref = match.groups()
        file = Path(ref)
        if not file.is_absolute():
            file = svg_path.parent / file
        if not file.exists():
            sys.exit(f"{svg_path}: referenced image not found: {ref}")
        mime = mimetypes.guess_type(file.name)[0] or "image/png"
        data = base64.b64encode(file.read_bytes()).decode("ascii")
        count += 1
        return f'{attr}="data:{mime};base64,{data}"'

    return HREF.sub(embed, text), count


def _points(d: str) -> list[tuple[float, float]]:
    nums = [float(n) for n in NUMBER.findall(d)]
    points = []
    for p in zip(nums[0::2], nums[1::2]):
        if not points or points[-1] != p:
            points.append(p)
    return points


def _segments(points):
    return [(a, b) for a, b in zip(points, points[1:]) if a[0] == b[0] or a[1] == b[1]]


def _crosses(segment, box) -> bool:
    (ax, ay), (bx, by) = segment
    x0, y0, x1, y1 = box
    if ax == bx:
        return x0 <= ax <= x1 and min(ay, by) <= y1 and max(ay, by) >= y0
    return y0 <= ay <= y1 and min(ax, bx) <= x1 and max(ax, bx) >= x0


def _text_box(anchor, x, y, size, content):
    visible = html.unescape(content).replace("\xa0", " ").strip()
    width = len(visible) * size * CHAR_WIDTH + 6
    left = {"start": x - 3, "end": x - width + 3}.get(anchor, x - width / 2)
    return visible, (left, y - size * 0.95, left + width, y + size * 0.25)


def lift_labels(text: str) -> tuple[str, int]:
    if LABELS_MARK in text:
        return text, 0

    clusters = []  # (area, box, fill, [title texts])
    edges = []  # (group text, segments, [label texts])
    for match in GROUP.finditer(text):
        kind, body = match.groups()
        texts = [m.groups() for m in TEXT.finditer(body)]
        if kind == "cluster":
            path = CLUSTER_PATH.search(body)
            if path:
                xs, ys = zip(*_points(path.group(2)))
                box = (min(xs), min(ys), max(xs), max(ys))
                clusters.append(((box[2] - box[0]) * (box[3] - box[1]), box, path.group(1), texts))
        else:
            path = re.search(r'<path [^>]* d="([^"]+)"', body)
            edges.append((match.group(0), _segments(_points(path.group(1))) if path else [], texts))

    def background(box) -> str:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        inside = [c for c in clusters if c[1][0] <= cx <= c[1][2] and c[1][1] <= cy <= c[1][3]]
        return min(inside, key=lambda c: c[0])[2] if inside else "white"

    all_segments = [s for _, segments, _ in edges for s in segments]
    out = []

    def emit(content, anchor, x, y, size, fill_attr, box):
        out.append(
            f'<rect x="{box[0]:.2f}" y="{box[1]:.2f}" width="{box[2] - box[0]:.2f}" '
            f'height="{box[3] - box[1]:.2f}" rx="3" fill="{background(box)}"/>\n'
            f'<text xml:space="preserve" text-anchor="{anchor}" x="{x:.2f}" y="{y:.2f}" '
            f'font-family="Helvetica,sans-Serif" font-size="{size}" {fill_attr}>{content}</text>'
        )

    for _, _, _, titles in clusters:
        for anchor, x, y, size, content in titles:
            visible, box = _text_box(anchor, float(x), float(y), float(size), content)
            if visible and any(_crosses(s, box) for s in all_segments):
                emit(content, anchor, float(x), float(y), size, 'fill="#1f2933"', box)

    # Node names too: orthogonal edges can leave a node at the height of its name.
    for g in re.finditer(r'<g id="[^"]*" class="node">(.*?)</g>', text, re.S):
        for m in TEXT.finditer(g.group(1)):
            anchor, x, y, size, content = m.groups()
            visible, box = _text_box(anchor, float(x), float(y), float(size), content)
            if visible and any(_crosses(s, box) for s in all_segments):
                fill = re.search(r'fill="[^"]+"', m.group(0)).group(0)
                emit(content, anchor, float(x), float(y), size, fill, box)

    # Obstacles a moved label should avoid: node and cluster texts, other labels.
    node_texts = [
        _text_box(m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5))[1]
        for g in re.finditer(r'<g id="[^"]*" class="node">(.*?)</g>', text, re.S)
        for m in TEXT.finditer(g.group(1))
    ] + [
        _text_box(anchor, float(x), float(y), float(size), content)[1]
        for _, _, _, titles in clusters for anchor, x, y, size, content in titles
    ]
    placed = []

    def overlaps(a, b) -> bool:
        return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

    for group, segments, labels in edges:
        if not labels or not segments:
            continue
        own = set(segments)
        others = [s for s in all_segments if s not in own]
        contents = [html.escape(html.unescape(c).replace("\xa0", " ").strip()) for *_, c in labels]
        size = float(labels[0][3])
        line_height = size * 1.15
        fill = re.search(r'fill="[^"]+"', TEXT.search(group).group(0)).group(0)

        def layout(seg, frac, side):
            (ax, ay), (bx, by) = seg
            mx, my = ax + (bx - ax) * frac, ay + (by - ay) * frac
            n = len(contents)
            if ax == bx:  # vertical run: beside it, block centered on the point
                anchor, x = ("start", mx + 6) if side > 0 else ("end", mx - 6)
                ys = [my - (n - 1) * line_height / 2 + size * 0.35 + i * line_height for i in range(n)]
            else:  # horizontal run: above or below it
                anchor, x = "middle", mx
                top = my - 6 - (n - 1) * line_height if side < 0 else my + 6 + size * 0.8
                ys = [top + i * line_height for i in range(n)]
            boxes = [_text_box(anchor, x, y, size, c)[1] for y, c in zip(ys, contents)]
            return anchor, x, ys, boxes

        def score(boxes) -> int:
            return sum(
                5 * sum(overlaps(b, o) for o in placed)
                + 3 * sum(overlaps(b, o) for o in node_texts)
                + sum(_crosses(s, b) for s in others)
                for b in boxes
            )

        # Longest straight runs first; prefer the middle of a run, right or above.
        runs = sorted(segments, key=lambda s: -(abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1])))[:3]
        candidates = [layout(seg, frac, side) for seg in runs for frac in (0.5, 0.35, 0.65, 0.2, 0.8) for side in (1, -1)]
        anchor, x, ys, boxes = min(candidates, key=lambda c: score(c[3]))
        for y, c, box in zip(ys, contents, boxes):
            emit(c, anchor, x, y, labels[0][3], fill, box)
            placed.append(box)
        # Drop the label Graphviz placed; the moved copy replaces it.
        text = text.replace(group, TEXT.sub("", group))

    if not out:
        return text, 0
    block = LABELS_MARK + "\n" + "\n".join(out) + "\n</g>\n"
    end = text.rindex("</g>\n</svg>")
    return text[:end] + block + text[end:], len(out)


def process(svg_path: Path) -> tuple[int, int]:
    text = svg_path.read_text(encoding="utf-8")
    text, images = embed_images(svg_path, text)
    text = SIZE.sub(r'<svg width="\1px" height="\2px"', text, count=1)
    text, labels = lift_labels(text)
    svg_path.write_text(text, encoding="utf-8")
    return images, labels


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        images, labels = process(Path(arg))
        print(f"{arg}: embedded {images} image(s), lifted {labels} label(s)")
