"""
SVG chart generator for Revolut GP L90D analysis.
Produces inline SVG strings that embed directly in HTML slides.
All charts use Inter font, Revolut dark palette, consistent sizing.

Standard chart dimensions: 520px wide, 300px tall.
"""

# Palette
BG = "#0A0A0A"
BLUE = "#0075EB"
BLUE_MID = "#3B9AFF"
BLUE_LIGHT = "#0075EB40"
RED = "#EF4444"
RED_LIGHT = "#EF444440"
WHITE = "#FFFFFF"
GRAY = "#B0B0B0"
DIM = "#707070"
GRID = "#1A1A1A"
FONT = "Inter, -apple-system, sans-serif"

# Standard dimensions
W = 520
H = 300
PAD_L = 70  # left padding for y-axis labels
PAD_R = 20
PAD_T = 20
PAD_B = 50  # bottom padding for x-axis labels


def _fmt(val, decimals=0):
    if abs(val) >= 1_000_000:
        return f"£{val/1_000_000:.{max(decimals,1)}f}M"
    if abs(val) >= 1_000:
        return f"£{val/1_000:.{decimals}f}K"
    return f"£{val:.{decimals}f}"


def _svg_start(w=W, h=H):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" style="width:100%;height:100%;font-family:{FONT};">\n'


def _svg_end():
    return '</svg>\n'


