@echo off
setlocal enabledelayedexpansion

:: �����ļ�·��
set "CONFIG_FILE=%~dp0laxuhub_config.ini"
set "oldpath=%path%"

:main
cls
echo.
echo    ================================
echo        Laxuhub ��������������
echo    ================================
echo.

:: ����Ƿ���������ļ�
if exist "%CONFIG_FILE%" (
    call :load_config
    if not errorlevel 1 (
        echo    ��⵽�ϴ�����: 
        for %%i in (!LAST_ENVIRONMENTS!) do echo        %%i
        echo.
        set /p "confirm=�Ƿ�����ϴ����ã�(�س�ȷ��/Y=ȷ��/N=��������): "
        if "!confirm!"=="" goto quick_start
        if /i "!confirm!"=="y" goto quick_start
        if /i "!confirm!"=="n" goto config_mode
        goto main
    )
)

:config_mode
:: �������п��û���
call :discover_environments

:: ��ʾѡ��˵�
:show_menu
cls
echo.
echo    ================================
echo       �������� - ������ѡ��
echo    ================================
echo.
echo    ��ѡ��Ҫʹ�õĻ������ɶ�ѡ������������ÿո�ָ���
echo.

set /a index=0
for /f "tokens=1,* delims==" %%a in ('set env_ 2^>nul') do (
    set /a index+=1
    for /f "tokens=1,2 delims=_" %%c in ("%%a") do (
        echo [!index!] %%d : %%b
    )
)
echo.
echo [0] ���ѡ��
echo.
echo    ʾ��: 1 3 5  (ѡ��Go��Node.js��Python310)
echo.

:: ��ȡ�û�ѡ��
set /p "choices=������Ҫѡ��Ļ������: "

if "!choices!"=="0" goto save_config

:: ��֤������ѡ��
set "SELECTED_ENVS="
set "error_msg="

for %%c in (!choices!) do (
    set "selected_env="
    set /a index=0
    
    :: ֱ�ӱ�����������
    for /f "tokens=1,* delims==" %%a in ('set env_ 2^>nul') do (
        set /a index+=1
        if !index! equ %%c (
            set "var_name=%%a"
            set "var_value=%%b"
            for /f "tokens=1,2 delims=_" %%i in ("!var_name!") do (
                set "selected_env=%%j_!var_value!"
            )
        )
    )
    
    if "!selected_env!"=="" (
        set "error_msg=!error_msg!��� %%c ��Ч "
    ) else (
        for /f "tokens=1 delims=_" %%i in ("!selected_env!") do set "current_lang=%%i"
        
        set "duplicate=0"
        for %%e in (!SELECTED_ENVS!) do (
            for /f "tokens=1 delims=_" %%i in ("%%e") do (
                if "%%i"=="!current_lang!" set "duplicate=1"
            )
        )
        
        if !duplicate! equ 1 (
            set "error_msg=!error_msg!���� !current_lang! ��ѡ�� "
        ) else (
            if "!SELECTED_ENVS!"=="" (
                set "SELECTED_ENVS=!selected_env!"
            ) else (
                set "SELECTED_ENVS=!SELECTED_ENVS! !selected_env!"
            )
        )
    )
)

:: ��ʾ������Ϣ
if not "!error_msg!"=="" (
    echo.
    echo ����: !error_msg!
    echo ������ѡ��
    pause
    goto config_mode
)

if "!SELECTED_ENVS!"=="" (
    echo ����δѡ���κλ�����
    pause
    goto config_mode
)

:save_config
:: ��������
(
    echo [Settings]
    echo LastEnvironments=!SELECTED_ENVS!
    echo ConfigVersion=1.0
) > "%CONFIG_FILE%"

set "LAST_ENVIRONMENTS=!SELECTED_ENVS!"
goto quick_start

:quick_start
cls
echo.
echo    ================================
echo       ������������
echo    ================================
echo.
echo    ��������: !LAST_ENVIRONMENTS!
echo.
echo    ================================

:: ���û�����������
set "mybin=%~dp0mybin"

:: �Զ����ֲ���� sub_ ��ͷ����Ŀ¼�� mybin_sub
set "mybin_sub="
for /d %%i in ("%mybin%\sub_*") do (
    if "!mybin_sub!"=="" (
        set "mybin_sub=%%i"
    ) else (
        set "mybin_sub=!mybin_sub!;%%i"
    )
)

