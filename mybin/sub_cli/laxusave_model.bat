@echo off
setlocal enabledelayedexpansion

##swap##
echo=

:: ʹ�� where ������� laxusave.exe ��·����λ
where laxusave.exe >nul 2>&1

if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where laxusave.exe') do (
        set "sub_cli=%%~dpi"
        echo ���ҵ�: !sub_cli!laxusave.exe��λĿ��
    )
) else (
    echo δ�ҵ� laxusave.exe��λĿ��
    pause
    exit /b 1
)
echo=

set "mybin=%sub_cli%.."

call %mybin%\cn_mirror.bat
call %mybin%\vsenv.bat

cmd /k "!sub_cli!..\sub_clink\clink.bat inject --quiet"
