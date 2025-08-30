@echo off
:: �ر�ע�⣺���Բ���ʹ�� setlocal

set "VS_ENV_SCRIPT=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
echo vcvarsall=%VS_ENV_SCRIPT%

if not exist "%VS_ENV_SCRIPT%" (
    echo Error: vcvarsall.bat not found at:
    echo     "%VS_ENV_SCRIPT%"
    pause
    exit /b 1
)

:: �������Ƿ�Ϸ����ա�x64 �� x86��
if "%1"=="" (
    call "%VS_ENV_SCRIPT%" x64
) else if "%1"=="x64" (
    call "%VS_ENV_SCRIPT%" x64
) else if "%1"=="x86" (
    call "%VS_ENV_SCRIPT%" x86
) else (
    echo ������Ч���� "%1"��
    echo.
    echo ��ȷ�÷���
    echo    vsenv         ^<Ĭ�� x64^>
    echo    vsenv x64     ^<64 λ����^>
    echo    vsenv x86     ^<32 λ����^>
    pause
    exit /b 1
)