def _gridlines(plot_x, plot_y, plot_w, plot_h, y_min, y_max, steps=5):
    """Draw horizontal gridlines and y-axis labels."""
    lines = []
    for i in range(steps + 1):
        val = y_min + (y_max - y_min) * i / steps
        y = plot_y + plot_h - (val - y_min) / (y_max - y_min) * plot_h
        lines.append(f'<line x1="{plot_x}" y1="{y:.1f}" x2="{plot_x + plot_w}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        lines.append(f'<text x="{plot_x - 8}" y="{y:.1f}" text-anchor="end" font-size="11" fill="{DIM}" dominant-baseline="middle">{_fmt(val)}</text>')
    return '\n'.join(lines)


def bar_chart_vertical(data, w=W, h=H, color=BLUE, show_labels=True):
    """
    Vertical bar chart.
    data: list of (label, value) tuples.
    """
    n = len(data)
    plot_x = PAD_L
    plot_y = PAD_T
    plot_w = w - PAD_L - PAD_R
    plot_h = h - PAD_T - PAD_B

    values = [d[1] for d in data]
    y_min = 0
    y_max = max(values) * 1.15

    bar_w = min(plot_w / n * 0.55, 60)
    gap = plot_w / n

    svg = _svg_start(w, h)
    svg += _gridlines(plot_x, plot_y, plot_w, plot_h, y_min, y_max)

    for i, (label, val) in enumerate(data):
        cx = plot_x + gap * i + gap / 2
        bx = cx - bar_w / 2
        bar_h = (val - y_min) / (y_max - y_min) * plot_h
        by = plot_y + plot_h - bar_h

        svg += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" rx="3"/>\n'

        if show_labels:
            svg += f'<text x="{cx:.1f}" y="{by - 8:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{WHITE}">{_fmt(val)}</text>\n'

        svg += f'<text x="{cx:.1f}" y="{plot_y + plot_h + 20}" text-anchor="middle" font-size="11" fill="{DIM}">{label}</text>\n'

    svg += _svg_end()
    return svg


def bar_chart_grouped(groups, w=W, h=H):
    """
    Grouped vertical bar chart.
    groups: list of (label, [(series_name, value, color), ...])
    """
    n = len(groups)
    plot_x = PAD_L
    plot_y = PAD_T + 20  # extra room for legend
    plot_w = w - PAD_L - PAD_R
    plot_h = h - PAD_T - PAD_B - 20

    all_vals = [v for _, series in groups for _, v, _ in series]
    y_min = min(0, min(all_vals) * 1.1) if any(v < 0 for v in all_vals) else 0
    y_max = max(all_vals) * 1.15

    gap = plot_w / n
    n_series = len(groups[0][1])
    bar_w = min(gap * 0.7 / n_series, 30)

    svg = _svg_start(w, h)
    svg += _gridlines(plot_x, plot_y, plot_w, plot_h, y_min, y_max)

    # Zero line if needed
    if y_min < 0:
        zero_y = plot_y + plot_h - (0 - y_min) / (y_max - y_min) * plot_h
        svg += f'<line x1="{plot_x}" y1="{zero_y:.1f}" x2="{plot_x + plot_w}" y2="{zero_y:.1f}" stroke="{DIM}" stroke-width="1"/>\n'

    # Legend
    legend_items = groups[0][1]
    lx = plot_x
    for j, (sname, _, scolor) in enumerate(legend_items):
        svg += f'<rect x="{lx}" y="5" width="10" height="10" fill="{scolor}" rx="2"/>'
        svg += f'<text x="{lx + 14}" y="14" font-size="10" fill="{DIM}">{sname}</text>'
        lx += len(sname) * 6 + 30

    for i, (label, series) in enumerate(groups):
        cx = plot_x + gap * i + gap / 2
        total_w = bar_w * n_series + 2 * (n_series - 1)
        start_x = cx - total_w / 2

        for j, (_, val, color) in enumerate(series):
            bx = start_x + j * (bar_w + 2)
            if val >= 0:
                bar_h = val / (y_max - y_min) * plot_h
                zero_y = plot_y + plot_h - (0 - y_min) / (y_max - y_min) * plot_h
                by = zero_y - bar_h
            else:
                bar_h = abs(val) / (y_max - y_min) * plot_h
                zero_y = plot_y + plot_h - (0 - y_min) / (y_max - y_min) * plot_h
                by = zero_y

            svg += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" rx="2"/>\n'

            # Value label on top
            label_y = by - 6 if val >= 0 else by + bar_h + 14
            svg += f'<text x="{bx + bar_w/2:.1f}" y="{label_y:.1f}" text-anchor="middle" font-size="9" font-weight="600" fill="{GRAY}">{_fmt(val)}</text>\n'

        svg += f'<text x="{cx:.1f}" y="{plot_y + plot_h + 20}" text-anchor="middle" font-size="11" fill="{DIM}">{label}</text>\n'

    svg += _svg_end()
    return svg


def bar_chart_horizontal(data, w=W, h=H, show_target=None):
    """
    Horizontal bar chart with optional target line.
    data: list of (label, mid, low, high) tuples.
    """
    n = len(data)
    plot_x = 160  # wider left margin for labels
    plot_y = PAD_T
    plot_w = w - plot_x - PAD_R
    plot_h = h - PAD_T - PAD_B

    max_val = max(d[3] for d in data) if data else 1
    if show_target:
        max_val = max(max_val, show_target) * 1.1

    bar_h = min(plot_h / n * 0.6, 28)
    gap = plot_h / n

    svg = _svg_start(w, h)

    # X-axis gridlines
    for i in range(6):
        val = max_val * i / 5
        x = plot_x + val / max_val * plot_w
        svg += f'<line x1="{x:.1f}" y1="{plot_y}" x2="{x:.1f}" y2="{plot_y + plot_h}" stroke="{GRID}" stroke-width="1"/>\n'
        svg += f'<text x="{x:.1f}" y="{plot_y + plot_h + 16}" text-anchor="middle" font-size="10" fill="{DIM}">{_fmt(val)}</text>\n'

    # Target line
    if show_target:
        tx = plot_x + show_target / max_val * plot_w
        svg += f'<line x1="{tx:.1f}" y1="{plot_y - 5}" x2="{tx:.1f}" y2="{plot_y + plot_h + 5}" stroke="{RED}" stroke-width="2" stroke-dasharray="6,4"/>\n'
        svg += f'<text x="{tx + 6:.1f}" y="{plot_y - 2}" font-size="12" font-weight="700" fill="{RED}">£4M target</text>\n'

    for i, (label, mid, low, high) in enumerate(data):
        cy = plot_y + gap * i + gap / 2
        by = cy - bar_h / 2

        # Bar
        bar_px = mid / max_val * plot_w
        svg += f'<rect x="{plot_x}" y="{by:.1f}" width="{bar_px:.1f}" height="{bar_h:.1f}" fill="{BLUE}" rx="3"/>\n'

        # Range line
        lx = plot_x + low / max_val * plot_w
        hx = plot_x + high / max_val * plot_w
        svg += f'<line x1="{lx:.1f}" y1="{cy:.1f}" x2="{hx:.1f}" y2="{cy:.1f}" stroke="{WHITE}" stroke-width="2"/>\n'
        svg += f'<line x1="{lx:.1f}" y1="{cy-4:.1f}" x2="{lx:.1f}" y2="{cy+4:.1f}" stroke="{WHITE}" stroke-width="2"/>\n'
        svg += f'<line x1="{hx:.1f}" y1="{cy-4:.1f}" x2="{hx:.1f}" y2="{cy+4:.1f}" stroke="{WHITE}" stroke-width="2"/>\n'

        # Value label
        svg += f'<text x="{plot_x + bar_px + 8:.1f}" y="{cy + 4:.1f}" font-size="12" font-weight="700" fill="{WHITE}">£{mid/1000:.1f}M</text>\n'

        # Label
        svg += f'<text x="{plot_x - 8}" y="{cy + 4:.1f}" text-anchor="end" font-size="11" fill="{GRAY}">{label}</text>\n'

    # Total annotation
    total_mid = sum(d[1] for d in data)
    total_low = sum(d[2] for d in data)
    total_high = sum(d[3] for d in data)
    svg += f'<text x="{plot_x}" y="{plot_y + plot_h + 35}" font-size="11" font-weight="600" fill="{DIM}">Total: £{total_mid/1000:.1f}M (range £{total_low/1000:.1f}M to £{total_high/1000:.1f}M)</text>\n'

    svg += _svg_end()
    return svg


def waterfall_chart(data, w=W, h=H):
    """
    Waterfall (bridge) chart.
    data: list of (label, value, type) where type is 'total' or 'delta'.
    """
    n = len(data)
    plot_x = PAD_L
    plot_y = PAD_T
    plot_w = w - PAD_L - PAD_R
    plot_h = h - PAD_T - PAD_B

    # Find range
    totals = [d[1] for d in data if d[2] == 'total']
    y_max = max(totals) * 1.12
    y_min = 0

    gap = plot_w / n
    bar_w = min(gap * 0.55, 50)

    svg = _svg_start(w, h)
    svg += _gridlines(plot_x, plot_y, plot_w, plot_h, y_min, y_max)

    running = 0
    prev_running = 0

    for i, (label, val, typ) in enumerate(data):
        cx = plot_x + gap * i + gap / 2
        bx = cx - bar_w / 2

        if typ == 'total':
            bar_h = val / y_max * plot_h
            by = plot_y + plot_h - bar_h
            svg += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{BLUE}" rx="3"/>\n'
            svg += f'<text x="{cx:.1f}" y="{by - 8:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="{WHITE}">{_fmt(val)}</text>\n'
            running = val
        else:
            color = BLUE_MID if val > 0 else RED
            if val >= 0:
                bottom = running
                top = running + val
            else:
                top = running
                bottom = running + val

            by_top = plot_y + plot_h - top / y_max * plot_h
            by_bottom = plot_y + plot_h - bottom / y_max * plot_h
            rect_h = by_bottom - by_top

            svg += f'<rect x="{bx:.1f}" y="{by_top:.1f}" width="{bar_w:.1f}" height="{rect_h:.1f}" fill="{color}" rx="2" opacity="0.85"/>\n'

            # Connector from previous bar
            prev_cx = plot_x + gap * (i - 1) + gap / 2
            conn_y = plot_y + plot_h - running / y_max * plot_h
            svg += f'<line x1="{prev_cx + bar_w/2:.1f}" y1="{conn_y:.1f}" x2="{bx:.1f}" y2="{conn_y:.1f}" stroke="{GRID}" stroke-width="1" stroke-dasharray="3,3"/>\n'

            # Label
            sign = "+" if val > 0 else ""
            label_y = by_top - 6 if val > 0 else by_bottom + 14
            if rect_h > 25:
                label_y = by_top + rect_h / 2 + 4
                svg += f'<text x="{cx:.1f}" y="{label_y:.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="{WHITE}">{sign}{_fmt(val)}</text>\n'
            else:
                svg += f'<text x="{cx:.1f}" y="{label_y:.1f}" text-anchor="middle" font-size="9" font-weight="600" fill="{color}">{sign}{_fmt(val)}</text>\n'

            running += val

        # X-axis label
        svg += f'<text x="{cx:.1f}" y="{plot_y + plot_h + 16}" text-anchor="middle" font-size="9" fill="{DIM}">{label}</text>\n'

    svg += _svg_end()
    return svg
