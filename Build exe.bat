@echo off
setlocal

call venv\Scripts\activate

echo Cleaning previous build files...

if exist "output\dist" rmdir /s /q "output\dist"
if exist "output\build" rmdir /s /q "output\build"
if exist "output\FlashCard.spec" del /q "output\FlashCard.spec"

for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

echo Starting build...

pyinstaller app\Main.py ^
  --name FlashCard ^
  --onefile ^
  --noconsole ^
  --add-data "%CD%\app\Kv;Kv" ^
  --add-data "%CD%\app\assets;assets" ^
  --add-data "%CD%\app\widgets;widgets" ^
  --hidden-import kivymd.icon_definitions ^
  --hidden-import kivymd.uix.slider ^
  --distpath output\dist ^
  --workpath output\build ^
  --specpath output ^
  --clean

echo.
echo Build finished.
pause