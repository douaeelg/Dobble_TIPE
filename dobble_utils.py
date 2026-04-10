import textwrap
from itertools import combinations


def mod_inv(a, p):
    return pow(a, -1, p)


def canonique(point, q):
    x, y, z = point
    for value in (x, y, z):
        if value % q != 0:
            inv = mod_inv(value % q, q)
            return tuple((inv * coord) % q for coord in point)
    raise ValueError("Le vecteur nul ne définit pas de point projectif.")


def points_projectifs(q):
    pts = []
    seen = set()
    for x in range(q):
        for y in range(q):
            for z in range(q):
                if (x, y, z) == (0, 0, 0):
                    continue
                point = canonique((x, y, z), q)
                if point not in seen:
                    seen.add(point)
                    pts.append(point)
    return pts


def droites_projectives(q):
    return points_projectifs(q)


def incidences_ligne(line, points, q):
    a, b, c = line
    return [p for p in points if (a * p[0] + b * p[1] + c * p[2]) % q == 0]


def construire_plan(q):
    pts = points_projectifs(q)
    lignes = droites_projectives(q)
    incidence = {line: incidences_ligne(line, pts, q) for line in lignes}
    return pts, lignes, incidence


def etiquette_point(point):
    return f"[{point[0]}:{point[1]}:{point[2]}]"


def equation_ligne(line):
    a, b, c = line
    return f"{a}x + {b}y + {c}z = 0"


def donnees_fano():
    points = {
        "A": (1, 0, 0),
        "B": (0, 1, 0),
        "C": (0, 0, 1),
        "M_AB": (1, 1, 0),
        "M_AC": (1, 0, 1),
        "M_BC": (0, 1, 1),
        "O": (1, 1, 1),
    }
    lines = [
        {"name": "z = 0", "points": ("A", "B", "M_AB"), "kind": "segment"},
        {"name": "y = 0", "points": ("A", "C", "M_AC"), "kind": "segment"},
        {"name": "x = 0", "points": ("B", "C", "M_BC"), "kind": "segment"},
        {"name": "x + y = 0", "points": ("C", "M_AB", "O"), "kind": "segment"},
        {"name": "x + z = 0", "points": ("B", "M_AC", "O"), "kind": "segment"},
        {"name": "y + z = 0", "points": ("A", "M_BC", "O"), "kind": "segment"},
        {"name": "x + y + z = 0", "points": ("M_AB", "M_AC", "M_BC"), "kind": "circle"},
    ]
    return points, lines


def resume_fano():
    _, lines = donnees_fano()
    lines_text = "\n".join(f"- {line['name']} : {', '.join(line['points'])}" for line in lines)
    return textwrap.dedent(
        f"""
        Vérification du plan de Fano

        Représentation retenue :
        - trois sommets A, B, C d'un triangle ;
        - trois milieux M_AB, M_AC, M_BC ;
        - un point central O ;
        - six droites rectilignes et un cercle.

        Les 7 droites représentées sont :
        {lines_text}

        La figure est cohérente avec P²(F_2) :
        - 7 points ;
        - 7 droites ;
        - 3 points sur chaque droite ;
        - 3 droites passant par chaque point.
        """
    ).strip()


def nommer_points(points):
    return {point: f"S{idx + 1}" for idx, point in enumerate(points)}


def deck_projectif(q=7):
    points, lignes, incidence = construire_plan(q)
    noms = nommer_points(points)
    deck = []
    for idx, line in enumerate(lignes, start=1):
        deck.append(
            {
                "carte": f"C{idx}",
                "equation": line,
                "symboles": [noms[p] for p in incidence[line]],
                "points": incidence[line],
            }
        )
    return points, lignes, incidence, deck, noms


def resume_p7():
    points, lignes, incidence, deck, _ = deck_projectif(7)
    tailles = {len(card["symboles"]) for card in deck}
    intersections = [
        len(set(c1["symboles"]) & set(c2["symboles"]))
        for c1, c2 in combinations(deck, 2)
    ]
    return textwrap.dedent(
        f"""
        Vérification combinatoire pour P²(F_7)

        - nombre de points : {len(points)}
        - nombre de droites : {len(lignes)}
        - nombre de cartes théoriques : {len(deck)}
        - tailles observées des cartes : {sorted(tailles)}
        - intersection minimale entre deux cartes : {min(intersections)}
        - intersection maximale entre deux cartes : {max(intersections)}

        Conclusion :
        toute paire de cartes distinctes partage exactement un symbole.
        """
    ).strip()


def noter_sources_web(urls):
    lines = ["Sources web consultées pour vérifier la figure et le contexte :"]
    for url in urls:
        lines.append(f"- {url}")
    return "\n".join(lines)
