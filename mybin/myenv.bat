@echo off

REM ���� Python ���⻷����������ű�
setlocal enabledelayedexpansion

set "mybin=%~dp0"
set "clink=%mybin%clink\clink.bat inject --quiet"

REM ����Ĭ�ϻ�������
set "env_name=myenv"
if not "%1"=="" set "env_name=%1"

REM ������⻷��Ŀ¼�Ƿ��Ѵ���
if exist "%env_name%" (
    echo ����Ŀ¼ "%env_name%" �Ѵ���
    echo ��ѡ���������ƻ�ɾ������Ŀ¼
    pause
    exit /b 1
)

:: ����Python������������ʹ�õ��ýű���Python��
set "python_exe=python"
where !python_exe! >nul 2>nul || (
    echo ����δ�ҵ� Python ������
    echo ��ȷ�� Python �Ѱ�װ����ӵ� PATH
    pause
    exit /b 1
)

REM �������⻷��
echo ���ڴ������⻷��: %env_name%
%python_exe% -m venv "%env_name%"

if errorlevel 1 (
    echo ���󣺴������⻷��ʧ��
    pause
    exit /b 1
)

echo ���⻷�������ɹ���
echo �����������⻷���´���...
:: д��һ���������⻷�����ڵĽű�
set tmp_name=%env_name%

echo @echo off>%cd%\%env_name%.bat
echo set tmp_name=%env_name%>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo title %%tmp_name%% ���⻷��>>%cd%\%env_name%.bat
echo set path=%%path%%;%mybin%>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo cd /d %cd%\%%tmp_name%%>>%cd%\%env_name%.bat
echo call Scripts\activate>>%cd%\%env_name%.bat
echo call ����Դ.bat>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo echo ʹ��%%tmp_name%% ���⻷��>>%cd%\%env_name%.bat
echo python -V>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo cmd /k %clink%>>%cd%\%env_name%.bat

start %cd%\%env_name%.bat
