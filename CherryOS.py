from CherryAPI import CherryAPI
import time
import framebuf
bar = 0
cherry_icon = bytearray([
    0x00, 0x00, 0x03, 0x00, 0x01, 0x80, 0x01, 0x40, 0x01, 0x20, 0x01, 0x10,
    0x02, 0x08, 0x04, 0x04, 0x18, 0x18, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c,
    0x3c, 0x3c, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00
])
cherry_fb = framebuf.FrameBuffer(cherry_icon, 16, 16, framebuf.MONO_HLSB)
def progress():
    global bar
    CherryAPI.fill(0)
    bar += 16
    if bar >= 32:
        CherryAPI.make(cherry_fb, 101, 10)
        CherryAPI.text("CherryOS", 60, 28, 1)
    if bar == 16:
        CherryAPI.text("Disp: OK;", 0, 0, 1)
    elif bar == 32:
        CherryAPI.text("Var: OK;", 0, 0, 1)
    elif bar == 48:
        CherryAPI.text("Games: OK;", 0, 0, 1)
    elif bar == 64:
        CherryAPI.text("Data: OK;", 0, 0, 1)
    elif bar == 80:
        CherryAPI.text("Audio: OK;", 0, 0, 1)
    elif bar == 96:
        CherryAPI.text("Utilits: OK;", 0, 0, 1)
    elif bar == 112:
        CherryAPI.text("S-ings: OK;", 0, 0, 1)
    elif bar == 128:
        CherryAPI.text("Load: OK;", 0, 0, 1)
    else:
        CherryAPI.text("Success!!!", 0, 0, 1)
    CherryAPI.fill_rect(0, 60, bar, 2, 1)
    CherryAPI.show()
    time.sleep(0.01)

progress()
from machine import Timer
import _thread
import sys
import os
import gc
import random
import json
volumesteps = [0, 16, 32, 48, 64, 86, 128, 192, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 50000]
step = CherryAPI.get_setting("volume_step", 8)
volume = volumesteps[step]
mode = 0
number = 0
mytime = [2021, 1, 1, 0, 0, 0]
streak = 0
best_score = 0

progress()

def popplay():
    global streak, best_score, volume
    i = 0
    x1 = 0
    x2 = 0
    allow = True
    facingright = True
    CherryAPI.fill(1)
    CherryAPI.text("Tap black when", 1, 1, 0)
    CherryAPI.text("line on rect", 1, 11, 0)
    CherryAPI.text(f"{CherryAPI.button_name("enter")} - continue", 1, 21, 0)
    CherryAPI.show()
    streak = 1
    while not CherryAPI.pressed(2):
        pass
    CherryAPI.click(volume)
    while CherryAPI.pressed(2):
        pass
    i = 0
    while allow:
        x1 = random.randint(15, 113)
        x2 = max(2, round(15 - (streak / 5)))
        while not CherryAPI.pressed(2):
            if facingright:
                i += 2.4
                if i >= 126:
                    facingright = False
            else:
                i -= 2.4
                if i <= 0:
                    facingright = True
            CherryAPI.fill(0)
            CherryAPI.text(f"{streak}; Best: {best_score}", 0, 0, 1)
            CherryAPI.fill_rect(round(i), 47, 1, 5, 1)
            CherryAPI.fill_rect(0, 55, 128, 8, 1)
            CherryAPI.fill_rect(x1, 56, x2, 6, 0)
            CherryAPI.show()
            time.sleep(0.004)
        while CherryAPI.pressed(2) == 0:
            pass
        if x1 < i and i < x1 + x2:
            streak += 1
            CherryAPI.sound(500, 0.1, volume)
            CherryAPI.sound(600, 0.1, volume)
        else:
            allow = False
            CherryAPI.fill(0)
            CherryAPI.text("You fail!", 0, 0, 1)
            for i in range(800, 200, -25):
                CherryAPI.sound(i, 0.05, volume)
            CherryAPI.text(f"Streak: {streak}", 0, 10, 1)
            CherryAPI.text(f"{CherryAPI.button_name("enter")} - exit", 0, 20, 1)
            CherryAPI.show()
            while not CherryAPI.pressed(2):
                pass
            while CherryAPI.pressed(2):
                pass
            if streak > best_score:
                best_score = streak

