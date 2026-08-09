# ! Important
# ! Pls do not edit this, if you dont know what you do!!!!
# ! It can damage your hardware 
# ! Follow instructions (sure if you don`t edit connecting)
# ! OLED (128x64 SSD1306): SDA - GPIO 0, SCL - GPIO 1
# ! Buttons - GPIO (2-4)
# ! Passive buzzer - GPIO 5
# ! Be careful when connecting >.<
# ** You can change GPIO there <3
gpsda = 0 # Don`t forget good I2C pin))
gpscl = 1 # Don`t forget good I2C pin))
gpbutton = 4 # Next (right)
gpbutton2 = 3 # Enter
gpbutton3 = 2 # Previos (left)
gpbuzzer = 5 # Buzzer

from micropython import const
import framebuf
import time
import machine
from machine import Pin, I2C, PWM, ADC, Timer
import _thread
import json
import os

CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "buttons": {"next": "red", "enter": "black", "prev": "red"},
    "volume_step": 8,
    "password": "0000",
    "last_time": [2021, 1, 1, 0, 0, 0],
    "total_uptime": 0,
    "show_battery": True,
    "last_shutdown_reason": None
}

# Battery voltage range: 3.0V = 0%, 4.2V (full Li-ion charge) = 100%.
# Anything above 4.2V (e.g. 5V straight from USB) is clamped to 100% via min().
BATTERY_MIN = 3.0
BATTERY_MAX = 4.2
LOW_BATTERY_WARN = 3.0
LOW_BATTERY_CUTOFF = 2.9

# MicroPython SSD1306 OLED driver, I2C and SPI interfaces
# register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,
            SET_MEM_ADDR,
            0x00,
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,
            SET_CONTRAST,
            0xFF,
            SET_ENTIRE_ON,
            SET_NORM_INV,
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        import time

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)

# * --- END SSD1306 ---
# Dynamic clock
_system = None
def timer(t):
    global _system
    _system.my_time[5] += 1
    if _system.my_time[5] > 59:
        _system.my_time[5] = 0
        _system.my_time[4] += 1
        if _system.my_time[4] != _system._last_save_minute:
            _system._last_save_minute = _system.my_time[4]
            _system.config["last_time"] = list(_system.my_time)
            _system.save_config()
        if _system.my_time[4] > 59:
            _system.my_time[4] = 0
            _system.my_time[3] += 1
            if _system.my_time[3] > 23:
                _system.my_time[3] = 0
                _system.my_time[2] += 1
                month = _system.my_time[1]
                year = _system.my_time[0]
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    max_days = 31
                elif month in [4, 6, 9, 11]:
                    max_days = 30
                elif month == 2:
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        max_days = 29
                    else:
                        max_days = 28
                if _system.my_time[2] > max_days:
                    _system.my_time[2] = 1
                    _system.my_time[1] += 1
                    if _system.my_time[1] > 12:
                        _system.my_time[1] = 1
                        _system.my_time[0] += 1
def battery_check(t):
    global _system
    if _system is None:
        return
    v = _system.get_voltage()
    if v <= 0.0:
        return 
    if v < LOW_BATTERY_CUTOFF:
        _system.force_shutdown_low_battery()

