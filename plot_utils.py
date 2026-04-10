import math
from pathlib import Path

from dobble_utils import construire_plan, deck_projectif, donnees_fano

try:
    from IPython.display import Markdown, SVG, display
except ModuleNotFoundError:  # pragma: no cover - mode script sans IPython
    class _SimpleDisplayObject:
        def __init__(self, data):
            self.data = data

    class Markdown(_SimpleDisplayObject):
        pass

    class SVG(_SimpleDisplayObject):
        pass

    def display(*_args, **_kwargs):
        return None


ROOT = Path(__file__).resolve().parent
EXPORT_ROOT = ROOT / "exports"
FIG_SVG_DIR = EXPORT_ROOT / "figures" / "svg"
LOG_DIR = EXPORT_ROOT / "logs"

PALETTE = {
    "bg": "#ffffff",
    "ink": "#202124",
    "muted": "#5f6368",
    "blue": "#2563eb",
    "red": "#dc2626",
    "green": "#059669",
    "gold": "#b7791f",
    "orange": "#ea580c",
    "rose": "#db2777",
    "violet": "#7c3aed",
    "teal": "#0f766e",
    "sand": "#efe3c2",
    "line": "#d8cbb0",
}


def assurer_dossiers_exports():
    for folder in (FIG_SVG_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def slugifier(name):
    chars = []
    for char in name.lower():
        if char.isalnum():
            chars.append(char)
        elif char in {" ", "-", "_"}:
            chars.append("_")
    slug = "".join(chars).strip("_")
    return slug or "figure"


def ecrire_log(name, contenu):
    assurer_dossiers_exports()
    path = LOG_DIR / f"{slugifier(name)}.log"
    path.write_text(contenu.strip() + "\n", encoding="utf-8")
    return path


def exporter_figure(name, svg_content, description=None):
    assurer_dossiers_exports()
    slug = slugifier(name)
    svg_path = FIG_SVG_DIR / f"{slug}.svg"
    svg_path.write_text(svg_content, encoding="utf-8")

    if description:
        log_text = description
        log_text += f"\n\nSVG : {svg_path}"
        ecrire_log(name, log_text)

    return {"svg": svg_path, "pdf": None, "errors": []}


def afficher_figure(name, svg_content, description=None):
    export = exporter_figure(name, svg_content, description=description)
    display(SVG(svg_content))
    return export


def afficher_markdown_et_log(name, markdown_text):
    ecrire_log(name, markdown_text)
    display(Markdown(markdown_text))


def svg_canvas(width, height, content):
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <rect x="0" y="0" width="{width}" height="{height}" rx="24" fill="{PALETTE["bg"]}"/>
      {content}
    </svg>
    """


def tableau_parametres_svg(q_values=(2, 3, 4, 5, 7, 8, 9)):
    width, height = 760, 460
    x0, y0 = 60, 120
    row_h = 38
    col_w = [130, 160, 160, 180]
    headers = ["Ordre q", "Points", "Droites", "Points par droite"]

    parts = []
    parts.append(f'<text x="44" y="40" font-size="28" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">Tailles des plans projectifs finis</text>')
    parts.append(f'<text x="44" y="76" font-size="16" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">Pour P²(F_q), on a q² + q + 1 points et q + 1 points par droite.</text>')

    x = x0
    for width_col, header in zip(col_w, headers):
        parts.append(f'<rect x="{x}" y="{y0}" width="{width_col}" height="{row_h}" fill="{PALETTE["sand"]}" stroke="{PALETTE["line"]}"/>')
        parts.append(f'<text x="{x + width_col / 2}" y="{y0 + 25}" text-anchor="middle" font-size="15" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{header}</text>')
        x += width_col

    for idx, q in enumerate(q_values, start=1):
        row_y = y0 + idx * row_h
        values = [str(q), str(q * q + q + 1), str(q * q + q + 1), str(q + 1)]
        x = x0
        for width_col, value in zip(col_w, values):
            fill = "#fffdf8" if idx % 2 else "#fbf6ed"
            parts.append(f'<rect x="{x}" y="{row_y}" width="{width_col}" height="{row_h}" fill="{fill}" stroke="{PALETTE["line"]}"/>')
            parts.append(f'<text x="{x + width_col / 2}" y="{row_y + 25}" text-anchor="middle" font-size="15" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{value}</text>')
            x += width_col

    return svg_canvas(width, height, "".join(parts))


def dessiner_completion_projective(q=7):
    width, height = 1100, 660
    grid_size = 360
    x0, y0 = 90, 190
    step = grid_size / (q - 1)
    top_y = 115

    colors = [
        PALETTE["blue"], PALETTE["red"], PALETTE["green"], PALETTE["orange"],
        PALETTE["violet"], PALETTE["teal"], PALETTE["rose"], PALETTE["gold"],
    ]

    parts = []
    parts.append(f'<text x="{x0}" y="42" font-size="28" font-family="DejaVu Sans" fill="{PALETTE["ink"]}">Du plan affine F₇² au plan projectif</text>')
    parts.append(f'<text x="{x0}" y="76" font-size="16" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">La droite à l&apos;infini est séparée du dessin pour garder une lecture nette.</text>')
    parts.append(f'<line x1="{x0}" y1="{top_y}" x2="{x0 + grid_size}" y2="{top_y}" stroke="{PALETTE["ink"]}" stroke-width="2.5"/>')

    for i in range(q):
        x = x0 + i * step
        y = y0 + i * step
        parts.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + grid_size}" stroke="{PALETTE["line"]}" stroke-width="1"/>')
        parts.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + grid_size}" y2="{y}" stroke="{PALETTE["line"]}" stroke-width="1"/>')

    for i in range(q):
        for j in range(q):
            x = x0 + i * step
            y = y0 + (q - 1 - j) * step
            parts.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{PALETTE["ink"]}" opacity="0.8"/>')

    def affine_xy(x, y):
        return x0 + x * step, y0 + (q - 1 - y) * step

    for slope in range(q):
        color = colors[slope % len(colors)]
        inf_x = x0 + slope * (grid_size / (q - 1))
        parts.append(f'<circle cx="{inf_x}" cy="{top_y}" r="8" fill="{color}"/>')
        parts.append(f'<text x="{inf_x - 7}" y="{top_y - 14}" font-size="15" fill="{color}" font-family="DejaVu Sans">m={slope}</text>')
        for intercept in (0, 3):
            pts = [affine_xy(x, (slope * x + intercept) % q) for x in range(q)]
            d = " ".join(f"L {px:.1f} {py:.1f}" if idx else f"M {px:.1f} {py:.1f}" for idx, (px, py) in enumerate(pts))
            parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5" opacity="0.8"/>')
            midx, midy = pts[3]
            parts.append(f'<line x1="{midx}" y1="{midy}" x2="{inf_x}" y2="{top_y}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6 5" opacity="0.7"/>')

    vertical_x = x0 + grid_size + 145
    parts.append(f'<circle cx="{vertical_x}" cy="{top_y}" r="8" fill="{PALETTE["ink"]}"/>')
    parts.append(f'<text x="{vertical_x + 28}" y="{top_y - 18}" font-size="18" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">droite à l&apos;infini</text>')
    parts.append(f'<text x="{vertical_x + 18}" y="{top_y + 5}" font-size="15" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">verticale</text>')
    for xv in (1, 5):
        px, py1 = affine_xy(xv, 0)
        _, py2 = affine_xy(xv, 6)
        parts.append(f'<line x1="{px}" y1="{py1}" x2="{px}" y2="{py2}" stroke="{PALETTE["ink"]}" stroke-width="2.5" opacity="0.75"/>')
        parts.append(f'<line x1="{px}" y1="{(py1 + py2) / 2}" x2="{vertical_x}" y2="{top_y}" stroke="{PALETTE["ink"]}" stroke-width="1.5" stroke-dasharray="6 5" opacity="0.55"/>')

    parts.append(f'<rect x="{x0 - 18}" y="{y0 - 18}" width="{grid_size + 36}" height="{grid_size + 36}" rx="12" fill="none" stroke="{PALETTE["sand"]}" stroke-width="3"/>')
    parts.append(f'<text x="{x0}" y="{y0 + grid_size + 28}" font-size="18" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">Chaque famille de parallèles reçoit un point à l&apos;infini.</text>')
    parts.append(f'<text x="{x0}" y="{y0 + grid_size + 54}" font-size="18" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">Toutes ces directions sont ensuite rassemblées sur une même droite.</text>')
    return svg_canvas(width, height, "".join(parts))


def positions_fano():
    width, height = 980, 650
    cx, cy = 315, 340
    radius = 190
    angles = {"A": -90, "B": 150, "C": 30}
    vertices = {
        name: (
            cx + radius * math.cos(math.radians(angle)),
            cy + radius * math.sin(math.radians(angle)),
        )
        for name, angle in angles.items()
    }
    positions = {
        "A": vertices["A"],
        "B": vertices["B"],
        "C": vertices["C"],
        "M_AB": ((vertices["A"][0] + vertices["B"][0]) / 2, (vertices["A"][1] + vertices["B"][1]) / 2),
        "M_AC": ((vertices["A"][0] + vertices["C"][0]) / 2, (vertices["A"][1] + vertices["C"][1]) / 2),
        "M_BC": ((vertices["B"][0] + vertices["C"][0]) / 2, (vertices["B"][1] + vertices["C"][1]) / 2),
        "O": (cx, cy),
    }
    circle_r = math.dist(positions["O"], positions["M_AB"])
    return width, height, positions, circle_r


def dessiner_fano():
    labels = {
        "A": "[1:0:0]", "B": "[0:1:0]", "C": "[0:0:1]", "M_AB": "[1:1:0]",
        "M_AC": "[1:0:1]", "M_BC": "[0:1:1]", "O": "[1:1:1]",
    }
    pretty = {"A": "A", "B": "B", "C": "C", "M_AB": "M_AB", "M_AC": "M_AC", "M_BC": "M_BC", "O": "O"}
    _, lines = donnees_fano()
    width, height, positions, circle_r = positions_fano()
    colors = [
        PALETTE["blue"],
        PALETTE["red"],
        PALETTE["green"],
        PALETTE["orange"],
        PALETTE["violet"],
        PALETTE["teal"],
        PALETTE["rose"],
    ]

    parts = []
    parts.append(f'<text x="44" y="42" font-size="30" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">Plan de Fano : représentation canonique</text>')
    parts.append(f'<text x="44" y="78" font-size="16" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">Triangle, milieux des côtés, centre et cercle passant par les trois milieux.</text>')

    for idx, line in enumerate(lines):
        color = colors[idx]
        if line["kind"] == "circle":
            parts.append(f'<circle cx="{positions["O"][0]}" cy="{positions["O"][1]}" r="{circle_r}" fill="none" stroke="{color}" stroke-width="4"/>')
        else:
            pts = sorted((positions[line["points"][0]], positions[line["points"][1]], positions[line["points"][2]]), key=lambda item: (item[0], item[1]))
            parts.append(f'<line x1="{pts[0][0]}" y1="{pts[0][1]}" x2="{pts[-1][0]}" y2="{pts[-1][1]}" stroke="{color}" stroke-width="4"/>')

    for name, (x, y) in positions.items():
        dx = 18 if name != "B" else -110
        dy = -10 if name in {"A", "M_AB", "M_AC"} else 18
        parts.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{PALETTE["bg"]}" stroke="{PALETTE["ink"]}" stroke-width="3"/>')
        parts.append(f'<text x="{x + dx}" y="{y + dy}" font-size="18" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{pretty[name]}</text>')
        parts.append(f'<text x="{x + dx}" y="{y + dy + 18}" font-size="14" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">{labels[name]}</text>')

    legend_x, legend_y = 610, 145
    for idx, line in enumerate(lines):
        y = legend_y + idx * 52
        parts.append(f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 44}" y2="{y}" stroke="{colors[idx]}" stroke-width="4"/>')
        contenu = ", ".join(line["points"])
        parts.append(f'<text x="{legend_x + 58}" y="{y + 6}" font-size="16" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{line["name"]} : {contenu}</text>')

    parts.append(f'<text x="44" y="614" font-size="17" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">Le cercle joue ici le role de septieme droite et passe par M_AB, M_AC et M_BC.</text>')
    return svg_canvas(width, height, "".join(parts))


def matrice_incidence_svg(q=2, cell=38):
    pts, lignes, incidence = construire_plan(q)
    width = 190 + len(pts) * cell
    height = 150 + len(lignes) * cell

    parts = []
    parts.append(f'<text x="28" y="40" font-size="26" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">Matrice d&apos;incidence de P²(F_{q})</text>')
    x0, y0 = 130, 95

    for j, point in enumerate(pts):
        x = x0 + j * cell
        parts.append(f'<rect x="{x}" y="{y0 - 30}" width="{cell}" height="30" fill="{PALETTE["sand"]}" stroke="{PALETTE["line"]}"/>')
        parts.append(f'<text x="{x + cell / 2}" y="{y0 - 10}" text-anchor="middle" font-size="10" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{j + 1}</text>')

    for i, line in enumerate(lignes):
        y = y0 + i * cell
        parts.append(f'<rect x="{x0 - 82}" y="{y}" width="82" height="{cell}" fill="{PALETTE["sand"]}" stroke="{PALETTE["line"]}"/>')
        parts.append(f'<text x="{x0 - 41}" y="{y + 24}" text-anchor="middle" font-size="11" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">d{i + 1}</text>')
        line_points = set(incidence[line])
        for j, point in enumerate(pts):
            x = x0 + j * cell
            fill = PALETTE["blue"] if point in line_points else "#fffdf8"
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" fill-opacity="0.85" stroke="{PALETTE["line"]}"/>')
            if point in line_points:
                parts.append(f'<circle cx="{x + cell / 2}" cy="{y + cell / 2}" r="5" fill="{PALETTE["bg"]}"/>')
    return svg_canvas(width, height, "".join(parts))


def vue_affine_p7():
    width, height = 1100, 650
    x0, y0 = 90, 155
    step = 56
    q = 7
    grid = step * (q - 1)
    top_y = 100
    right_x = x0 + grid + 175

    parts = []
    parts.append(f'<text x="42" y="42" font-size="30" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">Une représentation de P²(F₇)</text>')
    parts.append(f'<text x="42" y="76" font-size="17" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">49 points affines et 8 points à l&apos;infini</text>')
    parts.append(f'<line x1="{x0}" y1="{top_y}" x2="{right_x}" y2="{top_y}" stroke="{PALETTE["ink"]}" stroke-width="2.5"/>')

    for i in range(q):
        x = x0 + i * step
        y = y0 + i * step
        parts.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + grid}" stroke="{PALETTE["line"]}" stroke-width="1"/>')
        parts.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + grid}" y2="{y}" stroke="{PALETTE["line"]}" stroke-width="1"/>')

    for x in range(q):
        for y in range(q):
            px = x0 + x * step
            py = y0 + (q - 1 - y) * step
            parts.append(f'<circle cx="{px}" cy="{py}" r="5.5" fill="{PALETTE["ink"]}"/>')

    directions = [0, 1, 2, 3, 4, 5, 6, "∞"]
    dir_colors = [PALETTE["blue"], PALETTE["red"], PALETTE["green"], PALETTE["orange"], PALETTE["violet"], PALETTE["teal"], PALETTE["rose"], PALETTE["ink"]]
    for idx, direction in enumerate(directions):
        px = x0 + idx * ((right_x - x0) / 7)
        parts.append(f'<circle cx="{px}" cy="{top_y}" r="9" fill="{dir_colors[idx]}"/>')
        label = f"m={direction}" if direction != "∞" else "verticale"
        parts.append(f'<text x="{px + 18}" y="{top_y + 5}" font-size="14" fill="{dir_colors[idx]}" font-family="DejaVu Sans">{label}</text>')

    exemples = [(2, 1, PALETTE["blue"]), (2, 4, PALETTE["blue"]), (5, 0, PALETTE["red"]), ("v", 3, PALETTE["ink"])]

    def affine_xy(x, y):
        return x0 + x * step, y0 + (q - 1 - y) * step

    for slope, intercept, color in exemples:
        if slope == "v":
            px, py1 = affine_xy(intercept, 0)
            _, py2 = affine_xy(intercept, 6)
            parts.append(f'<line x1="{px}" y1="{py1}" x2="{px}" y2="{py2}" stroke="{color}" stroke-width="4" opacity="0.85"/>')
        else:
            pts = [affine_xy(x, (slope * x + intercept) % q) for x in range(q)]
            d = " ".join(f"L {px} {py}" if idx else f"M {px} {py}" for idx, (px, py) in enumerate(pts))
            parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="4" opacity="0.78"/>')
    return svg_canvas(width, height, "".join(parts))


def dessiner_cartes(deck, colonnes=3, rayon=88):
    width = 1000
    cell_w, cell_h = 300, 250
    rows = math.ceil(len(deck) / colonnes)
    height = rows * cell_h + 90

    palette = [PALETTE["blue"], PALETTE["red"], PALETTE["green"], PALETTE["orange"], PALETTE["violet"], PALETTE["teal"], PALETTE["rose"], PALETTE["gold"]]
    icons = ["★", "●", "▲", "■", "✦", "◆", "✚", "⬢"]

    parts = []
    parts.append(f'<text x="34" y="42" font-size="28" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">Exemples de cartes construites à partir de P²(F₇)</text>')

    for idx, card in enumerate(deck):
        row, col = divmod(idx, colonnes)
        cx = 155 + col * cell_w
        cy = 180 + row * cell_h
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{rayon}" fill="#fffdfa" stroke="{PALETTE["ink"]}" stroke-width="3"/>')
        parts.append(f'<text x="{cx}" y="{cy - rayon - 14}" text-anchor="middle" font-size="18" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{card["carte"]}</text>')
        for k, symbol in enumerate(card["symboles"]):
            angle = -90 + k * 45
            radius = 52 if k % 2 == 0 else 34
            sx = cx + radius * math.cos(math.radians(angle))
            sy = cy + radius * math.sin(math.radians(angle))
            color = palette[k % len(palette)]
            icon = icons[k % len(icons)]
            parts.append(f'<text x="{sx}" y="{sy}" text-anchor="middle" font-size="20" fill="{color}" font-family="DejaVu Sans">{icon}</text>')
            parts.append(f'<text x="{sx}" y="{sy + 18}" text-anchor="middle" font-size="11" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{symbol}</text>')
    return svg_canvas(width, height, "".join(parts))


def visualiser_paire_commune(c1, c2):
    commun = sorted(set(c1["symboles"]) & set(c2["symboles"]))[0]
    width, height = 850, 400
    positions = [(-36, -48), (44, -44), (0, -6), (-54, 30), (56, 20), (-10, 56), (34, 66), (-68, -2)]
    colors = [PALETTE["blue"], PALETTE["red"], PALETTE["green"], PALETTE["orange"], PALETTE["violet"], PALETTE["teal"], PALETTE["rose"], PALETTE["gold"]]

    parts = []
    parts.append(f'<text x="32" y="42" font-size="28" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">Deux cartes distinctes se coupent en un unique symbole</text>')
    parts.append(f'<text x="32" y="76" font-size="16" fill="{PALETTE["muted"]}" font-family="DejaVu Sans">Le dessin laisse un espace libre sous le titre pour éviter les chevauchements.</text>')
    centers = [(225, 225), (620, 225)]
    for idx, (cx, cy) in enumerate(centers):
        card = [c1, c2][idx]
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="110" fill="#fffdfa" stroke="{PALETTE["ink"]}" stroke-width="3"/>')
        parts.append(f'<text x="{cx}" y="{cy - 128}" text-anchor="middle" font-size="19" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{card["carte"]}</text>')
        for k, symbol in enumerate(card["symboles"]):
            dx, dy = positions[k]
            color = PALETTE["gold"] if symbol == commun else colors[k % len(colors)]
            size = 18 if symbol == commun else 14
            weight = "700" if symbol == commun else "400"
            parts.append(f'<circle cx="{cx + dx}" cy="{cy + dy - 8}" r="17" fill="{color}" opacity="0.18"/>')
            parts.append(f'<text x="{cx + dx}" y="{cy + dy}" text-anchor="middle" font-size="{size}" font-weight="{weight}" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{symbol}</text>')

    parts.append(f'<line x1="340" y1="225" x2="505" y2="225" stroke="{PALETTE["gold"]}" stroke-width="5" stroke-dasharray="9 8"/>')
    parts.append(f'<text x="422" y="211" text-anchor="middle" font-size="18" fill="{PALETTE["gold"]}" font-family="DejaVu Sans">symbole commun</text>')
    parts.append(f'<text x="422" y="239" text-anchor="middle" font-size="22" fill="{PALETTE["ink"]}" font-family="DejaVu Sans">{commun}</text>')
    return svg_canvas(width, height, "".join(parts))
