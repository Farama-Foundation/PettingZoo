"""Pygame rendering for the Hanabi environment.

The game state is read from the string produced by the underlying OpenSpiel
``pyspiel`` state (``str(game_state)``), whose format is defined by the Hanabi
Learning Environment. A typical string looks like::

    Life tokens: 3
    Info tokens: 8
    Fireworks: R1 Y0 G2 W0 B1
    Hands:
    Cur player
    R1 || XX|RYGWB12345
    ...
    -----
    Y3 || XX|RYGWB12345
    ...
    Deck size: 40
    Discards: R1 Y5 G2

Colors are encoded as the letters ``RYGWB`` (red, yellow, green, white, blue)
and ranks as ``12345``. Fireworks are given as ``<color><height>`` where the
height is the value of the highest card played for that color (0 if empty).

The parsing here is kept isolated from the pygame drawing so that it can be
unit tested without a rendering backend.
"""

from __future__ import annotations

import os

# Card art is 64x88 pixels. Everything is laid out relative to that.
CARD_W, CARD_H = 64, 88

# Order used to lay out the fireworks and to name the sprite files.
COLOR_ORDER = ["R", "Y", "G", "W", "B"]
COLOR_NAME = {"R": "red", "Y": "yellow", "G": "green", "W": "white", "B": "blue"}
COLOR_RGB = {
    "R": (214, 48, 49),
    "Y": (240, 196, 25),
    "G": (46, 204, 90),
    "W": (232, 232, 238),
    "B": (52, 120, 232),
}

# Palette tuned to sit behind the navy fireworks card art.
BG_TOP = (18, 22, 40)
BG_BOTTOM = (10, 12, 24)
PANEL = (30, 36, 60)
PANEL_LIGHT = (42, 50, 80)
TEXT = (232, 236, 245)
TEXT_DIM = (150, 160, 185)
INFO_TOKEN = (90, 170, 255)
LIFE_TOKEN = (232, 72, 88)
HIGHLIGHT = (255, 214, 92)


def parse_hanabi_state(text: str) -> dict:
    """Parse an OpenSpiel Hanabi state string into a structured dict.

    Returns a dict with keys:
        ``life`` (int), ``info`` (int), ``deck`` (int),
        ``fireworks`` (dict color-letter -> height),
        ``hands`` (list of list of card strings, e.g. ``"R1"`` or ``"XX"``),
        ``cur_player`` (int index into ``hands``),
        ``discards`` (list of card strings).
    """
    data = {
        "life": 0,
        "info": 0,
        "deck": 0,
        "fireworks": {},
        "hands": [],
        "cur_player": 0,
        "discards": [],
    }
    lines = text.split("\n")

    hands_start = hands_end = None
    for i, raw in enumerate(lines):
        ln = raw.strip()
        if ln.startswith("Life tokens:"):
            data["life"] = int(ln.split(":", 1)[1])
        elif ln.startswith("Info tokens:"):
            data["info"] = int(ln.split(":", 1)[1])
        elif ln.startswith("Fireworks:"):
            for tok in ln[len("Fireworks:") :].split():
                data["fireworks"][tok[0]] = int(tok[1:])
        elif ln == "Hands:":
            hands_start = i + 1
        elif ln.startswith("Deck size:"):
            data["deck"] = int(ln.split(":", 1)[1])
            hands_end = i
        elif ln.startswith("Discards:"):
            data["discards"] = [t for t in ln[len("Discards:") :].split() if t]

    # Split the hands section (one group per player, separated by "-----").
    if hands_start is not None and hands_end is not None:
        groups: list[list[str]] = [[]]
        for raw in lines[hands_start:hands_end]:
            ln = raw.strip()
            if ln == "-----":
                groups.append([])
            elif ln:
                groups[-1].append(ln)
        for idx, group in enumerate(groups):
            cards = []
            for ln in group:
                if ln == "Cur player":
                    data["cur_player"] = idx
                elif "||" in ln:
                    cards.append(ln.split("||", 1)[0].strip())
            data["hands"].append(cards)

    return data


