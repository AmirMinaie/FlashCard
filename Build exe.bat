@echo off
setlocal

call venv\Scripts\activate

echo Cleaning previous build files...

if exist "output\dist" rmdir /s /q "output\dist"
if exist "output\build" rmdir /s /q "output\build"
if exist "output\FlashCard.spec" del /q "output\FlashCard.spec"

for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

echo Starting build...

set "PROJECT_DIR=%CD%"

pyinstaller "%PROJECT_DIR%\app\Main.py" ^
  --name DuckMemo ^
  --onefile ^
  --noconsole ^
  --icon="%PROJECT_DIR%\app\assets\images\icon.ico" ^
  --add-data "%PROJECT_DIR%\app\Kv;Kv" ^
  --add-data "%PROJECT_DIR%\app\assets;assets" ^
  --add-data "%PROJECT_DIR%\app\widgets;widgets" ^
  --hidden-import kivymd.icon_definitions ^
  --hidden-import kivymd.uix.slider ^
  --distpath "%PROJECT_DIR%\output\dist" ^
  --workpath "%PROJECT_DIR%\output\build" ^
  --specpath "%PROJECT_DIR%\output" ^
  --clean

echo.
echo Build finished.
pause