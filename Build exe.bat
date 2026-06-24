@echo off
call venv\Scripts\activate

python -m nuitka app\Main.py ^
  --standalone ^
  --windows-console-mode=disable ^
  --enable-plugin=kivy ^
  --include-data-dir=app\Kv=Kv ^
  --include-data-dir=app\assets=assets ^
  --include-data-dir=config=config ^
  --output-dir=output ^
  --output-filename=FlashCard.exe

pause