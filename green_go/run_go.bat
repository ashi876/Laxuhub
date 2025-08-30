@echo off
setlocal enabledelayedexpansion

:: ��ȡ��ǰ�ű�·����Ŀ¼
set "self=%~f0"
set "dir=%~dp0"
set "count=0"

:: �г���ǰĿ¼����go��ͷ���ļ���
echo ��������goĿ¼...
for /d %%f in ("%dir%go*") do (
    set /a count+=1
    set "dir[!count!]=%%~ff"
    set "last_dir=%%~nxf"
)

:: ���û���ҵ������������ļ���
if %count% equ 0 (
    echo ����δ�ҵ�goĿ¼������Ӧ��go��ͷ��
    pause
    exit /b
)

:: ���ֻ��һ��goĿ¼���Զ�ѡ��
if %count% equ 1 (
    echo ��⵽Ψһ��goĿ¼: %last_dir%
    set "choice=1"
    goto setenv
)

:: ���Ŀ¼ʱ��ʾѡ��˵�
echo ���õ�goĿ¼�б�
for /l %%i in (1,1,%count%) do (
    for %%A in ("!dir[%%i]!") do (
        echo [%%i] %%~nxA
    )
)

:: �û�ѡ�񲿷�
:retry
echo.
set /p "choice=������Ҫʹ�õ�goĿ¼���(1-%count%)��"

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
set "GO_ROOT=!dir[%choice%]!"
set "GO_HOME=!GO_ROOT!\bin"
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
set "PATH=%GO_HOME%;%mybin%;%mybin_sub%;%PATH%"

:: ���þ���Դ���ýű���������ڣ�
if exist "%mybin%\cn_mirror.bat" (
    call "%mybin%\cn_mirror.bat"
) else (
    echo "cn_mirror.bat"�ļ������ڣ�ʹ��Ĭ��Դ
)

:: ����clink��ʷ������Ŀ¼
set "CLINK_PROFILE=%~dp0..\data\temp"
del /f /q %CLINK_PROFILE%\clink_errorlevel_*.txt 2>nul

:: ���go.exe�Ƿ����
if not exist "%GO_HOME%\go.exe" (
    echo ������ѡ����Ŀ¼��δ�ҵ�go��ִ���ļ� >&2
    echo ���·��: %GO_HOME%\go.exe
    pause
    exit /b 1
)
echo.

:: ��ʾ���óɹ��ľ���goĿ¼���ƣ���ʾ��Ŀ¼��������bin��
for %%A in ("%GO_ROOT%") do (
    echoc 15 �ѳɹ����� 10 [%%~nxA] 15 ����:
)
echo GO_ROOT=%GO_ROOT%
echo GO_HOME=%GO_HOME%
echo.

set mydesk="%USERPROFILE%\Desktop"

cd /d %mydesk%

go version

:: ����Clink
echo [����ģʽ] ����Clink...
cmd /k "clink.bat inject --quiet"

pause
exit /b