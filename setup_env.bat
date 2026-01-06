@echo off
echo Creating Python 3.10 Virtual Environment...
py -3.10 -m venv .venv_rembg

echo Installing dependencies in .venv_rembg...
call .venv_rembg\Scripts\activate.bat
pip install "rembg[cpu]" Pillow

echo Setup Complete!
pause
