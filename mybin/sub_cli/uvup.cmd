@echo off
setlocal enabledelayedexpansion

title UV �汾������

echo ================================
echo        UV �汾������
echo ================================

:: ��鵱ǰ�汾
if exist "%~dp0uv.exe" (
    echo ��ǰ UV �汾��Ϣ:
    for /f "tokens=*" %%i in ('"%~dp0uv.exe" --version 2^>^&1') do (
        set "current_version=%%i"
        echo %%i
    )
    echo.
) else (
    echo δ�ҵ� uv.exe����ʼ����...
    echo.
)

:: ��ȡ���°汾��
echo ���ڻ�ȡ���°汾��Ϣ...
for /f "tokens=*" %%i in ('powershell -Command "(Invoke-RestMethod -Uri 'https://api.github.com/repos/astral-sh/uv/releases/latest').tag_name"') do (
    set "latest_version=%%i"
)

if "!current_version!"=="" (
    echo ���°汾: !latest_version!
) else (
    for /f "tokens=2" %%v in ("!current_version!") do set "current_ver=%%v"
    if "!current_ver!"=="!latest_version!" (
        echo ��ǰ�������°汾: !latest_version!
        echo ������¡�
        pause
        exit /b 0
    ) else (
        echo ��ǰ�汾: !current_ver!
        echo ���°汾: !latest_version!
        echo.
        set /p confirm="�Ƿ���µ����°汾��(y/n): "
        if /i not "!confirm!"=="y" (
            echo ������ȡ����
            pause
            exit /b 0
        )
    )
)

echo.
echo �������ز���װ���°� UV...

set "download_url=https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
set "zip_file=uv-latest.zip"
set "backup_file=uv-backup.exe"

:: ���ݾɰ汾
if exist "%~dp0uv.exe" (
    echo ���ݾɰ汾...
    copy "%~dp0uv.exe" "!backup_file!" >nul
)

echo ����1: ���� UV...
powershell -Command "Invoke-WebRequest -Uri '%download_url%' -OutFile '%zip_file%'"

if not exist "%zip_file%" (
    echo ����ʧ�ܣ�
    if exist "!backup_file!" (
        echo �ָ�����...
        move "!backup_file!" "%~dp0uv.exe" >nul
    )
    pause
    exit /b 1
)

echo ����2: ��ѹ�ļ�...
powershell -Command "Expand-Archive -Path '%zip_file%' -DestinationPath '%~dp0' -Force"

echo ����3: ������ʱ�ļ�...
if exist "%zip_file%" del "%zip_file%"
if exist "!backup_file!" del "!backup_file!"

if exist "%~dp0uv.exe" (
    echo.
    echo ��װ�ɹ���
    echo ���º� UV �汾��Ϣ:
    "%~dp0uv.exe" --version
    echo.
    echo ʹ��˵����
    echo - ֱ������ uv �����
    echo - �������û�������
    echo - ��ɫ��Я����Ŀ¼Я��
) else (
    echo ���󣺽�ѹ��δ�ҵ� uv.exe
    if exist "!backup_file!" (
        echo �ָ�����...
        move "!backup_file!" "%~dp0uv.exe" >nul
    )
)

echo.
pause