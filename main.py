from machine import Pin, I2C
import time
import sys
import gc
from kernel import System
from CherryAPI import CherryAPI
kernel = System()
CherryAPI.init_api(kernel)
led = Pin(25, Pin.OUT)
button2 = Pin(3, Pin.IN, Pin.PULL_UP)
kernel._display.text("CherryBoot", 0, 0, 1)
kernel._display.show()
time.sleep(0.1)
kernel._display.text("Connecting..", 0, 10, 1)
kernel._display.show()
time.sleep(0.1)
for i in range(11):
    led.toggle()
    time.sleep(0.03)
led.value(1)
try:
    kernel._display.text("Success!", 0, 20, 1)
    kernel._display.show()
    time.sleep(0.1)
    if button2.value() == 1:
        kernel._display.text("*Loading OS", 0, 30, 1)
        kernel._display.show()
        time.sleep(0.1)
        __import__('CherryOS')
    else:
        kernel._display.text("*COSS (BIOS)", 0, 30, 1)
        kernel._display.show()
        time.sleep(0.1)
        __import__('COSS')
    #kernel._display.fill(0)
    #kernel._display.text("Turn off energy", 0, 56, 1)
    #kernel._display.show()
except Exception as e:
    print("\n[Boot] Critical error:", e)
    kernel.panic(str(e))