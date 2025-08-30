@echo off
setlocal enabledelayedexpansion

:: ��ȡ��ǰ�ű�·����Ŀ¼
set "self=%~f0"
set "dir=%~dp0"
set "count=0"

:: �г���ǰĿ¼����nodejs��ͷ���ļ���
echo ��������Node.jsĿ¼...
for /d %%f in ("%dir%node*") do (
    set /a count+=1
    set "dir[!count!]=%%~ff"
    set "last_dir=%%~nxf"
)

:: ���û���ҵ������������ļ���
if %count% equ 0 (
    echo ����δ�ҵ�Node.jsĿ¼������Ӧ��node��ͷ��
    pause
    exit /b
)

:: ���ֻ��һ��Node.jsĿ¼���Զ�ѡ��
if %count% equ 1 (
    echo ��⵽Ψһ��Node.jsĿ¼: %last_dir%
    set "choice=1"
    goto setenv
)

:: ���Ŀ¼ʱ��ʾѡ��˵�
echo ���õ�Node.jsĿ¼�б�
for /l %%i in (1,1,%count%) do (
    for %%A in ("!dir[%%i]!") do (
        echo [%%i] %%~nxA
    )
)

:: �û�ѡ�񲿷�
:retry
echo.
set /p "choice=������Ҫʹ�õ�Node.jsĿ¼���(1-%count%)��"

:: ��֤����
if "%choice%"=="" (
    echo �������벻��Ϊ�գ�
    goto retry
)
set /a "test=choice" 2>nul
if errorlevel 1 (
    echo ����������������֣���������� "%choice%"
    goto retry
)
if %choice% lss 1 (
    echo ���󣺱�Ų���С�� 1
    goto retry
)
if %choice% gtr %count% (
    echo ���󣺱�Ų��ܴ��� %count%
    goto retry
)
echo=

:: ���û�������
:setenv
set "JC_HOME=!dir[%choice%]!"
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

:: ����PATH
set "PATH=%JC_HOME%;%mybin%;%mybin_sub%;%PATH%"

:: ����npm����Դ���ýű�
if exist "%mybin%\npm_mirror.bat" (
    call "%mybin%\npm_mirror.bat"
) else (
    echo "npm_mirror.bat"�ļ������ڣ�ʹ��Ĭ��Դ
)

:: ����clink��ʷ������Ŀ¼
set "CLINK_PROFILE=%~dp0..\data\temp"
del /f /q %CLINK_PROFILE%\clink_errorlevel_*.txt 2>nul

:: ���node.exe�Ƿ����
if not exist "%JC_HOME%\node.exe" (
    echo ������ѡ����Ŀ¼��δ�ҵ�Node.js��ִ���ļ� >&2
    pause
    exit /b 1
)

:: ��ʾ���ý��
echo.
for %%A in ("%JC_HOME%") do (
    echoc 15 �ѳɹ����� 10 [%%~nxA] 15 ������
)
echo JC_HOME=%JC_HOME%
echo.

:: ���ó���Ŀ¼����
set jcprojects="%~dp0jsprojects"
set mydesk="%USERPROFILE%\Desktop"
echo ���� cd /d %%jcprojects%% ����%jcprojects%Ŀ¼
echo ���� cd /d %%mydesk%% ����%mydesk%Ŀ¼
cd /d %mydesk%

:: ��֤npm
call "%JC_HOME%\nodevars.bat"

:: ����Clink
echo [����ģʽ] ����Clink...
cmd /k "clink.bat inject --quiet"

pause
exit /b