def play():
    global colors, volume
    possible_colors = ["Left", "Right"]
    CherryAPI.fill(0)
    CherryAPI.text("Simon says..", 0, 0, 1)
    CherryAPI.show()
    time.sleep(1)
    colors.append(random.choice(possible_colors))
    for count in range(len(colors)):
        CherryAPI.fill(0)
        CherryAPI.text(f"{colors[count]}    {count + 1}", 0, 0, 1)
        CherryAPI.rect(90, 52, 30, 10, 1)
        if colors[count] == "Left":
            CherryAPI.fill_rect(90, 52, 15, 10, 1)
        elif colors[count] == "Right":
            CherryAPI.fill_rect(105, 52, 15, 10, 1)
        CherryAPI.show()
        if colors[count] == "Left":
            CherryAPI.sound(1200, min(2, max(0.35, 7 / len(colors))), volume)
        elif colors[count] == "Right":
            CherryAPI.sound(1000, min(2, max(0.35, 7 / len(colors))), volume)
        time.sleep(0.05)
    CherryAPI.fill(1)
    CherryAPI.show()
    i_press_count = 0
    Pressing = True
    while Pressing:
        if CherryAPI.pressed(1) and i_press_count < len(colors):
            CherryAPI.click(volume)
            if colors[i_press_count] == "Right":
                i_press_count += 1
                while CherryAPI.pressed(1):
                    pass
            else:
                CherryAPI.fill(0)
                CherryAPI.text("You lose!", 0, 0, 1)
                CherryAPI.show()
                CherryAPI.sound(623, 0.75, volume)
                CherryAPI.sound(594, 0.75, volume)
                CherryAPI.sound(540, 0.75, volume)
                CherryAPI.sound(449, 1.25, volume)
                time.sleep(0.2)
                colors = []
                return None
        elif CherryAPI.pressed(3) and i_press_count < len(colors):
            CherryAPI.click(volume)
            if colors[i_press_count] == "Left":
                i_press_count += 1
                while CherryAPI.pressed(3):
                    pass
            else:
                CherryAPI.fill(0)
                CherryAPI.text("You lose!", 0, 0, 1)
                CherryAPI.show()
                CherryAPI.sound(623, 0.75, volume)
                CherryAPI.sound(594, 0.75, volume)
                CherryAPI.sound(540, 0.75, volume)
                CherryAPI.sound(449, 1.25, volume)
                time.sleep(0.2)
                colors = []
                return None
        if i_press_count == len(colors):
            CherryAPI.fill(0)
            CherryAPI.text("Next level!", 0, 0, 1)
            CherryAPI.show()
            for freq in range(400, 2000, 150):
                CherryAPI.sound(freq, 0.05, volume)
            time.sleep(0.2)
            Pressing = False
        time.sleep(0.1)

def dice_anim():
    global number, volume
    for i in range(6):
        if i == 0 or i == 3:
            number = "."
        elif i == 1 or i == 4:
            number = ".."
        elif i == 2:
            number = "..."
        else:
            number = random.randint(1, 6)
        CherryAPI.fill(0)
        CherryAPI.text("Dice!", 0, 0, 1)
        CherryAPI.text(f"{CherryAPI.button_name("enter")} - throw!", 0, 10, 1)
        CherryAPI.text(f"Number: {number}", 0, 20, 1)
        CherryAPI.show()
        if number == ".":
            CherryAPI.sound(400, 0.2, volume)
        elif number == "..":
            CherryAPI.sound(450, 0.2, volume)
        elif number == "...":
            CherryAPI.sound(500, 0.2, volume)
        else:
            time.sleep(0.1)
            CherryAPI.sound(int(number) * 150, 0.1, volume)
            time.sleep(0.1)
            CherryAPI.sound(int(number) * 125, 0.3, volume)
        time.sleep(0.1)
    time.sleep(0.1)

progress()
def saveinfouser(value):
    data = {"time": value}
    try:
        with open("save4.json", "w") as f:
            json.dump(data, f)
    except:
        pass

def loadinfouser():
    try:
        with open("save4.json", "r") as f:
            data = json.load(f)
            return data.get("time", 0)
    except:
        return True
def save_data_popit(value):
    data = {"best score": value}
    try:
        with open("save3.json", "w") as f:
            json.dump(data, f)
    except:
        pass

def load_data_popit():
    try:
        with open("save3.json", "r") as f:
            data = json.load(f)
            return data.get("best score", 0)
    except:
        return 0

def save_data(score):
    data = {"points": score}
    try:
        with open("save.json", "w") as f:
            json.dump(data, f)
    except:
        pass

def load_data():
    try:
        with open("save.json", "r") as f:
            data = json.load(f)
            return data.get("points", 0)
    except:
        return 0

def save_data_simon(col):
    data = {"colors": col}
    try:
        with open("save2.json", "w") as f:
            json.dump(data, f)
    except:
        pass

def load_data_simon():
    try:
        with open("save2.json", "r") as f:
            data = json.load(f)
            return data.get("colors", 0)
    except:
        return []