class System:
    def __init__(self):
        global _system
        _system = self
        self.version = "v1.0-beta"
        self._start_time = time.time()
        self._i2c = I2C(0, sda=Pin(gpsda), scl=Pin(gpscl), freq=400000)
        self._display = SSD1306_I2C(128, 64, self._i2c)
        self._led = Pin(25, Pin.OUT)
        self._btn_1 = Pin(gpbutton, Pin.IN, Pin.PULL_UP)
        self._btn_2 = Pin(gpbutton2, Pin.IN, Pin.PULL_UP)
        self._btn_3 = Pin(gpbutton3, Pin.IN, Pin.PULL_UP)
        self._buzzer = PWM(Pin(gpbuzzer))
        self._buzzer.duty_u16(0)
        self._temp_sensor = ADC(4)
        self._vsys = None
        try:
            self._vsys = ADC(29)
        except:
            self._vsys = None

        self.config = self.load_config()
        self._last_save_minute = -1

        self.check_time = time.localtime()
        if self.check_time[0] < 2025:
            self.time_actual = False
            self.timer_run = True
            self.my_time = list(self.config.get("last_time", [2021, 1, 1, 0, 0, 0]))
        else:
            self.time_actual = True
            self.timer_run = False
        if not self.time_actual:
            self.clock_timer = Timer(-1)
            self.clock_timer.init(period=1000, mode=Timer.PERIODIC, callback=timer)

        self.battery_timer = Timer(-1)
        self.battery_timer.init(period=5000, mode=Timer.PERIODIC, callback=battery_check)

    # --- Config (config.json) ---
    def load_config(self):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in data:
                    data[key] = value
            return data
        except:
            data = {}
            for key, value in DEFAULT_CONFIG.items():
                data[key] = value
            return data

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config, f)
        except:
            pass

    def get_setting(self, key, default=None):
        return self.config.get(key, default)

    def set_setting(self, key, value):
        self.config[key] = value
        self.save_config()

    def get_button_name(self, role):
        return self.config.get("buttons", DEFAULT_CONFIG["buttons"]).get(role, "?")

    def set_button_name(self, role, name):
        self.config.setdefault("buttons", {})[role] = name
        self.save_config()

    # --- Shutdown reason ---
    def get_shutdown_reason(self):
        override = self.config.get("last_shutdown_reason")
        if override:
            self.config["last_shutdown_reason"] = None
            self.save_config()
            return override
        try:
            cause = machine.reset_cause()
            reasons = {}
            for name, label in (
                ("PWRON_RESET", "Power on"),
                ("WDT_RESET", "Watchdog reset"),
                ("SOFT_RESET", "Soft reset (code)"),
                ("DEEPSLEEP_RESET", "Woke from sleep"),
            ):
                if hasattr(machine, name):
                    reasons[getattr(machine, name)] = label
            return reasons.get(cause, "Unknown/Hard reset")
        except:
            return "Unknown"

    # --- Extra hardware access ---
    def get_voltage(self):
        if not self._vsys:
            return 0.0
        try:
            reading = self._vsys.read_u16() * (3.3 / 65535) * 3
            return round(reading, 2)
        except:
            return 0.0

    def get_battery_percent(self):
        v = self.get_voltage()
        if v <= 0.0:
            return 0
        pct = (v - BATTERY_MIN) / (BATTERY_MAX - BATTERY_MIN) * 100
        return int(max(0, min(100, pct)))

    def is_battery_low(self):
        v = self.get_voltage()
        if v <= 0.0:
            return False
        return v < LOW_BATTERY_WARN

    def force_shutdown_low_battery(self):
        self.config["last_shutdown_reason"] = "Low battery"
        self.config["total_uptime"] = self.config.get("total_uptime", 0) + self.get_uptime()
        self.save_config()
        self._display.fill(0)
        self._display.text("LOW BATTERY!", 0, 20, 1)
        self._display.text("Shutting down", 0, 32, 1)
        self._display.show()
        self.play_tone(300, 0.3, 20000)
        self.play_tone(200, 0.5, 20000)
        self._led.value(0)
        time.sleep(1)
        self._display.fill(0)
        self._display.show()
        try:
            self._buzzer.duty_u16(0)
        except:
            pass
        try:
            machine.deepsleep()
        except:
            while True:
                time.sleep(1)

    def get_disk_info(self):
        try:
            s = os.statvfs("/")
            total = (s[0] * s[2]) / 1024
            free = (s[0] * s[3]) / 1024
            used = total - free
            return (round(used, 1), round(total, 1))
        except:
            return (0, 0)

    def set_cpu_freq(self, hz):
        try:
            machine.freq(hz)
        except:
            pass

    def get_cpu_freq(self):
        try:
            return machine.freq()
        except:
            return 0

    def soft_reset(self):
        self.save_config()
        machine.reset()

    def enter_sleep(self):
        self._display.poweroff()
        self._led.value(0)
        try:
            self._buzzer.duty_u16(0)
        except:
            pass

        woke = False
        def _wake(pin):
            nonlocal woke
            woke = True

        self._btn_2.irq(trigger=Pin.IRQ_FALLING, handler=_wake)
        try:
            while not woke:
                machine.lightsleep(1000)
        except:
            while self._btn_2.value():
                time.sleep(0.2)
        self._btn_2.irq(handler=None)

        while not self._btn_2.value():
            pass
        self._display.poweron()
        self._display.fill(0)
        self._display.show()
        self._led.value(1)

    def get_uptime(self):
        return int(time.time() - self._start_time)
    def play_tone(self, frequency, duration, volume):
        if volume == 0:
            pass
            time.sleep(duration)
            return
        try:
            self._buzzer.freq(frequency)
            self._buzzer.duty_u16(volume)
        except:
            pass
    
        time.sleep(duration)
        self._buzzer.duty_u16(0)
        time.sleep(0.01)
    def button_pressed(self, num):
        if num == 1:
            return not self._btn_1.value()
        elif num == 2:
            return not self._btn_2.value()
        elif num == 3:
            return not self._btn_3.value()
    
    def get_temp(self, offset=0):
        reading = self._temp_sensor.read_u16() * (3.3 / 65535)
        temperature = 27 - (reading - 0.706) / 0.001721
        return temperature + offset
    def get_time(self, v):
        if self.time_actual:
            a = time.localtime()
            return a[v]
        else:
            return self.my_time[v]
    def set_time(self, y, m, d, h, mi, s):
        self.my_time = [y, m, d, h, mi, s]
    def get_time_actual(self):
        return self.time_actual
    def panic(self, why):
        try:
            self.config["total_uptime"] = self.config.get("total_uptime", 0) + self.get_uptime()
            self.save_config()
        except:
            pass
        self._led.value(1)
        self.play_tone(2000, 0.1, 32000)
        self._led.value(0)
        self.play_tone(1000, 0.2, 32000)
        self._led.value(1)
        self.play_tone(2000, 0.1, 32000)
        self._led.value(0)
        self._display.fill(0)
        self._display.text("PANIC!!!", 0, 0, 1)
        self._display.show()
        time.sleep(0.05)
        self.play_tone(200, 1, 32000)
        for i in range(4):
            start = i * 14
            end = start + 14
            chunk = why[start:end]
            if not chunk:
                break
            self._display.text(chunk, 0, (i * 8) + 9, 1)
        self._display.text("Reboot & report", 0, 46, 1)
        self._display.text("for panic to me", 0, 54, 1)
        self._display.show()
