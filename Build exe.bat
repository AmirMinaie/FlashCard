call venv\Scripts\activate

pyinstaller app\Main.py ^
  --onefile ^
  --noconsole ^
  --add-data "..\app\Kv;kv" ^
  --distpath output\dist ^
  --workpath output\build ^
  --specpath output

pause