def save_data_user(password):
    CherryAPI.set_setting("password", password)

def load_data_user():
    return CherryAPI.get_setting("password", "0000")

progress()

def cherplayyer():
    audio = []
    Need = True
    i = 0
    while Need:
        i += 1
        try:
            with open(f"audio{i}.json", "r") as f:
                temp_data = json.load(f)
                audio.append(f"audio{i}.json")
        except:
            Need = False

    choice = 0
    CherryAPI.fill(0)
    CherryAPI.text(f"{CherryAPI.button_name("next")} - next", 0, 0, 1)
    CherryAPI.show()
    while True:
        if CherryAPI.pressed(1):
            CherryAPI.click(volume)
            if len(audio) == 0:
                CherryAPI.fill(0)
                CherryAPI.text("Nothing to play!", 0, 0, 1)
                CherryAPI.show()
                while CherryAPI.pressed(1):
                    pass
            else:
                choice += 1
                if choice > len(audio):
                    choice = 1
                with open(audio[choice - 1], "r") as f:
                    data = json.load(f)
                name = data.get("Name", f"Track {choice}")
                CherryAPI.fill(0)
                CherryAPI.text("Name:", 0, 0, 1)
                CherryAPI.text(name, 10, 9, 1)
                CherryAPI.show()
                while CherryAPI.pressed(1):
                    pass
        if CherryAPI.pressed(3):
            CherryAPI.click(volume)
            if len(audio) == 0:
                CherryAPI.fill(0)
                CherryAPI.text("Nothing to play!", 0, 0, 1)
                CherryAPI.show()
                while CherryAPI.pressed(3):
                    pass
            else:
                choice -= 1
                if choice < 1:
                    choice = len(audio)
                with open(audio[choice - 1], "r") as f:
                    data = json.load(f)
                name = data.get("Name", f"Track {choice}")
                CherryAPI.fill(0)
                CherryAPI.text("Name:", 0, 0, 1)
                CherryAPI.text(name, 10, 9, 1)
                CherryAPI.show()
                while CherryAPI.pressed(3):
                    pass
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            if len(audio) == 0 or choice == 0:
                return None
            CherryAPI.fill(0)
            CherryAPI.text("Playing...", 0, 0, 1)
            CherryAPI.show()
            for note in data.get("Notes", []):
                if CherryAPI.pressed(2):
                    while CherryAPI.pressed(2):
                        pass
                    return None
                if CherryAPI.pressed(1):
                    while CherryAPI.pressed(1):
                        pass
                freq = note.get("f", 0)
                dur = note.get("t", 0)
                if freq > 0:
                    CherryAPI.sound(freq, dur, volume)
                else:
                    time.sleep(dur)
            return None
progress()
def cora_list_files():
    excluded = ("main.py", "CherryOS.py", "CherryAPI.py", "kernel.py", "boot.py", "COSS.py")
    files = []
    for f in os.listdir():
        if f.endswith(".py") and f not in excluded:
            files.append(f)
    return files

def cora_scan_file(filename):
    threats = []
    try:
        with open(filename, "r") as f:
            content = f.read()
    except:
        return ["read_error"]
    if "import _kernel" in content:
        threats.append("import _kernel")
    if "os.remove" in content:
        threats.append("os.remove")
    if '"w")' in content or "'w')" in content or '"w",' in content or "'w'," in content:
        threats.append("file write")
    return threats

def cora_launch(filename):
    threats = cora_scan_file(filename)
    if threats == ["read_error"]:
        CherryAPI.fill(0)
        CherryAPI.text("Can't read file", 0, 0, 1)
        CherryAPI.text("Scan failed, app", 0, 12, 1)
        CherryAPI.text("blocked for safety", 0, 22, 1)
        CherryAPI.show()
        while not CherryAPI.pressed(2):
            pass
        while CherryAPI.pressed(2):
            pass
        return None
    if threats:
        choice = 0
        while True:
            CherryAPI.fill(0)
            CherryAPI.text("WARNING!", 0, 0, 1)
            CherryAPI.text(str(threats[0])[:16], 0, 10, 1)
            CherryAPI.text(("> " if choice == 0 else " ") + "Exit", 0, 30, 1)
            CherryAPI.text(("> " if choice == 1 else " ") + "Launch", 0, 42, 1)
            CherryAPI.show()
            if CherryAPI.pressed(1) or CherryAPI.pressed(3):
                CherryAPI.click(volume)
                choice = 1 - choice
                while CherryAPI.pressed(1) or CherryAPI.pressed(3):
                    pass
            elif CherryAPI.pressed(2):
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                if choice == 0:
                    return None
                break
        if not password_check(False):
            return None
    modname = filename[:-3] if filename.endswith(".py") else filename
    try:
        if modname in sys.modules:
            del sys.modules[modname]
        __import__(modname)
    except Exception as e:
        CherryAPI.fill(0)
        CherryAPI.text("App failed!", 0, 0, 1)
        err = str(e)
        for i in range(4):
            start = i * 16
            end = start + 16
            chunk = err[start:end]
            if not chunk:
                break
            CherryAPI.text(chunk, 0, (i * 9) + 12, 1)
        CherryAPI.show()
        while not CherryAPI.pressed(2):
            pass
        while CherryAPI.pressed(2):
            pass

