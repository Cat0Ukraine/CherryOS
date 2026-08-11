from machine import Pin
import time
import sys
import gc
from kernel import System
from CherryAPI import CherryAPI

kernel = System()
CherryAPI.init_api(kernel)

CherryAPI.text("CherryBoot", 0, 0, 1)
CherryAPI.show()
time.sleep(0.1)

CherryAPI.text("Connecting..", 0, 10, 1)
CherryAPI.show()
time.sleep(0.1)

for i in range(11):
    CherryAPI.led("toggle")
    time.sleep(0.03)

CherryAPI.led("on")

try:
    CherryAPI.text("Success!", 0, 20, 1)
    CherryAPI.show()
    time.sleep(0.1)
    if CherryAPI.pressed(2):
        CherryAPI.text("*Loading OS", 0, 30, 1)
        CherryAPI.show()
        time.sleep(0.1)
        __import__('CherryOS')
    else:
        CherryAPI.text("*COSS (BIOS)", 0, 30, 1)
        CherryAPI.show()
        time.sleep(0.1)
        __import__('COSS')

except Exception as e:
    print("\n[Boot] Critical error:", e)
    kernel.panic(str(e))