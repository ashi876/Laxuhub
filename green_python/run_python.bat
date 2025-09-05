@echo off
setlocal enabledelayedexpansion

:: ��ȡ��ǰ�ű�·����Ŀ¼
set "self=%~f0"
set "dir=%~dp0"
set "count=0"

:: �г���ǰĿ¼����python��ͷ���ļ���
echo ��������PythonĿ¼...
for /d %%f in ("%dir%python*") do (
    set /a count+=1
    set "dir[!count!]=%%~ff"
    set "last_dir=%%~nxf"
)

:: ���û���ҵ������������ļ���
if %count% equ 0 (
    echo ����δ�ҵ�PythonĿ¼������Ӧ��python��ͷ��
    pause
    exit /b
)

:: ���ֻ��һ��PythonĿ¼���Զ�ѡ��
if %count% equ 1 (
    echo ��⵽Ψһ��PythonĿ¼: %last_dir%
    set "choice=1"
    goto setenv
)

:: ���Ŀ¼ʱ��ʾѡ��˵�
echo ���õ�PythonĿ¼�б�
for /l %%i in (1,1,%count%) do (
    for %%A in ("!dir[%%i]!") do (
        echo [%%i] %%~nxA
    )
)

:: �û�ѡ�񲿷�
:retry
echo.
set /p "choice=������Ҫʹ�õ�PythonĿ¼���(1-%count%)��"

:: ��֤�����Ƿ�Ϊ��
if "%choice%"=="" (
    echo �������벻��Ϊ�գ�
    goto retry
)

:: ��֤�Ƿ�Ϊ������
set /a "test=choice" 2>nul
if errorlevel 1 (
    echo ����������������֣���������� "%choice%"
    goto retry
)

:: ��֤���ַ�Χ
if %choice% lss 1 (
    echo ���󣺱�Ų���С�� 1����������� "%choice%"
    goto retry
)
if %choice% gtr %count% (
    echo ���󣺱�Ų��ܴ��� %count%����������� "%choice%"
    goto retry
)
echo=

:: ���û�������
:setenv
set "PYTHON_HOME=!dir[%choice%]!"
set "mybin=%~dp0..\mybin"

:: �Զ����ֲ���� sub_ ��ͷ����Ŀ¼�� mybin_sub
set "mybin_sub="
for /d %%i in ("%mybin%\sub_*") do (
    if "!mybin_sub!"=="" (
        set "mybin_sub=%%i"
    ) else (
        set "mybin_sub=!mybin_sub!;%%i"
    )
)

:: ����PATH��������
set "PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%mybin%;%mybin_sub%;%PATH%"

:: ���þ���Դ���ýű���������ڣ�
if exist "%mybin%\pip_mirror.bat" (
    call "%mybin%\pip_mirror.bat"
) else (
    echo "pip_mirror.bat"�ļ������ڣ�ʹ��Ĭ��Դ
)


:: ����clink��ʷ������Ŀ¼
set "CLINK_PROFILE=%~dp0..\data\temp"
del /f /q %CLINK_PROFILE%\clink_errorlevel_*.txt 2>nul

:: ���python.exe�Ƿ����
if not exist "%PYTHON_HOME%\python.exe" (
    echo ������ѡ����Ŀ¼��δ�ҵ�Python��ִ���ļ� >&2
    pause
    exit /b 1
)
echo.

:: ��ʾ���óɹ��ľ���PythonĿ¼����
for %%A in ("%PYTHON_HOME%") do (
    echoc 15 �ѳɹ����� 10 [%%~nxA] 15 ����:
)
echo PYTHON_HOME=%PYTHON_HOME%
echo.

set mypy="%~dp0py"
set mydesk="%USERPROFILE%\Desktop"
echo ����cd /d %%mypy%% ����%mypy%Ŀ¼
echo ����cd /d %%mydesk%% ����%mydesk%Ŀ¼
cd /d %mydesk%

pip -V
if !errorlevel! equ 1 (
    echoc 12 ��⵽pip�������,����[pipreset.bat]��[pipsafeup.bat]
)

:: ����Clink
echo [����ģʽ] ����Clink...
cmd /k "clink.bat inject --quiet"

pause
exit /b