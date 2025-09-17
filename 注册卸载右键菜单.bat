@echo off
setlocal enabledelayedexpansion

:: �������� - ֻ���޸�����ı�������������������
set "APP_EXE=LaxuHub.exe"
set "APP_NAME=LaxuHub"
set "MENU_TEXT=ʹ�� %APP_NAME% ��"
set "APP_PARAMS=-q"
:: �����������

:: ����Ƿ��Թ���Ա�������
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ���Թ���Ա������д˽ű�
    pause
    exit /b 1
)

:MAIN_MENU
cls
echo ==============================
echo     %APP_NAME% �Ҽ��˵�����
echo ==============================
echo.
echo ��ѡ�������
echo 1. ע���Ҽ��˵�
echo 2. ж���Ҽ��˵�
echo 3. �˳�
echo.
set /p choice="������ѡ�� (1-3): "

if "%choice%"=="1" goto REGISTER
if "%choice%"=="2" goto UNINSTALL
if "%choice%"=="3" exit /b 0

echo ��Чѡ�����������
pause
goto MAIN_MENU

:REGISTER
cd /d %~dp0
:: �Զ���⵱ǰĿ¼�µĳ���
set "APP_PATH=%~dp0%APP_EXE%"

:: �������Ƿ����
if not exist "%APP_PATH%" (
    echo �����ڵ�ǰĿ¼δ�ҵ� %APP_EXE%
    echo ��ǰĿ¼��%CD%
    echo ��ȷ������������ %APP_EXE% ��ͬһĿ¼��
    pause
    goto MAIN_MENU
)

echo �ҵ� %APP_EXE%��%APP_PATH%
echo.

:: ���·�����пո���ʹ�ö�·����ʽ
set "SHORT_PATH=%APP_PATH: =" "%"
for %%I in ("%SHORT_PATH%") do set "SHORT_PATH=%%~sI"

:: ���������в���
if defined APP_PARAMS (
    set "CMD_LINE=\"%APP_PATH%\" %APP_PARAMS% \"%%1\""
    set "BG_CMD_LINE=\"%APP_PATH%\" %APP_PARAMS% \"%%V\""
) else (
    set "CMD_LINE=\"%APP_PATH%\" \"%%1\""
    set "BG_CMD_LINE=\"%APP_PATH%\" \"%%V\""
)

:: ע������
echo ��������Ҽ��˵�...

:: 1. Ϊ�ļ����ļ�����������Ĳ˵�
reg add "HKCR\*\shell\%APP_NAME%" /ve /d "%MENU_TEXT%" /f
reg add "HKCR\*\shell\%APP_NAME%" /v "Icon" /d "\"%SHORT_PATH%\"" /f

:: 2. Ϊ�ļ��б������հ״�����������Ĳ˵�
reg add "HKCR\Directory\Background\shell\%APP_NAME%" /ve /d "�ڴ˴����� %APP_NAME%" /f
reg add "HKCR\Directory\Background\shell\%APP_NAME%" /v "Icon" /d "\"%SHORT_PATH%\"" /f

:: 3. Ϊ�ļ���ͼ����������Ĳ˵�
reg add "HKCR\Directory\shell\%APP_NAME%" /ve /d "%MENU_TEXT%" /f
reg add "HKCR\Directory\shell\%APP_NAME%" /v "Icon" /d "\"%SHORT_PATH%\"" /f

:: 4. ����������
reg add "HKCR\*\shell\%APP_NAME%\command" /ve /d "%CMD_LINE%" /f
reg add "HKCR\Directory\shell\%APP_NAME%\command" /ve /d "%CMD_LINE%" /f
reg add "HKCR\Directory\Background\shell\%APP_NAME%\command" /ve /d "%BG_CMD_LINE%" /f

echo �Ҽ��˵������ɣ�
echo.
echo ���������λ���Ҽ��˵���
echo - �ļ��Ҽ��˵�
echo - �ļ���ͼ���Ҽ��˵�
echo - �ļ��пհ״��Ҽ��˵�
echo.
if defined APP_PARAMS (
    echo ʹ�õ������в���: %APP_PARAMS%
    echo.
)
echo ע�⣺������Ҫ������Դ�����������µ�¼���ܿ���Ч��
pause
goto MAIN_MENU

:UNINSTALL
echo �����Ƴ� %APP_NAME% �Ҽ��˵�...

:: ɾ��ע�����
reg delete "HKCR\*\shell\%APP_NAME%" /f 2>nul
reg delete "HKCR\Directory\shell\%APP_NAME%" /f 2>nul
reg delete "HKCR\Directory\Background\shell\%APP_NAME%" /f 2>nul

:: ����Ƿ�ɹ��Ƴ�
reg query "HKCR\*\shell\%APP_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %APP_NAME% �Ҽ��˵��ѳɹ��Ƴ���
) else (
    echo ���棺���� %APP_NAME% ע��������δ����ȫ�Ƴ�
)

echo ע�⣺������Ҫ������Դ�����������µ�¼������ȫ��Ч
pause
goto MAIN_MENU