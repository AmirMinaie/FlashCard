
set MIRROR=https://mirrors.aliyun.com/pypi/simple

py -3.10 -m venv venv

call venv\Scripts\activate

python -m pip install --upgrade pip -i %MIRROR% --trusted-host mirrors.aliyun.com

pip install -r requirements.txt --only-binary=:all: -i %MIRROR%
pause
