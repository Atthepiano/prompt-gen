@echo off
echo Starting PromptGen Tool...
python app_qt.py 2> last_error.log
set RC=%ERRORLEVEL%
echo.
echo Application closed (exit code %RC%).
if not %RC%==0 (
    echo.
    echo =========================================
    echo  Error log written to: last_error.log
    echo =========================================
    echo.
    type last_error.log
    echo.
    pause
)
