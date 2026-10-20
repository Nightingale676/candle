# 🕯️ Words to Candle

A screen filled with warm, glowing words slowly gathers into an ASCII candle. Once formed, the candle stays on screen with a gently flickering flame.

The artwork is made entirely from text characters and uses Python's standard library.

## ✨ Animation

### 📝 1. A screen full of words

Words fill the canvas and brighten during the opening 1.8 seconds.

### 🌀 2. Words gather into the candle

Over the next four seconds, the letters travel inward along curved paths and merge into the candle.

### 🕯️ 3. The finished candle

After 5.8 seconds, the candle remains intact while its flame flickers. The animation stays here until you replay or close it.

## 🚀 Run

You need Python 3. The window version uses Tkinter, which is included with many Python installations. No pip packages are required.

From this directory:

```sh
python eyes.py
```

Or from the repository root:

```sh
python fun/eye/eyes.py
```

On Windows, you can use `py` in place of `python`.

For output directly in a terminal:

```sh
python eyes.py --terminal
```

Use a terminal with ANSI true-color support and a monospace font. The terminal version adapts its character grid to the terminal size when it starts. If Tkinter cannot be imported, the program automatically starts in terminal mode.

## 🎮 Controls

| Mode | Control | Action |
| --- | --- | --- |
| Window | Space | Replay from the word-filled screen |
| Window | Escape or close button | Exit |
| Terminal | Ctrl+C | Exit |

## 🎨 Customize

Edit these values near the top of `eyes.py`:

| Setting | Default | Purpose |
| --- | --- | --- |
| `INTRO_WORDS` | LET, THE, WORLD, BURN, LIGHT, FLAME, GLOW, FIRE | Words filling the opening screen |
| `INTRO_HOLD` | `1.8` | Seconds before the words begin gathering |
| `MORPH_TIME` | `4.0` | Duration of the movement into the candle |
| `WIDTH`, `HEIGHT` | `144`, `76` | Character-grid dimensions |
| `ASCII_RAMP` | Sparse to dense characters | Characters used to shade the candle |
| `PALETTE` | 32 warm shades | Text colors |

## 📁 Files

```text
eyes.py
README.md
```