set "PATH=%mybin%;%mybin_sub%;%PATH%"

:: ����clink��ʷ������Ŀ¼
set "CLINK_PROFILE=%~dp0data\temp"
del /f /q "%CLINK_PROFILE%\clink_errorlevel_*.txt" 2>nul

:: ����ÿ��ѡ��Ļ���
for %%e in (!LAST_ENVIRONMENTS!) do (
    for /f "tokens=1,2 delims=_" %%i in ("%%e") do (
        set "lang=%%i"
        set "version=%%j"
    )
    
    echo [���� !lang! ����: !version!]...
    
    :: ʹ�ò�ͬ�ı����������ͻ
    for /d %%g in ("%~dp0green_!lang!*") do (
        if exist "%%g\!version!" (
            if "!lang!"=="python" (
                set "PYTHON_HOME=%%g\!version!"
                set "PATH=!PYTHON_HOME!;!PYTHON_HOME!\Scripts;!PATH!"
            ) else if "!lang!"=="node" (
                set "JC_HOME=%%g\!version!"
                set "PATH=!JC_HOME!;!PATH!"
            ) else if "!lang!"=="go" (
                set "GO_ROOT=%%g\!version!"
                set "GO_HOME=!GO_ROOT!\bin"
                set "PATH=!GO_HOME!;!PATH!"
            ) else if "!lang!"=="java" (
                set "JAVA_ROOT=%%g\!version!"
                set "JAVA_HOME=!JAVA_ROOT!\bin"
                set "PATH=!JAVA_HOME!;!PATH!"
                echo JAVA_HOME=!JAVA_HOME!
            )
        )
    )
)

:: ��ʾ����״̬
echo.
echo ================================
echo    ��������������ɣ�
echo ================================
if defined PYTHON_HOME echo Python: !PYTHON_HOME!
if defined JC_HOME echo Node.js: !JC_HOME!
if defined GO_HOME echo Go: !GO_HOME!
if defined JAVA_HOME echo java: !JAVA_HOME!
echo.
echo PATH: !PATH!
echo.

:: ���þ���Դ���ýű���������ڣ�
if exist "%mybin%\cn_mirror.bat" (
    call "%mybin%\cn_mirror.bat"
) else (
    echo "cn_mirror.bat"�ļ������ڣ�ʹ��Ĭ��Դ
)

:: ��֤���������
echo ================================
echo    ��֤��������ԣ�
echo ================================
python --version >nul 2>&1 && echoc 10 Python������� || echo ? Python�������
node --version >nul 2>&1 && echoc 10 Node.js������� || echo ? Node.js�������  
go version >nul 2>&1 && echoc 10 Go������� || echo ? Go�������
java --version >nul 2>&1 && echoc 10 java������� || echo ? java�������
echo.

:: ����Clink
echo ================================
echo    ����Clink����...
echo ================================
if exist "%1" (
    cd /d "%1"
) else (
    cd /d "%USERPROFILE%\Desktop"
)

cmd /k "clink.bat inject --quiet"

goto main

:discover_environments
:: ��ջ�������
for /f "delims==" %%i in ('set env_ 2^>nul') do set "%%i="

:: �Զ��������� green_ ��ͷ�Ļ���Ŀ¼
set /a total_index=0
for /d %%d in ("%~dp0green_*") do (
    :: ��ȡ�������ƣ�ȥ��green_ǰ׺��
    set "dir_name=%%~nxd"
    set "current_lang=!dir_name:~6!"
    
    set /a index=0
    
    :: ���ָ����Ե����а汾��ֻ������Ӧ���Կ�ͷ��Ŀ¼��
    for /d %%v in ("%%d\!current_lang!*") do (
        set /a index+=1
        set /a total_index+=1
        set "env_!current_lang!_!index!=%%~nxv"
    )
)
exit /b 0

:load_config
set "LAST_ENVIRONMENTS="
for /f "tokens=2 delims==" %%i in ('findstr "LastEnvironments" "%CONFIG_FILE%" 2^>nul') do (
    set "LAST_ENVIRONMENTS=%%i"
)
if "!LAST_ENVIRONMENTS!"=="" exit /b 1
exit /b 0