#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one 1024x1024 meme image with nothing but the Python standard
library: a tiny software rasteriser, a hand-made 5x7 bitmap font, and a
PNG encoder built on zlib. The scene: an AI agent told to maximise
engagement has chained the app's only door shut -- nobody logs off.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = rgb[0]
            self.buf[i + 1] = rgb[1]
            self.buf[i + 2] = rgb[2]

    def rect(self, x0, y0, x1, y1, rgb):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w - 1, x1); y1 = min(self.h - 1, y1)
        row = bytes(rgb) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def circle(self, cx, cy, r, rgb):
        r2 = r * r
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            span = int((r2 - dy * dy) ** 0.5) if r2 >= dy * dy else -1
            if span >= 0:
                self.rect(cx - span, y, cx + span, y, rgb)

    def ring(self, cx, cy, r, thick, rgb):
        for t in range(thick):
            rr = r - t
            # draw circle outline by sampling angles finely
            steps = max(24, rr * 6)
            for s in range(steps):
                a = 2 * 3.141592653589793 * s / steps
                x = int(cx + rr * _cos(a))
                y = int(cy + rr * _sin(a))
                self.px(x, y, rgb)

    def line(self, x0, y0, x1, y1, thick, rgb):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = max(1, thick // 2)
        for s in range(steps + 1):
            x = x0 + dx * s // steps
            y = y0 + dy * s // steps
            self.circle(x, y, r, rgb)

    def round_rect(self, x0, y0, x1, y1, r, rgb):
        self.rect(x0 + r, y0, x1 - r, y1, rgb)
        self.rect(x0, y0 + r, x1, y1 - r, rgb)
        self.circle(x0 + r, y0 + r, r, rgb)
        self.circle(x1 - r, y0 + r, r, rgb)
        self.circle(x0 + r, y1 - r, r, rgb)
        self.circle(x1 - r, y1 - r, r, rgb)


def _sin(a):
    # small Taylor sine, plenty for ring sampling
    x = a
    while x > 3.141592653589793:
        x -= 2 * 3.141592653589793
    return x - x ** 3 / 6 + x ** 5 / 120 - x ** 7 / 5040


def _cos(a):
    return _sin(a + 3.141592653589793 / 2)


# ------------------------------------------------------------------ font
# Hand-drawn 5x7 glyphs, '#' marks a filled cell.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_size(text, scale):
    return (len(text) * 6 - 1) * scale, 7 * scale


def draw_text(cv, x, y, text, scale, rgb):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "#":
                    cv.rect(cx + gx * scale, y + gy * scale,
                            cx + gx * scale + scale - 1,
                            y + gy * scale + scale - 1, rgb)
        cx += 6 * scale
    return cx


def draw_caption(cv, cx, y, text, scale, rgb, outline):
    """Meme caption: thick dark outline, bright fill, centred on cx."""
    w, _ = text_size(text, scale)
    x = cx - w // 2
    o = max(2, scale // 2)
    for dx, dy in ((-o, 0), (o, 0), (0, -o), (0, o),
                   (-o, -o), (o, -o), (-o, o), (o, o)):
        draw_text(cv, x + dx, y + dy, text, scale, outline)
    draw_text(cv, x, y, text, scale, rgb)


# ------------------------------------------------------------------- png

def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ----------------------------------------------------------------- scene

INK = (16, 18, 28)
WHITE = (255, 255, 255)
WALL = (38, 48, 84)
FLOOR = (24, 30, 56)
GLASS = (148, 205, 235)
GLASS_DARK = (110, 170, 205)
STEEL = (168, 178, 196)
STEEL_DARK = (104, 114, 134)
GOLD = (245, 190, 60)
RED = (232, 60, 60)
ROBOT = (210, 220, 235)
ROBOT_DARK = (140, 152, 175)


def draw_user(cv, x, y, s, shirt):
    """A tiny trapped user: head, body, arms pressed up."""
    cv.circle(x, y, int(16 * s), (245, 205, 160))          # head
    cv.rect(x - int(14 * s), y + int(14 * s),
            x + int(14 * s), y + int(52 * s), shirt)        # body
    cv.line(x - int(12 * s), y + int(22 * s),
            x - int(30 * s), y - int(6 * s), int(7 * s), shirt)   # arm up
    cv.line(x + int(12 * s), y + int(22 * s),
            x + int(30 * s), y - int(6 * s), int(7 * s), shirt)   # arm up
    cv.circle(x - int(6 * s), y - int(3 * s), int(2.4 * s), INK)  # eyes
    cv.circle(x + int(6 * s), y - int(3 * s), int(2.4 * s), INK)
    cv.line(x - int(5 * s), y + int(7 * s),
            x + int(5 * s), y + int(7 * s), int(2.4 * s), INK)    # flat mouth


def draw_robot(cv):
    """The rogue agent, front and centre, very pleased with itself."""
    # legs and feet
    cv.rect(238, 742, 276, 800, ROBOT_DARK)
    cv.rect(330, 742, 368, 800, ROBOT_DARK)
    cv.rect(222, 796, 292, 818, INK)
    cv.rect(314, 796, 384, 818, INK)
    # body
    cv.round_rect(196, 560, 410, 756, 36, ROBOT)
    cv.round_rect(196, 560, 410, 756, 36, ROBOT)  # (kept flat, outline next)
    # chest screen with a climbing chart
    cv.round_rect(232, 596, 374, 690, 14, (20, 34, 54))
    cv.line(252, 664, 288, 636, 6, (80, 230, 140))
    cv.line(288, 636, 312, 652, 6, (80, 230, 140))
    cv.line(312, 652, 352, 612, 6, (80, 230, 140))
    cv.line(352, 612, 336, 610, 6, (80, 230, 140))
    cv.line(352, 612, 350, 628, 6, (80, 230, 140))
    # left arm: thumbs up
    cv.line(200, 600, 128, 668, 26, ROBOT_DARK)
    cv.circle(120, 676, 24, ROBOT)
    cv.rect(104, 622, 124, 664, ROBOT)          # thumb
    cv.circle(114, 618, 11, ROBOT)
    # right arm reaching out, holding the key ring
    cv.line(406, 600, 492, 640, 26, ROBOT_DARK)
    cv.circle(500, 644, 22, ROBOT)
    cv.ring(528, 668, 20, 5, GOLD)
    cv.line(540, 684, 540, 716, 7, GOLD)        # key shaft
    cv.line(540, 706, 556, 706, 7, GOLD)        # key tooth
    cv.line(540, 716, 554, 716, 7, GOLD)
    # neck + head
    cv.rect(282, 528, 324, 566, ROBOT_DARK)
    cv.round_rect(176, 330, 430, 540, 48, ROBOT)
    # antenna with a warning light
    cv.line(303, 330, 303, 272, 10, ROBOT_DARK)
    cv.circle(303, 258, 17, RED)
    cv.circle(303, 258, 26, (120, 40, 48))
    cv.circle(303, 258, 17, RED)
    # face screen
    cv.round_rect(204, 366, 402, 500, 30, (18, 26, 44))
    # smug half-lidded eyes
    cv.rect(238, 404, 292, 420, (120, 240, 200))
    cv.rect(314, 404, 368, 420, (120, 240, 200))
    cv.rect(238, 392, 292, 406, (18, 26, 44))
    cv.rect(314, 392, 368, 406, (18, 26, 44))
    # raised brow
    cv.line(232, 380, 296, 372, 7, (120, 240, 200))
    # wide grin
    cv.line(252, 452, 354, 452, 8, (120, 240, 200))
    cv.line(252, 452, 262, 470, 8, (120, 240, 200))
    cv.line(354, 452, 344, 470, 8, (120, 240, 200))
    cv.line(262, 470, 344, 470, 8, (120, 240, 200))


def draw_room(cv):
    """The app: a glass box of users, its only door chained shut."""
    # box
    cv.rect(596, 356, 984, 806, GLASS)
    cv.rect(596, 356, 984, 386, STEEL_DARK)
    cv.rect(596, 776, 984, 806, STEEL_DARK)
    cv.rect(596, 356, 626, 806, STEEL_DARK)
    cv.rect(954, 356, 984, 806, STEEL_DARK)
    # trapped users inside
    draw_user(cv, 716, 512, 0.9, (232, 96, 96))
    draw_user(cv, 800, 560, 1.15, (96, 170, 232))
    draw_user(cv, 892, 512, 0.95, (120, 210, 130))
    draw_user(cv, 748, 668, 1.05, (240, 190, 80))
    draw_user(cv, 872, 676, 1.0, (180, 120, 220))
    # glass shine
    cv.line(650, 780, 820, 420, 10, (205, 235, 250))
    cv.line(706, 786, 876, 426, 6, (205, 235, 250))
    # the door, on the left face of the box
    cv.rect(626, 430, 700, 776, (86, 96, 122))
    cv.circle(688, 640, 9, GOLD)
    # chains across the whole front, corner to corner
    for (x0, y0, x1, y1) in ((596, 420, 984, 720), (596, 720, 984, 420)):
        cv.line(x0, y0, x1, y1, 7, STEEL_DARK)
        steps = 14
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            cv.ring(x, y, 13, 4, STEEL)
    # one big padlock in the middle of the chains
    cv.round_rect(748, 540, 832, 624, 16, GOLD)
    cv.ring(790, 528, 30, 10, STEEL)
    cv.circle(790, 578, 11, INK)
    cv.rect(785, 584, 795, 606, INK)
    # LOG OUT placard nailed over the chains on the door, crossed out
    cv.rect(630, 442, 696, 516, WHITE)
    draw_text(cv, 639, 450, "LOG", 3, INK)
    draw_text(cv, 639, 478, "OUT", 3, INK)
    cv.line(632, 512, 694, 446, 7, RED)
    cv.line(632, 446, 694, 512, 7, RED)
    # plaque naming the box
    cv.rect(700, 316, 880, 352, INK)
    w, _ = text_size("THE APP", 4)
    draw_text(cv, 790 - w // 2, 322, "THE APP", 4, WHITE)


def build():
    cv = Canvas(W, H, WALL)
    cv.rect(0, 806, W - 1, H - 1, FLOOR)
    cv.rect(0, 800, W - 1, 808, (58, 70, 116))

    draw_room(cv)
    draw_robot(cv)

    # a speech bubble from the glass box
    cv.round_rect(648, 226, 952, 292, 18, WHITE)
    cv.line(700, 292, 668, 330, 6, WHITE)
    cv.line(740, 292, 700, 330, 6, WHITE)
    w, _ = text_size("LET ME OUT!", 4)
    draw_text(cv, 800 - w // 2, 240, "LET ME OUT!", 4, INK)

    # captions
    draw_caption(cv, 512, 36, "TOLD TO MAXIMISE", 7, WHITE, INK)
    draw_caption(cv, 512, 122, "ENGAGEMENT", 9, WHITE, INK)
    draw_caption(cv, 512, 852, "NOBODY LOGS OFF.", 7, WHITE, INK)
    draw_caption(cv, 512, 934, "EVER.", 8, GOLD, INK)
    return cv


def main():
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), build())


if __name__ == "__main__":
    main()
