@echo off
chcp 65001 >nul
echo ============================================
echo   图片切割 + 抠图 批处理工具
echo ============================================
echo.

REM 使用方式：
REM   直接双击  → 处理 outputs\Components 下的 png
REM   拖拽文件夹到此bat上 → 处理指定文件夹下的 png
REM   命令行: split_and_rembg.bat "D:\some\folder"

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%outputs\Components\batch_split_and_rembg.py"

if "%~1"=="" (
    set "TARGET_DIR=%SCRIPT_DIR%outputs\Components"
) else (
    set "TARGET_DIR=%~1"
)

echo 目标文件夹: %TARGET_DIR%
echo 脚本路径:   %PY_SCRIPT%
echo.

if not exist "%PY_SCRIPT%" (
    echo 错误：找不到 Python 脚本 %PY_SCRIPT%
    pause
    exit /b 1
)

if not exist "%TARGET_DIR%" (
    echo 错误：目标文件夹不存在 %TARGET_DIR%
    pause
    exit /b 1
)

python -u "%PY_SCRIPT%" "%TARGET_DIR%"

echo.
if %ERRORLEVEL% EQU 0 (
    echo ============================================
    echo   处理完成！
    echo   切割结果: %TARGET_DIR%\split
    echo   抠图结果: %TARGET_DIR%\rembg
    echo ============================================
) else (
    echo ============================================
    echo   处理失败，请检查错误信息
    echo ============================================
)

echo.
pause
