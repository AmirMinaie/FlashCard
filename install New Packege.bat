@echo off
set MIRROR=https://mirrors.aliyun.com/pypi/simple

echo ===============================
echo   Python Package Installer
echo ===============================

set /p PACKAGE_NAME=Enter package name: 

if "%PACKAGE_NAME%"=="" (
    echo Package name is empty!
    pause
    exit /b
)

call venv\Scripts\activate

pip install %PACKAGE_NAME% -i %MIRROR%

if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b
)

for /f "tokens=2 delims=: " %%v in ('pip show %PACKAGE_NAME% ^| findstr Version') do (
    set PACKAGE_VERSION=%%v
)

if exist requirements.txt (
    findstr /v /i "^%PACKAGE_NAME%==" requirements.txt > requirements_tmp.txt
    move /y requirements_tmp.txt requirements.txt >nul
)

echo %PACKAGE_NAME%==%PACKAGE_VERSION%>>requirements.txt

echo.
echo Installed: %PACKAGE_NAME%==%PACKAGE_VERSION%
echo requirements.txt updated successfully!
echo.

pause
