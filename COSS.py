# COSS - Cherry Os Simple Setup (BIOS-mode)

from CherryAPI import CherryAPI
import time
import machine

volume = 8192


def show_info():
    used, total = CherryAPI.disk_info()
    CherryAPI.fill(0)
    CherryAPI.text("COSS - Sys info", 0, 0, 1)
    CherryAPI.text(f"Ver: {CherryAPI.get_version()}", 0, 12, 1)
    CherryAPI.text(f"Off: {CherryAPI.shutdown_reason()}"[:16], 0, 22, 1)
    CherryAPI.text(f"Up: {CherryAPI.get_uptime()}s", 0, 32, 1)
    CherryAPI.text(f"Bat: {CherryAPI.battery_percent()}%", 0, 42, 1)
    CherryAPI.text(f"Disk:{used}/{total}KB", 0, 52, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(2):
        pass
    while CherryAPI.pressed(2):
        pass


def hard_reset():
    CherryAPI.fill(0)
    CherryAPI.text("Hard reset?", 0, 0, 1)
    CherryAPI.text(f"{CherryAPI.button_name('enter')} - confirm", 0, 12, 1)
    CherryAPI.text(f"{CherryAPI.button_name('prev')} - cancel", 0, 22, 1)
    CherryAPI.show()
    while True:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            CherryAPI.fill(0)
            CherryAPI.text("Resetting...", 0, 0, 1)
            CherryAPI.show()
            time.sleep(0.5)
            machine.reset()
        if CherryAPI.pressed(3):
            CherryAPI.click(volume)
            while CherryAPI.pressed(3):
                pass
            return None
        time.sleep(0.05)


def run():
    options = ["System info", "Hard reset", "Continue to CherryOS"]
    choice = 0
    while True:
        CherryAPI.fill(0)
        CherryAPI.text("COSS (BIOS)", 0, 0, 1)
        for i, opt in enumerate(options):
            prefix = "> " if i == choice else "  "
            CherryAPI.text(prefix + opt, 0, 16 + i * 12, 1)
        CherryAPI.show()

        if CherryAPI.pressed(1):
            CherryAPI.click(volume)
            choice = (choice + 1) % len(options)
            while CherryAPI.pressed(1):
                pass
        elif CherryAPI.pressed(3):
            CherryAPI.click(volume)
            choice = (choice - 1) % len(options)
            while CherryAPI.pressed(3):
                pass
        elif CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            if choice == 0:
                show_info()
            elif choice == 1:
                hard_reset()
            elif choice == 2:
                __import__('CherryOS')
                return None
        time.sleep(0.1)


run()