def cora(): #CORA: Cherry Os Run App
    files = cora_list_files()
    items = ["Exit"] + files
    if not files:
        CherryAPI.fill(0)
        CherryAPI.text("CORA", 0, 0, 1)
        CherryAPI.text("No files found", 0, 20, 1)
        CherryAPI.show()
        time.sleep(1)
        return None
    choice = 0
    while True:
        CherryAPI.fill(0)
        CherryAPI.text("CORA - Run App", 0, 0, 1)
        CherryAPI.text(f"{choice + 1}/{len(items)}", 0, 54, 1)
        name = items[choice]
        if len(name) > 16:
            name = name[:13] + "..."
        CherryAPI.rect(0, 20, 128, 16, 1)
        CherryAPI.text(name, 4, 25, 1)
        CherryAPI.show()
        if CherryAPI.pressed(1):
            CherryAPI.click(volume)
            choice = (choice + 1) % len(items)
            while CherryAPI.pressed(1):
                pass
        elif CherryAPI.pressed(3):
            CherryAPI.click(volume)
            choice = (choice - 1) % len(items)
            while CherryAPI.pressed(3):
                pass
        elif CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            if choice == 0:
                return None
            cora_launch(items[choice])
            return None
        time.sleep(0.1)
def get_temp(offset=0):
    return CherryAPI.temp() + offset

def get_ram_info():
    info = f"{round(gc.mem_alloc() / 1024, 2)}/{int(gc.mem_free() / 1024) + int(gc.mem_alloc() / 1024)}"
    return info

def graphics_screenlock(changing):
    CherryAPI.fill_rect(0, 0, 128, 64, 1)
    CherryAPI.fill_rect(1, 1, 126, 62, 0)
    if changing:
        CherryAPI.text("New password:", 3, 3, 1)
    else:
        CherryAPI.text("user password:", 3, 3, 1)
    CherryAPI.rect(10, 24, 12, 12, 1)
    CherryAPI.rect(40, 24, 12, 12, 1)
    CherryAPI.rect(70, 24, 12, 12, 1)
    CherryAPI.rect(100, 24, 12, 12, 1)