class HanabiRenderer:
    """Draws a Hanabi board with pygame using the commissioned card art."""

    def __init__(self, colors: int = 5, ranks: int = 5, players: int = 2):
        import pygame

        pygame.font.init()
        self.colors = colors
        self.ranks = ranks
        self.players = players
        self._img_dir = os.path.join(os.path.dirname(__file__), "img")
        self._sprite_cache: dict[tuple, pygame.Surface] = {}

        self.scale = 1.6  # base scale for hand cards
        self.card_w = int(CARD_W * self.scale)
        self.card_h = int(CARD_H * self.scale)
        self.pad = 22
        self.hand_gap = 14

        self.width = max(
            980,
            self.pad * 2 + players * 0 + 5 * (self.card_w + self.hand_gap),
        )
        self.header_h = 96
        self.fireworks_h = self.card_h + 60
        self.hand_row_h = self.card_h + 52
        self.discard_h = int(CARD_H * 0.7) * 2 + 60
        self.height = (
            self.header_h
            + self.fireworks_h
            + players * self.hand_row_h
            + self.discard_h
            + self.pad
        )

        self.font_big = pygame.font.SysFont("arialrounded,arial", 30, bold=True)
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("arial", 15, bold=True)

    # -- asset loading ------------------------------------------------------
    def _sprite(self, name: str, w: int, h: int):
        import pygame

        key = (name, w, h)
        if key not in self._sprite_cache:
            surf = pygame.image.load(os.path.join(self._img_dir, f"{name}.png"))
            # convert_alpha() needs a video mode; skip it for headless
            # rgb_array rendering where no display has been created.
            if pygame.display.get_surface() is not None:
                surf = surf.convert_alpha()
            # scale() uses nearest-neighbour, keeping the pixel art crisp.
            self._sprite_cache[key] = pygame.transform.scale(surf, (w, h))
        return self._sprite_cache[key]

    def _card_sprite(self, card: str, w: int, h: int):
        """Sprite for a card string like ``"R3"``; ``"XX"`` -> card back."""
        if card == "XX" or len(card) < 2 or card[0] not in COLOR_NAME:
            return self._sprite("back", w, h)
        return self._sprite(f"{COLOR_NAME[card[0]]}_{card[1]}", w, h)

    # -- drawing helpers ----------------------------------------------------
    def _text(self, surface, text, pos, font=None, color=TEXT, center=False):
        font = font or self.font
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        surface.blit(img, rect)
        return rect

    def _empty_slot(self, surface, x, y, w, h, color_letter):
        import pygame

        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (0, 0, 0, 60), rect, border_radius=8)
        pygame.draw.rect(
            surface, COLOR_RGB[color_letter], rect, width=3, border_radius=8
        )
        self._text(
            surface,
            color_letter,
            rect.center,
            font=self.font_big,
            color=COLOR_RGB[color_letter],
            center=True,
        )

    def _token_row(self, surface, x, y, label, count, maxcount, color):
        import pygame

        self._text(surface, label, (x, y - 2), font=self.font_small, color=TEXT_DIM)
        r = 9
        cx = x + 44
        for i in range(maxcount):
            center = (cx + i * (2 * r + 6), y + 8)
            if i < count:
                pygame.draw.circle(surface, color, center, r)
                pygame.draw.circle(surface, (255, 255, 255), center, r, 1)
            else:
                pygame.draw.circle(surface, PANEL_LIGHT, center, r)
        self._text(
            surface,
            str(count),
            (cx + maxcount * (2 * r + 6) + 4, y - 4),
            font=self.font,
            color=color,
        )

    # -- main entry point ---------------------------------------------------
    def draw(self, data: dict, max_info: int = 8, max_life: int = 3):
        """Render the parsed ``data`` to a new pygame Surface and return it."""
        import pygame

        surface = pygame.Surface((self.width, self.height))
        # vertical gradient background
        for yy in range(self.height):
            t = yy / max(1, self.height - 1)
            col = [int(BG_TOP[c] + (BG_BOTTOM[c] - BG_TOP[c]) * t) for c in range(3)]
            pygame.draw.line(surface, col, (0, yy), (self.width, yy))

        present_colors = COLOR_ORDER[: self.colors]
        score = sum(data["fireworks"].get(c, 0) for c in present_colors)

        # ---- header --------------------------------------------------------
        self._text(surface, "Hanabi", (self.pad, 20), font=self.font_big)
        self._text(
            surface,
            f"Score {score} / {5 * self.colors}",
            (self.pad, 58),
            font=self.font,
            color=HIGHLIGHT,
        )
        # tokens (right aligned block)
        tok_x = self.width - 320
        self._token_row(surface, tok_x, 22, "Info", data["info"], max_info, INFO_TOKEN)
        self._token_row(surface, tok_x, 56, "Life", data["life"], max_life, LIFE_TOKEN)
        # deck
        deck_w, deck_h = int(CARD_W * 0.7), int(CARD_H * 0.7)
        deck_x = self.width - deck_w - self.pad
        surface.blit(self._sprite("back", deck_w, deck_h), (deck_x, 20))
        self._text(
            surface,
            f"x{data['deck']}",
            (deck_x + deck_w // 2, 20 + deck_h + 12),
            font=self.font_small,
            color=TEXT_DIM,
            center=True,
        )

        y = self.header_h

        # ---- fireworks -----------------------------------------------------
        self._text(surface, "Fireworks", (self.pad, y), font=self.font, color=TEXT_DIM)
        fw_y = y + 28
        total_w = self.colors * self.card_w + (self.colors - 1) * self.hand_gap
        start_x = (self.width - total_w) // 2
        for i, c in enumerate(present_colors):
            cx = start_x + i * (self.card_w + self.hand_gap)
            height = data["fireworks"].get(c, 0)
            if height > 0:
                surface.blit(
                    self._card_sprite(f"{c}{height}", self.card_w, self.card_h),
                    (cx, fw_y),
                )
            else:
                self._empty_slot(surface, cx, fw_y, self.card_w, self.card_h, c)
        y += self.fireworks_h

        # ---- hands ---------------------------------------------------------
        for p, hand in enumerate(data["hands"]):
            is_cur = p == data["cur_player"]
            row_rect = pygame.Rect(
                self.pad // 2, y, self.width - self.pad, self.hand_row_h - 12
            )
            pygame.draw.rect(
                surface,
                PANEL if not is_cur else PANEL_LIGHT,
                row_rect,
                border_radius=10,
            )
            if is_cur:
                pygame.draw.rect(
                    surface, HIGHLIGHT, row_rect, width=3, border_radius=10
                )
            label = f"Player {p}" + ("  (current turn)" if is_cur else "")
            self._text(
                surface,
                label,
                (self.pad, y + 10),
                font=self.font,
                color=HIGHLIGHT if is_cur else TEXT,
            )
            card_y = y + 8
            hand_w = len(hand) * self.card_w + max(0, len(hand) - 1) * self.hand_gap
            hx = self.width - self.pad - hand_w
            for card in hand:
                surface.blit(
                    self._card_sprite(card, self.card_w, self.card_h), (hx, card_y)
                )
                hx += self.card_w + self.hand_gap
            y += self.hand_row_h

        # ---- discards ------------------------------------------------------
        self._text(surface, "Discards", (self.pad, y), font=self.font, color=TEXT_DIM)
        dw, dh = int(CARD_W * 0.7), int(CARD_H * 0.7)
        dx, dy = self.pad, y + 28
        gap = 6
        discards = sorted(
            data["discards"],
            key=lambda cc: (
                COLOR_ORDER.index(cc[0]) if cc and cc[0] in COLOR_ORDER else 9,
                cc[1:] if len(cc) > 1 else "",
            ),
        )
        for card in discards:
            if dx + dw > self.width - self.pad:
                dx = self.pad
                dy += dh + gap
            surface.blit(self._card_sprite(card, dw, dh), (dx, dy))
            dx += dw + gap
        if not discards:
            self._text(
                surface, "none", (dx, dy + 8), font=self.font_small, color=TEXT_DIM
            )

        return surface
