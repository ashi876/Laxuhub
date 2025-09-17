@echo off
setlocal enabledelayedexpansion

:: 配置区域 - 只需修改这里的变量即可用于其他程序
set "APP_EXE=LaxuHub.exe"
set "APP_NAME=LaxuHub"
set "MENU_TEXT=使用 %APP_NAME% 打开"
set "APP_PARAMS=-q"
:: 配置区域结束

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员身份运行此脚本
    pause
    exit /b 1
)

:MAIN_MENU
cls
echo ==============================
echo     %APP_NAME% 右键菜单管理
echo ==============================
echo.
echo 请选择操作：
echo 1. 注册右键菜单
echo 2. 卸载右键菜单
echo 3. 退出
echo.
set /p choice="请输入选项 (1-3): "

if "%choice%"=="1" goto REGISTER
if "%choice%"=="2" goto UNINSTALL
if "%choice%"=="3" exit /b 0

echo 无效选项，请重新输入
pause
goto MAIN_MENU

:REGISTER
cd /d %~dp0
:: 自动检测当前目录下的程序
set "APP_PATH=%~dp0%APP_EXE%"

:: 检查程序是否存在
if not exist "%APP_PATH%" (
    echo 错误：在当前目录未找到 %APP_EXE%
    echo 当前目录：%CD%
    echo 请确保本批处理与 %APP_EXE% 在同一目录下
    pause
    goto MAIN_MENU
)

echo 找到 %APP_EXE%：%APP_PATH%
echo.

:: 如果路径中有空格，请使用短路径格式
set "SHORT_PATH=%APP_PATH: =" "%"
for %%I in ("%SHORT_PATH%") do set "SHORT_PATH=%%~sI"

:: 构建命令行参数
if defined APP_PARAMS (
    set "CMD_LINE=\"%APP_PATH%\" %APP_PARAMS% \"%%1\""
    set "BG_CMD_LINE=\"%APP_PATH%\" %APP_PARAMS% \"%%V\""
) else (
    set "CMD_LINE=\"%APP_PATH%\" \"%%1\""
    set "BG_CMD_LINE=\"%APP_PATH%\" \"%%V\""
)

:: 注册表操作
echo 正在添加右键菜单...

:: 1. 为文件和文件夹添加上下文菜单
reg add "HKCR\*\shell\%APP_NAME%" /ve /d "%MENU_TEXT%" /f
reg add "HKCR\*\shell\%APP_NAME%" /v "Icon" /d "\"%SHORT_PATH%\"" /f

:: 2. 为文件夹背景（空白处）添加上下文菜单
reg add "HKCR\Directory\Background\shell\%APP_NAME%" /ve /d "在此处启动 %APP_NAME%" /f
reg add "HKCR\Directory\Background\shell\%APP_NAME%" /v "Icon" /d "\"%SHORT_PATH%\"" /f

:: 3. 为文件夹图标添加上下文菜单
reg add "HKCR\Directory\shell\%APP_NAME%" /ve /d "%MENU_TEXT%" /f
reg add "HKCR\Directory\shell\%APP_NAME%" /v "Icon" /d "\"%SHORT_PATH%\"" /f

:: 4. 添加命令操作
reg add "HKCR\*\shell\%APP_NAME%\command" /ve /d "%CMD_LINE%" /f
reg add "HKCR\Directory\shell\%APP_NAME%\command" /ve /d "%CMD_LINE%" /f
reg add "HKCR\Directory\Background\shell\%APP_NAME%\command" /ve /d "%BG_CMD_LINE%" /f

echo 右键菜单添加完成！
echo.
echo 已添加以下位置右键菜单：
echo - 文件右键菜单
echo - 文件夹图标右键菜单
echo - 文件夹空白处右键菜单
echo.
if defined APP_PARAMS (
    echo 使用的命令行参数: %APP_PARAMS%
    echo.
)
echo 注意：可能需要重启资源管理器或重新登录才能看到效果
pause
goto MAIN_MENU

:UNINSTALL
echo 正在移除 %APP_NAME% 右键菜单...

:: 删除注册表项
reg delete "HKCR\*\shell\%APP_NAME%" /f 2>nul
reg delete "HKCR\Directory\shell\%APP_NAME%" /f 2>nul
reg delete "HKCR\Directory\Background\shell\%APP_NAME%" /f 2>nul

:: 检查是否成功移除
reg query "HKCR\*\shell\%APP_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %APP_NAME% 右键菜单已成功移除！
) else (
    echo 警告：部分 %APP_NAME% 注册表项可能未被完全移除
)

echo 注意：可能需要重启资源管理器或重新登录才能完全生效
pause
goto MAIN_MENU