def password_check(change):
    global passwordd, volume
    num = 0
    mynum = ""
    CherryAPI.fill(0)
    graphics_screenlock(change)
    CherryAPI.show()
    num = 0
    CherryAPI.fill(0)
    graphics_screenlock(change)
    CherryAPI.text(num, 12, 26, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(2):
        while CherryAPI.pressed(1):
            num += 1
            if num >= 10:
                num = 0
            CherryAPI.fill(0)
            graphics_screenlock(change)
            CherryAPI.text(num, 12, 26, 1)
            CherryAPI.show()
            CherryAPI.click(volume)
            while CherryAPI.pressed(1):
                pass
        time.sleep(0.05)
    CherryAPI.click(volume)
    while CherryAPI.pressed(2):
        pass
    mynum = f"{mynum}{num}"
    num = 0
    graphics_screenlock(change)
    CherryAPI.text("*", 12, 26, 1)
    CherryAPI.text(num, 42, 26, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(2):
        while CherryAPI.pressed(1):
            num += 1
            if num >= 10:
                num = 0
            CherryAPI.fill(0)
            graphics_screenlock(change)
            CherryAPI.text("*", 12, 26, 1)
            CherryAPI.text(num, 42, 26, 1)
            CherryAPI.show()
            CherryAPI.click(volume)
            while CherryAPI.pressed(1):
                pass
        time.sleep(0.05)
    CherryAPI.click(volume)
    while CherryAPI.pressed(2):
        pass
    mynum = f"{mynum}{num}"
    num = 0
    graphics_screenlock(change)
    CherryAPI.text("*", 12, 26, 1)
    CherryAPI.text("*", 42, 26, 1)
    CherryAPI.text(num, 72, 26, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(2):
        while CherryAPI.pressed(1):
            num += 1
            if num >= 10:
                num = 0
            CherryAPI.fill(0)
            graphics_screenlock(change)
            CherryAPI.text("*", 12, 26, 1)
            CherryAPI.text("*", 42, 26, 1)
            CherryAPI.text(str(num), 72, 26, 1)
            CherryAPI.show()
            CherryAPI.click(volume)
            while CherryAPI.pressed(1):
                pass
        time.sleep(0.05)
    CherryAPI.click(volume)
    while CherryAPI.pressed(2):
        pass
    mynum = f"{mynum}{num}"
    num = 0
    graphics_screenlock(change)
    CherryAPI.text("*", 12, 26, 1)
    CherryAPI.text("*", 42, 26, 1)
    CherryAPI.text("*", 72, 26, 1)
    CherryAPI.text(num, 102, 26, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(2):
        while CherryAPI.pressed(1):
            num += 1
            if num >= 10:
                num = 0
            CherryAPI.fill(0)
            graphics_screenlock(change)
            CherryAPI.text("*", 12, 26, 1)
            CherryAPI.text("*", 42, 26, 1)
            CherryAPI.text("*", 72, 26, 1)
            CherryAPI.text(num, 102, 26, 1)
            CherryAPI.show()
            CherryAPI.click(volume)
            while CherryAPI.pressed(1):
                pass
        time.sleep(0.05)
    CherryAPI.click(volume)
    while CherryAPI.pressed(2):
        pass
    mynum = f"{mynum}{num}"
    if change:
        return mynum
    if mynum == passwordd:
        return True
    else:
        CherryAPI.fill(0)
        CherryAPI.text("INCORRECT!", 3, 3, 1)
        CherryAPI.show()
        for i in range(10):
            CherryAPI.sound(1500, 0.1, volume)
            CherryAPI.sound(1000, 0.1, volume)
        time.sleep(2)
        return False
def tutorial():
    CherryAPI.fill(0)
    CherryAPI.text("Welcome to", 1, 1, 1)
    CherryAPI.text("CherryOS", 40, 11, 1)
    CherryAPI.text(f"Next is {CherryAPI.button_name('next')}", 0, 40, 1)
    CherryAPI.text("button", 0, 50, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(1):
        pass
    CherryAPI.click(volume)
    while CherryAPI.pressed(1):
        pass
    CherryAPI.fill(0)
    CherryAPI.text(f"Press {CherryAPI.button_name('enter')}", 0, 0, 1)
    CherryAPI.text("button, if you", 0, 10, 1)
    CherryAPI.text("know what to do", 0, 20, 1)
    CherryAPI.text(f"* Next is {CherryAPI.button_name('next')}", 0, 40, 1)
    CherryAPI.text("button", 0, 50, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(1) and not CherryAPI.pressed(2):
        pass
    CherryAPI.click(volume)
    if CherryAPI.pressed(1):
        while CherryAPI.pressed(1):
            pass
    else:
        saveinfouser(False)
        return None
    CherryAPI.fill(0)
    CherryAPI.text("CherryOS is", 0, 0, 1)
    CherryAPI.text("light gaming OS", 0, 10, 1)
    CherryAPI.text("with games))", 0, 20, 1)
    CherryAPI.text(f"* Next is {CherryAPI.button_name('next')}", 0, 30, 1)
    CherryAPI.text("btn everywhere", 0, 40, 1)
    CherryAPI.text("in OS", 0, 50, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(1):
        pass
    CherryAPI.click(volume)
    while CherryAPI.pressed(1):
        pass
    CherryAPI.fill(0)
    CherryAPI.text(f"{CherryAPI.button_name('enter')} button", 0, 0, 1)
    CherryAPI.text("is 'enter' or", 0, 10, 1)
    CherryAPI.text("confirm also", 0, 20, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(1):
        pass
    CherryAPI.click(volume)
    while CherryAPI.pressed(1):
        pass
    CherryAPI.fill(0)
    CherryAPI.text("CherryOS has", 0, 0, 1)
    CherryAPI.text("saving so", 0, 10, 1)
    CherryAPI.text("dont worry!", 0, 20, 1)
    CherryAPI.text("But poweroff", 0, 30, 1)
    CherryAPI.text("in settings)", 0, 40, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(1):
        pass
    CherryAPI.click(volume)
    while CherryAPI.pressed(1):
        pass
    CherryAPI.fill(0)
    CherryAPI.text("To launch app", 0, 0, 1)
    CherryAPI.text(f"find CORA in", 0, 10, 1)
    CherryAPI.text("list", 0, 20, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(1):
        pass
    CherryAPI.click(volume)
    while CherryAPI.pressed(1):
        pass
    CherryAPI.fill(0)
    CherryAPI.text("Password is", 0, 0, 1)
    CherryAPI.text("0000", 0, 10, 1)
    CherryAPI.text("and you can", 0, 20, 1)
    CherryAPI.text("change it in", 0, 30, 1)
    CherryAPI.text("settings", 0, 40, 1)
    CherryAPI.show()
    while not CherryAPI.pressed(1):
        pass
    CherryAPI.click(volume)
    while CherryAPI.pressed(1):
        pass
    saveinfouser(False)
progress()
def settings():
    global points, cherry_icon, cherry_fb, colors, best_score, volume, passwordd, step, audiomode

    items = ["Exit"]
    if not CherryAPI.time_actual():
        items.append("Set time")
    items += ["Change volume", "Sleep", "Delete data", "Power OFF", "Set password", "System info", "Show battery %"]

    choice = 0
    while True:
        CherryAPI.fill(0)
        CherryAPI.text("Settings", 0, 5, 1)
        label = items[choice]
        CherryAPI.text(f"< {label} >", 4, 28, 1)
        if label == "Show battery %":
            state = "ON" if CherryAPI.get_setting("show_battery", True) else "OFF"
            CherryAPI.text(f"(currently {state})", 4, 45, 1)
        CherryAPI.show()

        if CherryAPI.pressed(1):
            CherryAPI.click(volume)
            choice = (choice + 1) % len(items)
            while CherryAPI.pressed(1):
                pass
        elif CherryAPI.pressed(3):
            CherryAPI.click(volume)
            choice = (choice - 1) % len(items)
            while CherryAPI.pressed(3):
                pass
        elif CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            label = items[choice]

            if label == "Exit":
                return None

            elif label == "Show battery %":
                current = CherryAPI.get_setting("show_battery", True)
                CherryAPI.set_setting("show_battery", not current)
                return None

            elif label == "System info":
                used, total = CherryAPI.disk_info()
                CherryAPI.fill(0)
                CherryAPI.text("System info", 0, 0, 1)
                CherryAPI.text(f"Off: {CherryAPI.shutdown_reason()}"[:16], 0, 12, 1)
                CherryAPI.text(f"Up: {CherryAPI.get_uptime()}s", 0, 24, 1)
                CherryAPI.text(f"Disk:{used}/{total}KB", 0, 36, 1)
                CherryAPI.text(f"Ver: {CherryAPI.get_version()}", 0, 48, 1)
                CherryAPI.show()
                while not CherryAPI.pressed(2):
                    pass
                while CherryAPI.pressed(2):
                    pass
                return None

            elif label == "Set password":
                if password_check(False):
                    new = password_check(True)
                    save_data_user(new)
                    passwordd = new
                    return None
                else:
                    pass

            elif label == "Power OFF":
                save_data(points)
                save_data_simon(colors)
                save_data_popit(best_score)
                save_data_user(passwordd)
                CherryAPI.fill(0)
                CherryAPI.show(False)
                CherryAPI.led("off")
                time.sleep(0.1)
                return "poweroff"

            elif label == "Delete data":
                if password_check(False):
                    points = 0
                    colors = []
                    best_score = 0
                    passwordd = "0000"
                    save_data(points)
                    save_data_simon(colors)
                    save_data_popit(best_score)
                    save_data_user(passwordd)
                    saveinfouser(True)
                    CherryAPI.fill(0)
                    CherryAPI.show(False)
                    CherryAPI.led("off")
                    time.sleep(0.1)
                    while CherryAPI.pressed(2):
                        pass
                    return "poweroff"
                else:
                    pass

            elif label == "Sleep":
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.fill(0)
                CherryAPI.text("Sleeping...", 0, 0, 1)
                CherryAPI.show()
                time.sleep(1)
                CherryAPI.sleep()
                return None

            elif label == "Change volume":
                while CherryAPI.pressed(2):
                    pass
                while not CherryAPI.pressed(2):
                    CherryAPI.fill(0)
                    CherryAPI.text("Volume:", 0, 0, 1)
                    CherryAPI.rect(0, 35, 100, 10, 1)
                    CherryAPI.fill_rect(0, 35, round(step * 6.25), 10, 1)
                    CherryAPI.show()
                    if CherryAPI.pressed(1):
                        step = min(16, step + 1)
                        volume = volumesteps[step]
                        CherryAPI.click(volume)
                        time.sleep(0.1)
                    if CherryAPI.pressed(3):
                        step = max(0, step - 1)
                        volume = volumesteps[step]
                        CherryAPI.click(volume)
                        time.sleep(0.1)
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.set_setting("volume_step", step)
                return None

            elif label == "Set time":
                CherryAPI.fill(0)
                year = CherryAPI.get_time(0)
                month = CherryAPI.get_time(1)
                date = CherryAPI.get_time(2)
                hour = CherryAPI.get_time(3)
                minute = CherryAPI.get_time(4)
                seconds = CherryAPI.get_time(5)
                CherryAPI.text("Enter year", 0, 0, 1)
                CherryAPI.text(str(year), 0, 10, 1)
                CherryAPI.show()
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                while not CherryAPI.pressed(2):
                    while CherryAPI.pressed(1):
                        CherryAPI.click(volume)
                        year += 1
                        while CherryAPI.pressed(1):
                            pass
                    while CherryAPI.pressed(3):
                        CherryAPI.click(volume)
                        year -= 1
                        while CherryAPI.pressed(3):
                            pass
                    CherryAPI.fill(0)
                    CherryAPI.text("Enter year", 0, 0, 1)
                    CherryAPI.text(str(year), 0, 10, 1)
                    CherryAPI.show()
                    time.sleep(0.05)
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.fill(0)
                CherryAPI.text("Enter month", 0, 0, 1)
                CherryAPI.text(str(month), 0, 10, 1)
                CherryAPI.show()
                while not CherryAPI.pressed(2):
                    while CherryAPI.pressed(1):
                        CherryAPI.click(volume)
                        if month < 12:
                            month += 1
                        else:
                            month = 1
                        CherryAPI.fill(0)
                        CherryAPI.text("Enter month", 0, 0, 1)
                        CherryAPI.text(str(month), 0, 10, 1)
                        CherryAPI.show()
                        while CherryAPI.pressed(1):
                            pass
                    time.sleep(0.05)
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.fill(0)
                CherryAPI.text("Enter date", 0, 0, 1)
                CherryAPI.text(str(date), 0, 10, 1)
                CherryAPI.show()
                while not CherryAPI.pressed(2):
                    while CherryAPI.pressed(1):
                        CherryAPI.click(volume)
                        if date < 31:
                            date += 1
                        else:
                            date = 1
                        CherryAPI.fill(0)
                        CherryAPI.text("Enter date", 0, 0, 1)
                        CherryAPI.text(str(date), 0, 10, 1)
                        CherryAPI.show()
                        while CherryAPI.pressed(1):
                            pass
                    time.sleep(0.05)
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.fill(0)
                CherryAPI.text("Enter hour", 0, 0, 1)
                CherryAPI.text(str(hour), 0, 10, 1)
                CherryAPI.show()
                while not CherryAPI.pressed(2):
                    while CherryAPI.pressed(1):
                        CherryAPI.click(volume)
                        if hour < 23:
                            hour += 1
                        else:
                            hour = 0
                        CherryAPI.fill(0)
                        CherryAPI.text("Enter hour", 0, 0, 1)
                        CherryAPI.text(str(hour), 0, 10, 1)
                        CherryAPI.show()
                        while CherryAPI.pressed(1):
                            pass
                    time.sleep(0.05)
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.fill(0)
                CherryAPI.text("Enter minute", 0, 0, 1)
                CherryAPI.text(str(minute), 0, 10, 1)
                CherryAPI.show()
                while not CherryAPI.pressed(2):
                    while CherryAPI.pressed(1):
                        CherryAPI.click(volume)
                        if minute < 59:
                            minute += 1
                        else:
                            minute = 0
                        CherryAPI.fill(0)
                        CherryAPI.text("Enter minute", 0, 0, 1)
                        CherryAPI.text(str(minute), 0, 10, 1)
                        CherryAPI.show()
                        while CherryAPI.pressed(1):
                            pass
                    time.sleep(0.05)
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.fill(0)
                CherryAPI.text("Enter seconds", 0, 0, 1)
                CherryAPI.text(str(seconds), 0, 10, 1)
                CherryAPI.show()
                while not CherryAPI.pressed(2):
                    while CherryAPI.pressed(1):
                        CherryAPI.click(volume)
                        if seconds < 59:
                            seconds += 1
                        else:
                            seconds = 0
                        CherryAPI.fill(0)
                        CherryAPI.text("Enter seconds", 0, 0, 1)
                        CherryAPI.text(str(seconds), 0, 10, 1)
                        CherryAPI.show()
                        while CherryAPI.pressed(1):
                            pass
                    time.sleep(0.05)
                CherryAPI.click(volume)
                while CherryAPI.pressed(2):
                    pass
                CherryAPI.set_time(year, month, date, hour, minute, seconds)
        time.sleep(0.1)
progress()
CherryAPI.led("on")
colors = load_data_simon()
points = load_data()
best_score = load_data_popit()
passwordd = load_data_user()
progress()
progress()
CherryAPI.sound(700, 0.15, volume)
CherryAPI.sound(850, 0.15, volume)
CherryAPI.sound(700, 0.15, volume)
CherryAPI.sound(850, 0.15, volume)
CherryAPI.sound(900, 0.4, volume)
CherryAPI.sound(1000, 0.4, volume)
CherryAPI.sound(1100, 0.4, volume)
firsttime = loadinfouser()
if firsttime:
    tutorial()
while not password_check(False):
    pass
while True:
    gc.collect()
    if mode == 7:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            cora()
    elif mode == 6:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            cherplayyer()
    elif mode == 5:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            popplay()
    elif mode == 4:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            play()
    elif mode == 3:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            dice_anim()
    elif mode == 2:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            points += 1
            while CherryAPI.pressed(2):
                pass
    elif mode == 0:
        if CherryAPI.pressed(2):
            CherryAPI.click(volume)
            while CherryAPI.pressed(2):
                pass
            if settings() == "poweroff":
                break
            else:
                continue
    if CherryAPI.pressed(1):
        CherryAPI.click(volume)
        if mode < 7:
            mode += 1
        else:
            mode = 0
        while CherryAPI.pressed(1):
            pass
    if CherryAPI.pressed(3):
        CherryAPI.click(volume)
        if mode >= 1:
            mode -= 1
        else:
            mode = 7
        while CherryAPI.pressed(3):
            pass
    if mode == 7:
        CherryAPI.fill(0)
        CherryAPI.text("CORA", 0, 0, 1)
        CherryAPI.text(f"{CherryAPI.button_name("enter")} = run app", 0, 10, 1)
        CherryAPI.show()
        time.sleep(0.15)
    elif mode == 6:
        CherryAPI.fill(0)
        CherryAPI.text("CherPlayyer", 0, 0, 1)
        CherryAPI.text(f"{CherryAPI.button_name("enter")} = audio)", 0, 10, 1)
        CherryAPI.show()
        time.sleep(0.15)
    elif mode == 5:
        CherryAPI.fill(0)
        CherryAPI.text("PopIt", 0, 0, 1)
        CherryAPI.text(f"{CherryAPI.button_name("enter")} - start", 0, 10, 1)
        CherryAPI.show()
        time.sleep(0.09)
    elif mode == 4:
        CherryAPI.fill(0)
        CherryAPI.text("Simon!", 0, 0, 1)
        CherryAPI.text(f"{CherryAPI.button_name("enter")} - start", 0, 10, 1)
        if len(colors) < 10: 
            CherryAPI.text(f"({len(colors) + 1})", 100, 54, 1)
        elif 9 < len(colors) and len(colors) < 100:
            CherryAPI.text(f"({len(colors) + 1})", 90, 54, 1)
        else:
            CherryAPI.text(f"({len(colors) + 1})", 75, 54, 1)
        CherryAPI.show()
        time.sleep(0.07)
    elif mode == 3:
        CherryAPI.fill(0)
        CherryAPI.text("Dice!", 0, 0, 1)
        CherryAPI.text("Black - throw!", 0, 10, 1)
        CherryAPI.text(f"Number: {number}", 0, 20, 1)
        CherryAPI.show()
        time.sleep(0.12)
    elif mode == 2:
        CherryAPI.fill(0)
        CherryAPI.text("Clicker", 0, 0, 1)
        CherryAPI.text("Black - Tap", 0, 10, 1)
        CherryAPI.text(f"Score: {str(points)}", 0, 20, 1)
        CherryAPI.show()
        time.sleep(0.05)
    elif mode == 1:
        CherryAPI.fill(0)
        time_str = "{:02d}:{:02d}:{:02d}".format(CherryAPI.get_time(3), CherryAPI.get_time(4), CherryAPI.get_time(5))
        dd_mm_yy = "{:02d}.{:02d}.{:02d}".format(CherryAPI.get_time(2), CherryAPI.get_time(1), CherryAPI.get_time(0))
        CherryAPI.text(time_str, 32, 0, 1)
        CherryAPI.text(dd_mm_yy, 40, 54, 1)
        CherryAPI.show()
        time.sleep(0.15)
    elif mode == 0:
        CherryAPI.fill(0)
        time_str = "{:02d}:{:02d}:{:02d}".format(CherryAPI.get_time(3), CherryAPI.get_time(4), CherryAPI.get_time(5))
        CherryAPI.text(time_str, 32, 0, 1)
        CherryAPI.make(cherry_fb, 0, 25)
        CherryAPI.text("CherryOS", 18, 28, 1)
        CherryAPI.text(f"Temp: {int(get_temp(0))}", 1, 44, 1)
        CherryAPI.text(f"Ram: {get_ram_info()}", 1, 54, 1)
        CherryAPI.show(True)
        time.sleep(0.15)