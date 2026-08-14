# 🍒 CherryOS

A lightweight, gaming-focused operating system for the Raspberry Pi Pico, written from scratch in MicroPython — its own kernel, its own API layer, its own apps.

No Linux, no existing RTOS — just a 128x64 OLED, three buttons, a buzzer, and a custom OS built around them.

> 🎉 **v1.0** — first stable release. Runs the whole current app set (games, CORA, COSS, settings) reliably on real hardware.

---

## ✨ Features

- Animated boot screen with progress bar
- Password-protected lock screen (4-digit PIN)
- Built-in mini-games: Simon, PopIt (reaction), Dice, Clicker
- Custom JSON-based audio player (`CherryPlayer`)
- **CORA** (Cherry Os Run App) — a launcher that scans the flash for external `.py` files and lets you run them, with a built-in scanner that flags suspicious code (`import _kernel`, `os.remove`, file writes) and requires a password before running it. Includes an **Exit** option so you're never stuck in the launcher.
- **COSS** — a minimal BIOS-like mode: hard reset, system info, skip straight to CherryOS
- Compact **carousel-style settings menu** — one option at a time (`< Change volume >`), cycle with Next/Prev, confirm with Enter
- Persistent settings via `config.json` (button names, volume, password, saved time, battery display toggle)
- Battery percentage support (3.0V–4.2V range) with a real low-power `lightsleep()` sleep mode and automatic safe shutdown on critically low voltage
- Shutdown-reason tracking (power on, watchdog reset, soft reset, low battery, etc.)
- Clean `CherryAPI` layer — write your own app without ever touching the kernel

---

## 🔌 Hardware

| Component              | Pin (GPIO) |
|-------------------------|-----------|
| OLED SSD1306 (I2C) SDA  | 0         |
| OLED SSD1306 (I2C) SCL  | 1         |
| Button — Previous       | 2         |
| Button — Enter          | 3         |
| Button — Next           | 4         |
| Passive buzzer          | 5         |
| Onboard LED             | 25 (built-in) |

Display: SSD1306 128x64, I2C.
Buttons are wired with internal pull-ups (`Pin.PULL_UP`) — connect each button between its GPIO and GND.

> GPIO pins are configurable at the top of `kernel.py` if your wiring differs.

---

## 🚀 Installation

