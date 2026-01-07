@echo off
echo Cleaning up previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo Building Background Worker (worker_rembg.exe) using Isolated Environment...
@REM Use the isolated venv to build the worker, ensuring dependencies are bundled correctly.
call .venv_rembg\Scripts\activate
pip install pyinstaller
pyinstaller --noconfirm --onefile --console --name "worker_rembg" "worker_rembg.py"
call .venv_rembg\Scripts\deactivate

echo.
echo Building Main Application (PromptGen_Tool.exe)...
@REM Use the system python (or base venv) for the main GUI
pyinstaller --noconfirm --onedir --windowed --name "PromptGen_Tool" --add-data "iconcsv;iconcsv" "app.py"

echo.
echo Merging Worker into Main App Distribution...
copy "dist\worker_rembg.exe" "dist\PromptGen_Tool\worker_rembg.exe"

echo.
echo Waiting for file handles to release...
timeout /t 5 /nobreak

echo Creating Deployment ZIP...
powershell Compress-Archive -Path "dist\PromptGen_Tool" -DestinationPath "PromptGen_Full_Release.zip" -Force

echo.
echo BUILD COMPLETE!
echo The release is ready at: PromptGen_Full_Release.zip (Unzip and Run, no setup needed)
pause
