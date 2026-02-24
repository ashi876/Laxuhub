@echo off
cls
echo.
echo   ================================
echo       开发环境版本检查工具
echo   ================================
echo.

rem 设置脚本所在目录
set "SCRIPT_DIR=%~dp0"

rem 收集所有check_开头的py脚本
setlocal enabledelayedexpansion
set index=1
set count=0

echo   请选择要检查的语言环境：
echo.

for %%f in ("%SCRIPT_DIR%check_*.py") do (
    set "filename=%%~nxf"
    set "langname=!filename:check_=!"
    set "langname=!langname:.py=!"
    set "lang[!index!]=!langname!"
    set "script[!index!]=%%f"
    echo   [!index!] !langname! 版本检查
    set /a index+=1
    set /a count+=1
)

echo   [a] 全部检查
echo.
echo   [0] 退出
echo.

set /p choice=请输入选择 (0-%count%, a): 

if "%choice%"=="0" goto exit
if /i "%choice%"=="a" goto check_all

rem 检查是否为数字且在范围内
echo !choice!|findstr /r "^[1-9][0-9]*$" >nul
if errorlevel 1 (
    echo 无效选择，请输入数字或a
    pause
    exit
)

if !choice! gtr !count! (
    echo 无效选择，超出范围
    pause
    exit
)

rem 执行对应的脚本
echo.
echo 正在检查 !lang[%choice%]! 版本...
echo.
python "%SCRIPT_DIR%check_!lang[%choice%]!.py"
goto end

:check_all
echo.
echo 依次检查所有语言版本...
echo.

for /l %%i in (1,1,%count%) do (
    echo.
    echo === !lang[%%i]! ===
    python "%SCRIPT_DIR%check_!lang[%%i]!.py"
    echo.
)

:end
echo.
echo 检查完成，按任意键返回LaxuHub...
pause >nul
exit

:exit
echo 退出
exit