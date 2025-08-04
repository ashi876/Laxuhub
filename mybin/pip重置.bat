@echo off
setlocal enabledelayedexpansion

:: ================================================
:: ��ɫ��PythonǨ���޸�����
:: ���ܣ���ʼ��pip + ·���̻�(������ͬ�汾)
:: ���ã���ɫ��PythonĿ¼�ƶ���ʹ��
:: ================================================

echo.
echo [1/3] ���ڶ�λPython������...
echo.

:: ����Python������
set "PYTHON_EXE="
for /f "tokens=*" %%a in ('where python 2^>nul') do (
    set "PYTHON_EXE=%%a"
    set "PYTHON_DIR=%%~dpa"
    goto :python_found
)

:python_not_found
echo ����: δ�ҵ�Python������
echo ��ȷ��:
echo   1. Python�Ѽ���PATH��������
echo   2. ���ڴ�Ŀ¼����: %~dp0
exit /b 1

:python_found
echo ʹ��Python: %PYTHON_EXE%
echo ��װĿ¼: %PYTHON_DIR%
echo.

:: ================================================
:: �����޸�����
:: ================================================

:: ����1: ��ʼ�������ð汾
echo [2/3] ��ʼ��pip�����ð汾...
echo ִ��: %PYTHON_EXE% -m ensurepip --upgrade --default-pip
"%PYTHON_EXE%" -m ensurepip --upgrade --default-pip
if errorlevel 1 (
    echo ����: pip��ʼ��ʧ��
    echo ����ԭ��: 
    echo   - ������������
    echo   - Python������
    echo   - Ȩ�޲���
    exit /b 1
)
echo ��ʼ���ɹ�!
echo.

:: ����2: ��ȡ��ǰ�汾
echo ��ȡ��ǰpip�汾...
set "CURRENT_PIP_VERSION="
for /f "tokens=1,2 delims= " %%a in ('"%PYTHON_EXE%" -m pip --version 2^>nul') do (
    if "%%a"=="pip" set "CURRENT_PIP_VERSION=%%b"
)

if not defined CURRENT_PIP_VERSION (
    echo ����: �޷���ȡpip�汾��
    echo �����ֶ�����: %PYTHON_EXE% -m pip --version
    exit /b 1
)
echo ��ǰpip�汾: !CURRENT_PIP_VERSION!
echo.

:: ����3: ��ͬ�汾��װ(·���̻�)
echo [3/3] ·���̻�(��װ��ͬ�汾:!CURRENT_PIP_VERSION!)...
echo ִ��: %PYTHON_EXE% -m pip install --force-reinstall --no-cache-dir "pip==!CURRENT_PIP_VERSION!"
"%PYTHON_EXE%" -m pip install --force-reinstall --no-cache-dir "pip==!CURRENT_PIP_VERSION!"
if errorlevel 1 (
    echo ����: ·���̻�ʧ��
    echo ���鳢��:
    echo   1. �����������
    echo   2. ��ʱ�رշ���ǽ/ɱ�����
    echo   3. �ֶ�����: %PYTHON_EXE% -m pip install --force-reinstall pip
    exit /b 1
)
echo ·���̻��ɹ�!
echo.

:: ================================================
:: ���ù��ھ���Դ��ԭ�����ã�
:: ================================================

REM set "PIP_CONFIG=%APPDATA%\pip\pip.ini"
REM if not exist "%APPDATA%\pip\" mkdir "%APPDATA%\pip"

REM set "TEMP_CONFIG=%TEMP%\pip_temp_%RANDOM%.ini"
REM (
    REM echo [global]
    REM echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
    REM echo extra-index-url = https://mirrors.aliyun.com/pypi/simple/ https://pypi.mirrors.ustc.edu.cn/simple/
    REM echo trusted-host = pypi.tuna.tsinghua.edu.cn mirrors.aliyun.com pypi.mirrors.ustc.edu.cn
    REM echo timeout = 120
REM ) > "%TEMP_CONFIG%"

REM move /Y "%TEMP_CONFIG%" "%PIP_CONFIG%" > nul
REM echo ����Դ�����ļ�λ��: %PIP_CONFIG%
REM echo ����:
REM type "%PIP_CONFIG%"
REM echo.

:: ================================================
:: ��֤���
:: ================================================

echo ������֤:
echo Python·��: %PYTHON_DIR%
"%PYTHON_EXE%" --version
"%PYTHON_EXE%" -m pip --version
echo.

echo ��ʾpip����:
"%PYTHON_EXE%" -m pip config list
echo.

:: ================================================
:: �����ʾ
:: ================================================

echo [�ɹ�] %PYTHON_DIR% �����޸����!
echo �����ܽ�:
echo   1. ��ʼ��pip�����ð汾
echo   2. ·���̻�(���ְ汾 !CURRENT_PIP_VERSION!)
echo.
echo ��ʾ: �ƶ�PythonĿ¼����Ҫ�������д˽ű�
echo.
endlocal