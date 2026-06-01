#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dobble — 2 robots theoriques

Trois cartes rondes sur fond noir :
  - une carte CENTRALE partagee
  - une carte pour le ROBOT 1 (gauche)
  - une carte pour le ROBOT 2 (droite)

Chaque robot cherche le symbole commun entre sa carte et la carte centrale
(c'est la vraie mecanique de Dobble : deux cartes partagent toujours
exactement un symbole). Le robot le plus rapide marque le point ; le
symbole trouve est mis en surbrillance.

Les symboles sont des emojis. Tout se joue automatiquement.

Commandes :
  ESPACE  -> pause / reprise
  R       -> reset des scores
  ECHAP   -> quitter

Dependance : pip install pygame
"""

import os
import sys
import math
import random

import pygame

# --------------------------------------------------------------------------
# 1) Generation d'un deck Dobble valide (plan projectif d'ordre n, n premier)
#    -> n^2+n+1 cartes, n+1 symboles par carte, n^2+n+1 symboles au total.
#    n = 7  ->  57 cartes, 8 symboles/carte, 57 symboles.  (Dobble classique)
# --------------------------------------------------------------------------
def generate_dobble(n=7):
    cards = []
    for i in range(n + 1):
        cards.append([0] + [1 + n * i + j for j in range(n)])
    for i in range(n):
        for j in range(n):
            card = [i + 1]
            for k in range(n):
                card.append(n + 1 + n * k + ((i * k + j) % n))
            cards.append(card)
    return cards


# 57 emojis distincts (un par symbole)
SYMBOLS = [
    "🍎", "🍌", "🍇", "🍓", "🍒", "🍑", "🥝", "🍍", "🥥", "🥭",
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
    "🦁", "🐮", "🐷", "🐸", "🐵", "🐔", "🐧", "🐦", "🦄", "🐝",
    "🚗", "🚕", "🚙", "🚌", "🚓", "🚑", "🚒", "🚐", "🚚", "🚛",
    "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱", "🎸", "🎹",
    "🎺", "🎻", "🥁", "🎤", "🎧", "🎲", "🧩",
]

# --------------------------------------------------------------------------
# 2) Rendu des emojis (multi-plateforme)
#    Les polices emoji couleur (Noto) sont bitmap : on rend une fois a taille
#    native puis on met a l'echelle / on tourne par instance, avec cache.
# --------------------------------------------------------------------------
EMOJI_FONT_CANDIDATES = [
    "C:/Windows/Fonts/seguiemj.ttf",                                  # Windows
    "/System/Library/Fonts/Apple Color Emoji.ttc",                    # macOS
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",              # Linux Debian/Ubuntu
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/noto-cjk/NotoColorEmoji.ttf",
    "/usr/share/fonts/google-noto-emoji/NotoColorEmoji.ttf",          # Fedora
    "/usr/share/fonts/TTF/NotoColorEmoji.ttf",                        # Arch
]

BASE_EMOJI_PX = 96  # taille native de rendu avant mise a l'echelle


class EmojiRenderer:
    def __init__(self):
        self.font = None
        self.color_ok = False
        for path in EMOJI_FONT_CANDIDATES:
            if os.path.exists(path):
                try:
                    self.font = pygame.font.Font(path, BASE_EMOJI_PX)
                    self.color_ok = True
                    break
                except Exception:
                    # Police emoji couleur bitmap : taille fixe imposee
                    for sz in (109, 128, 137, 160):
                        try:
                            self.font = pygame.font.Font(path, sz)
                            self.color_ok = True
                            break
                        except Exception:
                            continue
                    if self.font:
                        break
        if self.font is None:
            # Repli : police systeme par defaut (emojis monochromes/tofu)
            self.font = pygame.font.SysFont(None, BASE_EMOJI_PX)
            print("[!] Aucune police emoji couleur trouvee : rendu de repli.\n"
                  "    Linux : sudo apt install fonts-noto-color-emoji")
        self._base = {}    # emoji -> surface taille native
        self._cache = {}   # (emoji, taille) -> surface mise a l'echelle

    def _base_surface(self, emoji):
        if emoji not in self._base:
            try:
                surf = self.font.render(emoji, True, (255, 255, 255))
            except Exception:
                surf = self.font.render("?", True, (255, 255, 255))
            self._base[emoji] = surf
        return self._base[emoji]

    def get(self, emoji, size):
        size = max(8, int(size))
        key = (emoji, size)
        if key not in self._cache:
            base = self._base_surface(emoji)
            w, h = base.get_size()
            scale = size / max(w, h)
            surf = pygame.transform.smoothscale(
                base, (max(1, int(w * scale)), max(1, int(h * scale)))
            )
            self._cache[key] = surf
        return self._cache[key]


# --------------------------------------------------------------------------
# 3) Disposition des symboles a l'interieur d'une carte ronde
#    Echantillonnage par rejet pour limiter les chevauchements + rotation/taille.
# --------------------------------------------------------------------------
def layout_symbols(count, card_radius):
    placements = []
    margin = card_radius * 0.16
    usable = card_radius - margin
    sizes = []
    for _ in range(count):
        # tailles variees comme dans un vrai Dobble
        sizes.append(card_radius * random.uniform(0.30, 0.46))
    sizes.sort(reverse=True)  # placer d'abord les plus gros

    for s in sizes:
        sr = s * 0.5
        placed = None
        for attempt in range(400):
            ease = attempt / 400.0
            r = random.uniform(0, max(0.0, usable - sr))
            a = random.uniform(0, 2 * math.pi)
            x, y = r * math.cos(a), r * math.sin(a)
            min_gap = (sr * (0.9 - 0.5 * ease))
            if all(math.hypot(x - px, y - py) > (sr + ps * 0.5) - min_gap
                   for px, py, ps in [(p[0], p[1], p[2]) for p in placements]):
                placed = (x, y)
                break
        if placed is None:
            placed = (r * math.cos(a), r * math.sin(a))
        rot = random.uniform(-50, 50)
        placements.append((placed[0], placed[1], s, rot))
    random.shuffle(placements)
    return placements


# --------------------------------------------------------------------------
# 4) Le jeu
# --------------------------------------------------------------------------
WIDTH, HEIGHT = 1120, 720
BG = (8, 8, 12)
CARD_FILL = (245, 245, 245)
CARD_EDGE = (30, 30, 36)
R1_COLOR = (90, 200, 255)
R2_COLOR = (255, 140, 90)
TXT = (235, 235, 240)
DIM = (150, 150, 160)


class Card:
    def __init__(self, symbol_ids, center, radius, renderer):
        self.symbol_ids = symbol_ids
        self.center = center
        self.radius = radius
        self.renderer = renderer
        self.layout = layout_symbols(len(symbol_ids), radius)

    def draw(self, surf, highlight_sym=None, hl_color=(0, 230, 120), pulse=0.0):
        cx, cy = self.center
        pygame.draw.circle(surf, (0, 0, 0), (cx, cy + 6), self.radius)  # ombre
        pygame.draw.circle(surf, CARD_FILL, (cx, cy), self.radius)
        pygame.draw.circle(surf, CARD_EDGE, (cx, cy), self.radius, 5)
        for (dx, dy, size, rot), sid in zip(self.layout, self.symbol_ids):
            emoji = SYMBOLS[sid % len(SYMBOLS)]
            img = self.renderer.get(emoji, size)
            img = pygame.transform.rotate(img, rot)
            rect = img.get_rect(center=(cx + dx, cy + dy))
            if highlight_sym is not None and sid == highlight_sym:
                rad = int(size * 0.62 + 6 + 5 * math.sin(pulse * 6))
                glow = pygame.Surface((rad * 2 + 8, rad * 2 + 8), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*hl_color, 70), (rad + 4, rad + 4), rad + 4)
                pygame.draw.circle(glow, (*hl_color, 255), (rad + 4, rad + 4), rad, 5)
                surf.blit(glow, glow.get_rect(center=(cx + dx, cy + dy)))
            surf.blit(img, rect)


def common_symbol(a, b):
    s = set(a) & set(b)
    return next(iter(s)) if s else None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dobble — 2 robots theoriques")
    clock = pygame.time.Clock()
    renderer = EmojiRenderer()
    font_big = pygame.font.SysFont("arial", 30, bold=True)
    font_mid = pygame.font.SysFont("arial", 22, bold=True)
    font_sm = pygame.font.SysFont("arial", 17)

    deck = generate_dobble(7)
    radius = 165
    y = 410
    pos_left = (250, y)
    pos_center = (560, y)
    pos_right = (870, y)

    scores = [0, 0]
    rounds = 0
    # petite "personnalite" de vitesse pour chaque robot
    robot_speed = [random.uniform(0.85, 1.15), random.uniform(0.85, 1.15)]

    # machine a etats
    STATE_THINK, STATE_REVEAL = "think", "reveal"
    state = STATE_THINK
    paused = False
    t_state = 0.0

    def deal():
        idx = random.sample(range(len(deck)), 3)
        c_center = Card(deck[idx[0]], pos_center, radius, renderer)
        c_left = Card(deck[idx[1]], pos_left, radius, renderer)
        c_right = Card(deck[idx[2]], pos_right, radius, renderer)
        m1 = common_symbol(deck[idx[1]], deck[idx[0]])
        m2 = common_symbol(deck[idx[2]], deck[idx[0]])
        # temps de reaction de chaque robot
        rt1 = random.uniform(0.7, 2.4) * robot_speed[0]
        rt2 = random.uniform(0.7, 2.4) * robot_speed[1]
        return {
            "center": c_center, "left": c_left, "right": c_right,
            "m1": m1, "m2": m2, "rt": [rt1, rt2],
            "winner": 0 if rt1 <= rt2 else 1,
        }

    round_data = deal()
    elapsed = [0.0, 0.0]
    found = [False, False]

    def draw_hud():
        # bandeau scores
        title = font_big.render("DOBBLE  —  2 robots theoriques", True, TXT)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 18))

        for i, (name, color, x) in enumerate(
            [("ROBOT 1", R1_COLOR, 250), ("ROBOT 2", R2_COLOR, 870)]
        ):
            label = font_mid.render(name, True, color)
            screen.blit(label, (x - label.get_width() // 2, 70))
            sc = font_big.render(str(scores[i]), True, color)
            screen.blit(sc, (x - sc.get_width() // 2, 96))
            st = "cherche..." if (state == STATE_THINK and not found[i]) else \
                 ("TROUVE !" if found[i] else "")
            stt = font_sm.render(st, True, color if found[i] else DIM)
            screen.blit(stt, (x - stt.get_width() // 2, 140))

        vs = font_mid.render("VS", True, DIM)
        screen.blit(vs, (560 - vs.get_width() // 2, 96))

        cl = font_sm.render("carte commune", True, DIM)
        screen.blit(cl, (560 - cl.get_width() // 2, 196))

        info = font_sm.render(
            f"manche {rounds}   |   ESPACE: pause   R: reset   ECHAP: quitter"
            + ("   [PAUSE]" if paused else ""),
            True, DIM,
        )
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT - 32))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                elif ev.key == pygame.K_r:
                    scores = [0, 0]
                    rounds = 0

        if not paused:
            t_state += dt
            if state == STATE_THINK:
                for i in (0, 1):
                    if not found[i]:
                        elapsed[i] += dt
                        if elapsed[i] >= round_data["rt"][i]:
                            found[i] = True
                # le premier robot a trouver remporte la manche
                w = round_data["winner"]
                if found[w]:
                    scores[w] += 1
                    rounds += 1
                    state = STATE_REVEAL
                    t_state = 0.0
            elif state == STATE_REVEAL:
                if t_state >= 1.8:
                    round_data = deal()
                    elapsed = [0.0, 0.0]
                    found = [False, False]
                    state = STATE_THINK
                    t_state = 0.0

        # --- rendu ---
        screen.fill(BG)
        w = round_data["winner"]
        hl_center = hl_left = hl_right = None
        if state == STATE_REVEAL:
            if w == 0:
                hl_center, hl_left = round_data["m1"], round_data["m1"]
            else:
                hl_center, hl_right = round_data["m2"], round_data["m2"]

        round_data["left"].draw(screen, hl_left, R1_COLOR, t_state)
        round_data["center"].draw(screen, hl_center,
                                  R1_COLOR if w == 0 else R2_COLOR, t_state)
        round_data["right"].draw(screen, hl_right, R2_COLOR, t_state)

        if state == STATE_REVEAL:
            wname = "ROBOT 1" if w == 0 else "ROBOT 2"
            wcol = R1_COLOR if w == 0 else R2_COLOR
            msg = font_big.render(f"{wname} marque le point !", True, wcol)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 78))

        draw_hud()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
