@echo off
setlocal enabledelayedexpansion

set /a count=0
echo.
echo ���õ� run ����:(run_XXX��ʽ����Ӳ�������)
echo.

for /f "delims=" %%p in ('lspath -l 3 -path') do (
    set "filename=%%~nxp"
    if /i "!filename:~0,3!"=="run" if /i "!filename:~-4!"==".bat" (
        if exist "%%p" (
            set /a count+=1
            for %%d in ("%%~dpp.") do set "dir_path=%%~fd"
            echo [!count!] !filename!   [·��: %%p]
            set "run!count!=%%p"
        )
    )
)

if !count! equ 0 (
    echo û���ҵ��κ� run*.bat ����
    pause
    exit /b
)

echo.
echo [0] �˳�
echo.
set /p choice="ѡ��Ҫ�����ķ�����: "

if "!choice!"=="0" (
    echo �˳�����
    exit /b
)

call "!run%choice%!"