# 🍒 CherryOS

A lightweight, gaming-focused operating system for the Raspberry Pi Pico, written from scratch in MicroPython — its own kernel, its own API layer, its own apps.

No Linux, no existing RTOS — just a 128x64 OLED, three buttons, a buzzer, and a custom OS built around them.

> ⚠️ **v1.0-beta** — functional and internally tested for logic, but not yet fully verified on real hardware. Expect rough edges.

---

## ✨ Features

- Animated boot screen with progress bar
- Password-protected lock screen (4-digit PIN)
- Built-in mini-games: Simon, PopIt (reaction), Dice, Clicker
- Custom JSON-based audio player (`CherryPlayer`)
- **CORA** (Cherry Os Run App) — a launcher that scans the flash for external `.py` files and lets you run them, with a built-in scanner that flags suspicious code (`import _kernel`, `os.remove`, file writes) and requires a password before running it
- **COSS** — a minimal BIOS-like mode: hard reset, system info, skip straight to CherryOS
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

Linux/macOS:
```bash
chmod +x flash.sh
SRC_DIR=$(pwd) ./flash.sh
```

Windows:
```
flash.bat
```

The script copies `CherryOS.py`, `kernel.py`, `main.py`, and `CherryAPI.py` onto the board and restarts it.

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

Any standalone `.py` file placed on the Pico's flash (that isn't `main.py`, `kernel.py`, `CherryAPI.py`, or `CherryOS.py`) will show up in the CORA launcher automatically. Your app only needs to import `CherryAPI`:

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

CORA runs a basic safety scan on any file before launching it — code containing `import _kernel`, `os.remove`, or file-write operations will trigger a password prompt before it's allowed to run.

**Never import `kernel` directly from an app** — always go through `CherryAPI`. That's the whole point of the API layer: it keeps the kernel safe from apps that misbehave.

---

## 📁 Project structure

```
kernel.py      # Low-level hardware access (display driver, buttons, buzzer, config, power). Don't edit unless you know what you're doing.
CherryAPI.py   # Safe API layer between the kernel and everything else.
main.py        # Bootloader — decides whether to load CherryOS or COSS.
CherryOS.py    # The OS itself: UI, games, settings, CORA.
COSS.py        # Minimal BIOS-like fallback mode.
flash.sh       # Linux/macOS flashing script (mpremote).
flash.bat      # Windows flashing script (mpremote).
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE). Use it, modify it, build on it, just keep the copyright notice.

---

## 🙌 Credits

Made by [Cat0Ukraine](https://github.com/Cat0Ukraine) — a solo hobby project, still learning and improving it.

Contributions, forks, and your own CORA apps are welcome.
