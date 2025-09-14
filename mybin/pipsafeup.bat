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

:: 1. ���wget�Ƿ���ã�������
echo [1/5] ������ع���...
where wget >nul 2>nul
if %errorlevel% equ 0 (
    echo  ʹ��wget���ذ�װ��...
    wget --show-progress -O "%OUTPUT_FILE%" "%PIP_URL%"
    if %errorlevel% equ 0 (
        if exist "%OUTPUT_FILE%" (
            echo  �� ���سɹ���wget��
            goto install
        )
    )
)

:: 2. ���curl�Ƿ����
echo [2/5] wget�����ã�����curl...
where curl >nul 2>nul
if %errorlevel% equ 0 (
    echo  ʹ��curl���ذ�װ��...
    curl -L -k -o "%OUTPUT_FILE%" "%PIP_URL%" >nul 2>&1
    if exist "%OUTPUT_FILE%" (
        echo  �� ���سɹ���curl��
        goto install
    )
)

:: 3. �л���certutil����
echo [3/5] curl�����ã�����powershell...
powershell -Command "Invoke-WebRequest -Uri '%PIP_URL%' -OutFile '%OUTPUT_FILE%' -UseBasicParsing" >nul 2>&1
if %errorlevel% equ 0 (
    if exist "%OUTPUT_FILE%" (
        echo  �� ���سɹ���PowerShell��
        goto install
    )
)

:: 4. ����ʧ�ܴ���
echo [4/5] ��������ʧ�ܣ�
echo ����ԭ��
echo   a) ���粻ͨ - ����ping bootstrap.pypa.io
echo   b) �������� - ��������������
echo   c) ��ȫ������� - ��ʱ���÷���ǽ
exit /b 1

:: 5. ִ�д�����װ
:install
echo [5/5] ִ�д������簲װ...
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