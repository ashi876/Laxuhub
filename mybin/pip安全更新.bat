@echo off
setlocal enabledelayedexpansion

:: ================================
:: ǿ�����߸��� pip ���ռ�����
:: ================================

:: ��������
set PIP_URL=https://bootstrap.pypa.io/get-pip.py
set OUTPUT_FILE=new-get-pip.py
set PYTHON_EXE=python

:: ���Python�Ƿ����
where %PYTHON_EXE% >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] δ�ҵ�Python��ִ���ļ�
    echo ��ȷ��Python�Ѱ�װ�������ϵͳ·��
    exit /b 1
)

:: 1. ���curl�Ƿ����
echo [1/4] ������ع���...
where curl >nul 2>nul
if %errorlevel% equ 0 (
    echo  ʹ��curl���ذ�װ��...
    curl -L -k -o "%OUTPUT_FILE%" "%PIP_URL%"
    if exist "%OUTPUT_FILE%" (
        echo  �� ���سɹ���curl��
        goto install
    )
)

:: 2. �л���certutil����
echo [2/4] curl�����ã�����powershell...
powershell -Command "Invoke-WebRequest -Uri '%PIP_URL%' -OutFile '%OUTPUT_FILE%' -UseBasicParsing" >nul
if %errorlevel% equ 0 (
    if exist "%OUTPUT_FILE%" (
        echo  �� ���سɹ���PowerShell��
        goto install
    )
)

:: 3. ����ʧ�ܴ���
echo [3/4] ��������ʧ�ܣ�
echo ����ԭ��
echo   a) ���粻ͨ - ����ping bootstrap.pypa.io
echo   b) �������� - ��������������
echo   c) ��ȫ������� - ��ʱ���÷���ǽ
exit /b 1

:: 4. ִ�д�����װ
:install
echo [4/4] ִ�д������簲װ...
%PYTHON_EXE% "%OUTPUT_FILE%" --no-warn-script-location --no-cache-dir

:: ��֤��װ
echo.
echo ��֤��װ���...
%PYTHON_EXE% -m pip --version
if %errorlevel% equ 0 (
    echo ======================================
    echo �� PIP ��ͨ���������簲װ���!
    echo ======================================
) else (
    echo [!] ��װ��֤ʧ��
    echo �����ֶ���װ: python %OUTPUT_FILE%
)

:: �����ļ�
::del /q "%OUTPUT_FILE%" >nul 2>&1
exit /b