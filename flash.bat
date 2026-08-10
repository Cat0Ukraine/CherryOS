@echo off
chcp 65001 > nul

set "SRC_DIR=%USERPROFILE%\Projects\MicroPython\CherryOS"

echo =============================================
echo 🍒 CherryOS Auto-Flasher via mpremote 🍒
echo =============================================

mpremote connect list >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Raspberry Pi Pico not found!
    echo Check the USB connection and try again.
    exit /b 1
)

echo ⏳ Copying files to the board...
echo ---------------------------------------------

echo 📦 [1/4] Copying CherryOS.py...
mpremote cp "%SRC_DIR%\CherryOS.py" :CherryOS.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to copy CherryOS.py
    exit /b 1
) else (
    echo ✅ Done!
)

echo 📦 [2/4] Copying kernel.py...
mpremote cp "%SRC_DIR%\kernel.py" :kernel.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to copy kernel.py
    exit /b 1
) else (
    echo ✅ Done!
)

echo 📦 [3/4] Copying main.py...
mpremote cp "%SRC_DIR%\main.py" :main.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to copy main.py
    exit /b 1
) else (
    echo ✅ Done!
)

echo 📦 [4/4] Copying CherryAPI.py...
mpremote cp "%SRC_DIR%\CherryAPI.py" :CherryAPI.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to copy CherryAPI.py
    exit /b 1
) else (
    echo ✅ Done!
)

echo ---------------------------------------------
echo 🚀 All files uploaded successfully!
echo 🔄 Restarting Raspberry Pi Pico...

mpremote rtc --set + run "%SRC_DIR%\main.py"

echo ✨ Done! CherryOS is running.
echo =============================================
pause