@echo off
setlocal enabledelayedexpansion

set /a count=0
echo.
echo 可用的 run 服务:(run_XXX格式名需加参数运行)
echo.

for /f "delims=" %%p in ('lspath -l 3 -path') do (
    set "filename=%%~nxp"
    if /i "!filename:~0,3!"=="run" if /i "!filename:~-4!"==".bat" (
        if exist "%%p" (
            set /a count+=1
            for %%d in ("%%~dpp.") do set "dir_path=%%~fd"
            echo [!count!] !filename!   [路径: %%p]
            set "run!count!=%%p"
        )
    )
)

if !count! equ 0 (
    echo 没有找到任何 run*.bat 服务
    pause
    exit /b
)

echo.
echo [0] 退出
echo.
set /p choice="选择要启动的服务编号: "

if "!choice!"=="0" (
    echo 退出程序
    exit /b
)

call "!run%choice%!"