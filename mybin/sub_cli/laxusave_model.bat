@echo off
setlocal enabledelayedexpansion

##swap##
echo=

:: 使用 where 命令查找 laxusave.exe 的路径定位
where laxusave.exe >nul 2>&1

if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where laxusave.exe') do (
        set "sub_cli=%%~dpi"
        echo 已找到: !sub_cli!laxusave.exe定位目标
    )
) else (
    echo 未找到 laxusave.exe定位目标
    pause
    exit /b 1
)
echo=

set "mybin=%sub_cli%.."

call %mybin%\cn_mirror.bat
call %mybin%\vsenv.bat

cmd /k "!sub_cli!..\sub_clink\clink.bat inject --quiet"
