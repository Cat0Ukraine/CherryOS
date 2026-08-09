@echo off
chcp 65001 > nul

:: Шлях до твоїх файлів
set "SRC_DIR=%USERPROFILE%\Projects\MicroPython\CherryOS"

echo =============================================
echo 🍒 CherryOS Auto-Flasher via mpremote 🍒
echo =============================================

:: Перевіряємо, чи підключено Raspberry Pi Pico
mpremote connect list >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Помилка: Raspberry Pi Pico не знайдено!
    echo Перевірте підключення по USB та спробуйте ще раз.
    exit /b 1
)

echo ⏳ Починаю копіювання файлів на плату...
echo ---------------------------------------------

echo 📦 [1/4] Копіюю CherryOS.py...
mpremote cp "%SRC_DIR%\CherryOS.py" :CherryOS.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Помилка копіювання CherryOS.py
    exit /b 1
) else (
    echo ✅ Успішно!
)

echo 📦 [2/4] Копіюю kernel.py...
mpremote cp "%SRC_DIR%\kernel.py" :kernel.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Помилка копіювання kernel.py
    exit /b 1
) else (
    echo ✅ Успішно!
)

echo 📦 [3/4] Копіюю main.py...
mpremote cp "%SRC_DIR%\main.py" :main.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Помилка копіювання main.py
    exit /b 1
) else (
    echo ✅ Успішно!
)

echo 📦 [4/4] Копіюю CherryAPI.py...
mpremote cp "%SRC_DIR%\CherryAPI.py" :CherryAPI.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Помилка копіювання CherryAPI.py
    exit /b 1
) else (
    echo ✅ Успішно!
)

echo ---------------------------------------------
echo 🚀 Усі файли успішно завантажено!
echo 🔄 Перезавантажую Raspberry Pi Pico...

mpremote rtc --set + run "%SRC_DIR%\main.py"

echo ✨ Готово! CherryOS запущено.
echo =============================================
pause