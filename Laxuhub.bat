@echo off
setlocal enabledelayedexpansion

:: 配置文件路径
set "CONFIG_FILE=%~dp0laxuhub_config.ini"
set "oldpath=%path%"

:main
cls
echo.
echo    ================================
echo        Laxuhub 开发环境引导器
echo    ================================
echo.

:: 检查是否存在配置文件
if exist "%CONFIG_FILE%" (
    call :load_config
    if not errorlevel 1 (
        echo    检测到上次配置: 
        for %%i in (!LAST_ENVIRONMENTS!) do echo        %%i
        echo.
        set /p "confirm=是否加载上次配置？(回车确认/Y=确认/N=重新配置): "
        if "!confirm!"=="" goto quick_start
        if /i "!confirm!"=="y" goto quick_start
        if /i "!confirm!"=="n" goto config_mode
        goto main
    )
)

:config_mode
:: 发现所有可用环境
call :discover_environments

:: 显示选择菜单
:show_menu
cls
echo.
echo    ================================
echo       环境配置 - 多语言选择
echo    ================================
echo.
echo    请选择要使用的环境（可多选，输入多个编号用空格分隔）
echo.

set /a index=0
for /f "tokens=1,* delims==" %%a in ('set env_ 2^>nul') do (
    set /a index+=1
    for /f "tokens=1,2 delims=_" %%c in ("%%a") do (
        echo [!index!] %%d : %%b
    )
)
echo.
echo [0] 完成选择
echo.
echo    示例: 1 3 5  (选择Go、Node.js、Python310)
echo.

:: 获取用户选择
set /p "choices=请输入要选择的环境编号: "

if "!choices!"=="0" goto save_config

:: 验证并处理选择
set "SELECTED_ENVS="
set "error_msg="

for %%c in (!choices!) do (
    set "selected_env="
    set /a index=0
    
    :: 直接遍历环境变量
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
        set "error_msg=!error_msg!编号 %%c 无效 "
    ) else (
        for /f "tokens=1 delims=_" %%i in ("!selected_env!") do set "current_lang=%%i"
        
        set "duplicate=0"
        for %%e in (!SELECTED_ENVS!) do (
            for /f "tokens=1 delims=_" %%i in ("%%e") do (
                if "%%i"=="!current_lang!" set "duplicate=1"
            )
        )
        
        if !duplicate! equ 1 (
            set "error_msg=!error_msg!语言 !current_lang! 已选择 "
        ) else (
            if "!SELECTED_ENVS!"=="" (
                set "SELECTED_ENVS=!selected_env!"
            ) else (
                set "SELECTED_ENVS=!SELECTED_ENVS! !selected_env!"
            )
        )
    )
)

:: 显示错误信息
if not "!error_msg!"=="" (
    echo.
    echo 错误: !error_msg!
    echo 请重新选择
    pause
    goto config_mode
)

if "!SELECTED_ENVS!"=="" (
    echo 错误：未选择任何环境！
    pause
    goto config_mode
)

:save_config
:: 保存配置
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
echo       快速启动环境
echo    ================================
echo.
echo    正在启动: !LAST_ENVIRONMENTS!
echo.
echo    ================================

:: 设置基础环境变量
set "mybin=%~dp0mybin"

:: 自动发现并添加 sub_ 开头的子目录到 mybin_sub
set "mybin_sub="
for /d %%i in ("%mybin%\sub_*") do (
    if "!mybin_sub!"=="" (
        set "mybin_sub=%%i"
    ) else (
        set "mybin_sub=!mybin_sub!;%%i"
    )
)

set "PATH=%mybin%;%mybin_sub%;%PATH%"

:: 设置clink历史命令存放目录
set "CLINK_PROFILE=%~dp0data\temp"
del /f /q "%CLINK_PROFILE%\clink_errorlevel_*.txt" 2>nul

:: 加载每个选择的环境
for %%e in (!LAST_ENVIRONMENTS!) do (
    for /f "tokens=1,2 delims=_" %%i in ("%%e") do (
        set "lang=%%i"
        set "version=%%j"
    )
    
    echo [设置 !lang! 环境: !version!]...
    
    :: 使用不同的变量名避免冲突
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

:: 显示环境状态
echo.
echo ================================
echo    环境变量设置完成：
echo ================================
if defined PYTHON_HOME echo Python: !PYTHON_HOME!
if defined JC_HOME echo Node.js: !JC_HOME!
if defined GO_HOME echo Go: !GO_HOME!
if defined JAVA_HOME echo java: !JAVA_HOME!
echo.
echo PATH: !PATH!
echo.

:: 调用镜像源设置脚本（如果存在）
if exist "%mybin%\cn_mirror.bat" (
    call "%mybin%\cn_mirror.bat"
) else (
    echo "cn_mirror.bat"文件不存在，使用默认源
)

:: 验证命令可用性
echo ================================
echo    验证命令可用性：
echo ================================
python --version >nul 2>&1 && echoc 10 Python命令可用 || echo ? Python命令不可用
node --version >nul 2>&1 && echoc 10 Node.js命令可用 || echo ? Node.js命令不可用  
go version >nul 2>&1 && echoc 10 Go命令可用 || echo ? Go命令不可用
java --version >nul 2>&1 && echoc 10 java命令可用 || echo ? java命令不可用
echo.

:: 启动Clink
echo ================================
echo    启动Clink环境...
echo ================================
if exist "%1" (
    cd /d "%1"
) else (
    cd /d "%USERPROFILE%\Desktop"
)

cmd /k "clink.bat inject --quiet"

goto main

:discover_environments
:: 清空环境变量
for /f "delims==" %%i in ('set env_ 2^>nul') do set "%%i="

:: 自动发现所有 green_ 开头的环境目录
set /a total_index=0
for /d %%d in ("%~dp0green_*") do (
    :: 获取语言名称（去掉green_前缀）
    set "dir_name=%%~nxd"
    set "current_lang=!dir_name:~6!"
    
    set /a index=0
    
    :: 发现该语言的所有版本（只搜索对应语言开头的目录）
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