**1. Flash MicroPython onto your Pico first** (one-time step, via BOOTSEL mode + the official `.uf2` firmware from [micropython.org](https://micropython.org/download/RPI_PICO/)).

**2. Do NOT use BOOTSEL mode for CherryOS itself** — after MicroPython is on the board, everything below is done over USB serial with `mpremote`, not by dragging files into BOOTSEL storage.

**3. Clone or download this repo:**
```bash
git clone https://github.com/Cat0Ukraine/CherryOS.git
cd CherryOS
```

**4. Install mpremote (if you don't have it):**
```bash
pip install mpremote
```

**5. Flash CherryOS to your Pico:**

One script, works the same on Linux, macOS, and Windows:

```bash
python flash.py
```

It will ask you:
```
COM port (leave empty for auto-detect):
Run CherryOS after flashing? (Y/n):
```

Just press Enter twice for the default (auto-detect port, run immediately after flashing). It copies `CherryOS.py`, `kernel.py`, `main.py`, and `CherryAPI.py` onto the board.

---

## 🕹️ Controls

CherryOS reads button roles from `config.json`, so labels shown on-screen (e.g. "Press black button") adapt to whatever names you've set for the buttons.

| Button (default GPIO) | Role    |
|------------------------|---------|
| GPIO 4                 | Next    |
| GPIO 3                 | Enter / OK |
| GPIO 2                 | Previous |

Default password: `0000` (change it from Settings → Set password).

---

## 🧩 Adding your own app (via CORA)

Any standalone `.py` file placed on the Pico's flash (that isn't `main.py`, `kernel.py`, `CherryAPI.py`, or `CherryOS.py`) will show up in the **CORA** launcher automatically, right below the built-in **Exit** option. Your app only needs to import `CherryAPI` — never `kernel` directly, that's the whole point of the API layer, it keeps the kernel safe from apps that misbehave.

**Minimal example** — enough to get something on screen:

```python
from CherryAPI import CherryAPI
import time

def run():
    CherryAPI.fill(0)
    CherryAPI.text("Hello from my app!", 0, 0, 1)
    CherryAPI.show()
    time.sleep(2)

run()
```

Save it as `myapp.py`, flash it onto the Pico alongside the other files (or drop it in with `mpremote cp`), and it appears in CORA immediately — no registration, no extra config.

CORA runs a basic safety scan on any file before launching it — code containing `import _kernel`, `os.remove`, or file-write operations will trigger a warning and require the password before it's allowed to run.

**Full example — a small game (`dodger.py`):**

This one shows movement, collision, scoring, and a game-over screen — a solid template for building your own game on top of.

```python
# dodger.py — example CORA app for CherryOS
# A tiny "dodge the falling blocks" game.
# Controls: Next/Prev move left/right, Enter exits.

from CherryAPI import CherryAPI
import time
import random

volume = 8192


def run():
    player_x = 60
    blocks = []  # each block: [x, y]
    score = 0
    speed = 1.5
    alive = True
    spawn_timer = 0

    CherryAPI.fill(0)
    CherryAPI.text("Dodger", 0, 0, 1)
    CherryAPI.text("Next/Prev = move", 0, 20, 1)
    CherryAPI.text("Black = start", 0, 32, 1)
    CherryAPI.show()
    while CherryAPI.pressed(2):
        pass
    while not CherryAPI.pressed(2):
        pass

    while alive:
        if CherryAPI.pressed(1) and player_x < 118:
            player_x += 4
        if CherryAPI.pressed(3) and player_x > 0:
            player_x -= 4

        spawn_timer += 1
        if spawn_timer > max(10, 30 - int(score / 5)):
            spawn_timer = 0
            blocks.append([random.randint(0, 118), 0])

        for b in blocks:
            b[1] += speed

        for b in blocks:
            if b[1] > 58 and player_x < b[0] + 8 and player_x + 8 > b[0]:
                alive = False

        blocks = [b for b in blocks if b[1] < 64]
        score += 1

        CherryAPI.fill(0)
        CherryAPI.text(str(score // 10), 0, 0, 1)
        CherryAPI.fill_rect(player_x, 58, 8, 6, 1)
        for b in blocks:
            CherryAPI.fill_rect(b[0], int(b[1]), 8, 4, 1)
        CherryAPI.show()
        time.sleep(0.03)

    CherryAPI.fill(0)
    CherryAPI.text("Game over!", 0, 0, 1)
    CherryAPI.text(f"Score: {score // 10}", 0, 12, 1)
    CherryAPI.text("Black - exit", 0, 40, 1)
    CherryAPI.sound(300, 0.3, volume)
    CherryAPI.show()
    while not CherryAPI.pressed(2):
        pass
    while CherryAPI.pressed(2):
        pass


run()
```

**A few patterns worth reusing from this example:**
- Wait for a "clean" button press before starting (`while CherryAPI.pressed(2): pass` then `while not CherryAPI.pressed(2): pass`) — avoids accidentally re-triggering the game instantly if Enter was held down from a previous screen
- Keep game state in local variables inside `run()`, not globals — CORA re-imports the module fresh each launch
- End with a game-over screen that waits for Enter before returning, so the player sees their result instead of snapping straight back to the CORA menu
- `CherryAPI.fill_rect(x, y, width, height, color)` is your main drawing tool for anything beyond text — cheap and fast on a 128x64 mono display

---

## 📁 Project structure

```
kernel.py      # Low-level hardware access (display driver, buttons, buzzer, config, power). Don't edit unless you know what you're doing.
CherryAPI.py   # Safe API layer between the kernel and everything else.
main.py        # Bootloader — decides whether to load CherryOS or COSS.
CherryOS.py    # The OS itself: UI, games, settings, CORA.
COSS.py        # Minimal BIOS-like fallback mode (system info, hard reset, forced panic test).
flash.py       # Cross-platform flashing script (mpremote), replaces flash.sh/flash.bat.
dodger.py      # Example CORA app — see "Adding your own app" above.
```

---

## 🩹 Changelog

**v1.0**
- Fixed: running the same app twice from CORA did nothing the second time (module caching) — apps now re-run correctly every time
- Fixed: battery percentage stayed visible on screen for a moment right before power-off / delete-data instead of a clean blank screen
- Fixed: the software clock could roll `13:59:59` into an invalid `13:60:00` instead of `14:00:00` after certain reboot timing
- Added: **Exit** option in CORA, so you can leave the launcher without running anything
- Reworked: Settings menu is now a single-item carousel (`< Change volume >`) instead of a 9-item scrolling list
- Replaced `flash.sh` + `flash.bat` with a single cross-platform `flash.py`, with a short interactive prompt (COM port, run after flashing)

---

## 📜 License

MIT License — see [LICENSE](LICENSE). Use it, modify it, build on it, just keep the copyright notice.

---

## 🙌 Credits

Made by [Cat0Ukraine](https://github.com/Cat0Ukraine) — a solo hobby project, still learning and improving it.

Contributions, forks, and your own CORA apps are welcome.