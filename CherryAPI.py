# ! This is API
# ! You can edit this, but other programs may crash

from kernel import System
import time
_kernel = None

class CherryAPI:
    @staticmethod
    def init_api(kernel_instance):
        global _kernel
        _kernel = kernel_instance
    @staticmethod
    def clear():
        if _kernel:
            _kernel._display.fill(0)
            _kernel._display.show()
    @staticmethod
    def text(string, x, y, c):
        if _kernel:
            _kernel._display.text(str(string), x, y, c)
    @staticmethod
    def line(x1, y1, x2, y2, c):
        if _kernel:
            _kernel._display.line(x1, y1, x2, y2, c)
    @staticmethod
    def rect(x1, y1, x2, y2, c):
        if _kernel:
            _kernel._display.rect(x1, y1, x2, y2, c)
    @staticmethod
    def fill_rect(x1, y1, x2, y2, c):
        if _kernel:
            _kernel._display.fill_rect(x1, y1, x2, y2, c)
    @staticmethod
    def pixel(x, y, c):
        if _kernel:
            _kernel._display.pixel(x, y, c)
    @staticmethod
    def make(framebuf, x, y):
        if _kernel:
            _kernel._display.blit(framebuf, x, y)
    @staticmethod
    def fill(value):
        if _kernel:
            _kernel._display.fill(value)
    @staticmethod
    def show(visible=True):
        if _kernel:
            if visible and _kernel.get_setting("show_battery", True):
                pct = _kernel.get_battery_percent()
                _kernel._display.fill_rect(101, 0, 27, 8, 0)
                _kernel._display.text(f"{pct}%", 101, 0, 1)
            _kernel._display.show()
    @staticmethod
    def beep(volume):
        if _kernel:
            _kernel.play_tone(500, 0.1, volume)
    @staticmethod
    def click(volume):
        if _kernel:
            _kernel.play_tone(1200, 0.02, volume)
            time.sleep(0.01)
            _kernel.play_tone(1500, 0.02, volume)
    @staticmethod        
    def sound(f, t, v):
        if _kernel:
            _kernel.play_tone(f, t, v)
    @staticmethod
    def pressed(button_num):
        if _kernel:
            return _kernel.button_pressed(button_num)
    @staticmethod
    def led(what):
        if _kernel:
            if what == "toggle":
                _kernel._led.toggle()
            elif what == "on":
                _kernel._led.value(1)
            elif what == "off":
                _kernel._led.value(0)
    @staticmethod
    def get_version():
        if _kernel:
            return _kernel.version
        return "Unknown"

    @staticmethod
    def get_uptime():
        if _kernel:
            return _kernel.get_uptime()
        return 0
    @staticmethod
    def temp():
        if _kernel:
            return _kernel.get_temp()
        return 0
    @staticmethod
    def get_time(v):
        if _kernel:
            return _kernel.get_time(v)
        return None
    @staticmethod
    def set_time(y, m, d, h, mi, s):
        if _kernel:
            _kernel.set_time(y, m, d, h, mi, s)
    @staticmethod
    def time_actual():
        if _kernel:
            return _kernel.get_time_actual()
        return False
    @staticmethod
    def button_name(role):
        if _kernel:
            return _kernel.get_button_name(role)
        return "?"
    @staticmethod
    def get_setting(key, default=None):
        if _kernel:
            return _kernel.get_setting(key, default)
        return default
    @staticmethod
    def set_setting(key, value):
        if _kernel:
            _kernel.set_setting(key, value)
    @staticmethod
    def shutdown_reason():
        if _kernel:
            return _kernel.get_shutdown_reason()
        return "Unknown"
    @staticmethod
    def disk_info():
        if _kernel:
            return _kernel.get_disk_info()
        return (0, 0)
    @staticmethod
    def voltage():
        if _kernel:
            return _kernel.get_voltage()
        return 0.0
    @staticmethod
    def cpu_freq():
        if _kernel:
            return _kernel.get_cpu_freq()
        return 0
    @staticmethod
    def battery_percent():
        if _kernel:
            return _kernel.get_battery_percent()
        return 0
    @staticmethod
    def battery_low():
        if _kernel:
            return _kernel.is_battery_low()
        return False
    @staticmethod
    def sleep():
        if _kernel:
            _kernel.enter_sleep()