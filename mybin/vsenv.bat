@echo off
:: 特别注意：绝对不能使用 setlocal

set "VS_ENV_SCRIPT=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
echo vcvarsall=%VS_ENV_SCRIPT%

if not exist "%VS_ENV_SCRIPT%" (
    echo Error: vcvarsall.bat not found at:
    echo     "%VS_ENV_SCRIPT%"
    pause
    exit /b 1
)

:: 检查参数是否合法（空、x64 或 x86）
if "%1"=="" (
    call "%VS_ENV_SCRIPT%" x64
) else if "%1"=="x64" (
    call "%VS_ENV_SCRIPT%" x64
) else if "%1"=="x86" (
    call "%VS_ENV_SCRIPT%" x86
) else (
    echo 错误：无效参数 "%1"！
    echo.
    echo 正确用法：
    echo    vsenv         ^<默认 x64^>
    echo    vsenv x64     ^<64 位环境^>
    echo    vsenv x86     ^<32 位环境^>
    pause
    exit /b 1
)