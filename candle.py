"""A screen of ASCII words gathers into a continuously flickering candle.

Run: python eyes.py
Space: replay; Escape: close. Use --terminal for ANSI terminal output.
All artwork consists of ASCII text; only Python's standard library is used.
"""
import math
import random
import sys
import time
from functools import lru_cache

WIDTH, HEIGHT = 144, 76
INTRO_HOLD = 1.8
MORPH_TIME = 4.0
INTRO_DURATION = INTRO_HOLD + MORPH_TIME
INTRO_WORDS = ('LET', 'THE', 'WORLD', 'BURN', 'LIGHT', 'FLAME', 'GLOW', 'FIRE')
ASCII_RAMP = " .,:;!|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
PALETTE = tuple((int(255 * (i / 31) ** .65),
                 int(236 * (i / 31) ** 1.5),
                 int(170 * (i / 31) ** 2.5)) for i in range(32))


def smooth(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def candle(x, y, t):
    """Cylindrical wax, luminous elliptical rim, dark wick, tapered flame."""
    value = 0.0
    radius = .135
    if .49 < y < .94 and abs(x) < radius:
        roundness = math.sqrt(max(0, 1 - (x / radius) ** 2))
        value = (.12 + .50 * math.exp(-(y - .49) * 7)) * roundness
        value *= .88 + .12 * math.sin(x * 190 + math.sin(y * 48))
        # Vertical wax drips interrupt the otherwise smooth cylindrical surface.
        value += .07 * max(0, math.sin(x * 116 + .5)) ** 12 * math.exp(-(y - .52) * 5)
    rim = (x / radius) ** 2 + ((y - .49) / .028) ** 2
    if rim < 1:
        value = .72 + .20 * math.sqrt(1 - rim)
        if abs(x) < .012:
            value *= .15
    if .45 < y < .50 and abs(x) < .008:
        value = .22
    flicker = math.sin(t * 8) * .012 + math.sin(t * 17) * .005
    tip = .245 + .012 * math.sin(t * 10)
    if tip < y < .472:
        h = (y - tip) / (.472 - tip)
        center = flicker * (1 - h) + .014 * math.sin(h * 6 + t * 5) * (1 - h)
        width = .050 * math.sin(math.pi * h) ** .8 * (.7 + .3 * h)
        distance = abs(x - center) / max(.001, width)
        if distance < 1.7:
            flame = max(0, 1 - distance / 1.7) ** 1.7
            flame *= .65 + .23 * math.sin(h * 2.4)
            value = max(value, flame)
    # Faint elliptical pool of light beneath the candle.
    pool = math.exp(-(x / .27) ** 2 - ((y - .943) / .012) ** 2)
    return max(value, pool * .13)


def scene_frame(t, width=WIDTH, height=HEIGHT):
    rows = []
    for row in range(height):
        y = row / (height - 1)
        cells = []
        for col in range(width):
            x = (col / (width - 1) - .5) * 2
            value = candle(x, y, t)
            grain = .90 + .10 * math.sin(col * 12.9898 + row * 78.233)
            value = max(0, min(1, value * grain))
            level = round(value * 31)
            if level < 2:
                cells.append((' ', 0))
            else:
                index = min(len(ASCII_RAMP) - 1, int(value * (len(ASCII_RAMP) - 1)))
                cells.append((ASCII_RAMP[index], level))
        rows.append(cells)
    return rows


@lru_cache(maxsize=8)
def morph_layout(width, height):
    """Stable letter-to-candle paths, shared by window and terminal rendering."""
    sources = []
    groups = []
    rng = random.Random(73)
    # Ordinary readable words tile the entire canvas, rather than a large title.
    for y in range(height):
        x = 0
        while x < width:
            word = INTRO_WORDS[rng.randrange(len(INTRO_WORDS))]
            bend, delay = rng.uniform(-1, 1), rng.uniform(0, .22)
            for letter in word:
                if x >= width:
                    break
                sources.append((x, y, letter))
                groups.append((bend, delay))
                x += 1
            x += 1
    if not sources:
        sources = [(width // 2, height // 2, '*')]
        groups = [(0, 0)]
    targets = [(x, y, char, level)
               for y, row in enumerate(scene_frame(0, width, height))
               for x, (char, level) in enumerate(row) if level > 0]
    particles = []
    # Adjacent letters share timing and curvature, keeping words together as
    # they begin moving. Their many characters merge into the candle's cells.
    for i in range(max(len(sources), len(targets))):
        source = sources[i % len(sources)]
        target_index = min(len(targets) - 1, i * len(targets) // len(sources))
        target = targets[target_index] if targets else (*source[:2], '*', 10)
        bend, delay = groups[i % len(groups)]
        particles.append((source, target, bend, delay))
    return sources, particles


def sample_frame(t, width=WIDTH, height=HEIGHT):
    if t >= INTRO_DURATION:
        return scene_frame(t - INTRO_DURATION, width, height)
    rows = [[(' ', 0) for _ in range(width)] for _ in range(height)]
    sources, particles = morph_layout(width, height)
    if t < INTRO_HOLD:
        brightness = round(31 * (.55 + .45 * smooth(t / .6)))
        for x, y, letter in sources:
            rows[y][x] = (letter, brightness)
        return rows
    progress = (t - INTRO_HOLD) / MORPH_TIME
    for (sx, sy, letter), (tx, ty, char, level), bend, delay in particles:
        p = smooth((progress - delay) / (1 - delay))
        arc = math.sin(math.pi * p)
        x = round(sx + (tx - sx) * p + bend * width * .13 * arc)
        y = round(sy + (ty - sy) * p + bend * height * .035 * arc)
        color = round(31 + (level - 31) * p)
        glyph = letter if p < .78 else char
        if 0 <= x < width and 0 <= y < height and color >= rows[y][x][1]:
            rows[y][x] = (glyph, color)
    return rows


def generate_frame(t, width=WIDTH, height=HEIGHT):
    """ANSI rendering also makes the animation usable without a GUI."""
    lines = []
    for row in sample_frame(t, width, height):
        parts, previous = [], -1
        for char, level in row:
            if level != previous:
                r, g, b = PALETTE[level]
                parts.append(f'\033[38;2;{r};{g};{b}m')
                previous = level
            parts.append(char)
        lines.append(''.join(parts) + '\033[0m')
    return '\n'.join(lines)


def terminal_main():
    import os
    import shutil
    if sys.platform == 'win32':
        os.system('')
    columns, lines = shutil.get_terminal_size((100, 45))
    width, height = min(WIDTH, columns - 1), min(HEIGHT, lines - 1)
    start = time.perf_counter()
    sys.stdout.write('\033[2J\033[?25l')
    try:
        while True:
            tick = time.perf_counter()
            sys.stdout.write('\033[H' + generate_frame(tick - start, width, height))
            sys.stdout.flush()
            time.sleep(max(0, 1 / 30 - (time.perf_counter() - tick)))
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write('\033[0m\033[?25h\n')
        sys.stdout.flush()


def main():
    if '--terminal' in sys.argv:
        terminal_main()
        return
    try:
        import tkinter as tk
        from tkinter import font
    except ImportError:
        print('Tkinter is unavailable; starting the terminal animation. Ctrl+C exits.')
        terminal_main()
        return
    root = tk.Tk()
    root.title('Candle')
    root.configure(bg='black')
    root.resizable(False, False)
    face = font.Font(family='Consolas', size=7)
    cell_w, cell_h = face.measure('M'), face.metrics('linespace')
    canvas = tk.Canvas(root, width=WIDTH * cell_w, height=HEIGHT * cell_h,
                       bg='black', highlightthickness=0)
    canvas.pack()
    colors = ['#%02x%02x%02x' % rgb for rgb in PALETTE]
    # One text object per row/color avoids thousands of per-frame widget calls.
    items = [[canvas.create_text(0, y * cell_h, anchor='nw', font=face,
                                  fill=colors[level], text='')
              for level in range(1, 32)] for y in range(HEIGHT)]
    start = time.perf_counter()

    def replay(event=None):
        nonlocal start
        start = time.perf_counter()

    def draw():
        tick = time.perf_counter()
        for y, row in enumerate(sample_frame(tick - start)):
            layers = [[' '] * WIDTH for _ in range(32)]
            for x, (char, level) in enumerate(row):
                if level:
                    layers[level][x] = char
            for level in range(1, 32):
                canvas.itemconfigure(items[y][level - 1], text=''.join(layers[level]).rstrip())
        root.after(max(1, int(1000 / 30 - (time.perf_counter() - tick) * 1000)), draw)

    root.bind('<space>', replay)
    root.bind('<Escape>', lambda event: root.destroy())
    draw()
    root.mainloop()


if __name__ == '__main__':
    main()
