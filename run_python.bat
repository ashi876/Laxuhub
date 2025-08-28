@echo off
setlocal enabledelayedexpansion

:: 获取当前脚本路径和目录
set "self=%~f0"
set "dir=%~dp0"
set "count=0"

:: 列出当前目录所有python开头的文件夹
echo 正在搜索Python目录...
for /d %%f in ("%dir%python*") do (
    set /a count+=1
    set "dir[!count!]=%%~ff"
    set "last_dir=%%~nxf"
)

:: 如果没有找到符合条件的文件夹
if %count% equ 0 (
    echo 错误：未找到Python目录（名称应以python开头）
    pause
    exit /b
)

:: 如果只有一个Python目录，自动选择
if %count% equ 1 (
    echo 检测到唯一的Python目录: %last_dir%
    set "choice=1"
    goto setenv
)

:: 多个目录时显示选择菜单
echo 可用的Python目录列表：
for /l %%i in (1,1,%count%) do (
    for %%A in ("!dir[%%i]!") do (
        echo [%%i] %%~nxA
    )
)

:: 用户选择部分
:retry
echo.
set /p "choice=请输入要使用的Python目录编号(1-%count%)："

:: 验证输入是否为空
if "%choice%"=="" (
    echo 错误：输入不能为空！
    goto retry
)

:: 验证是否为纯数字
set /a "test=choice" 2>nul
if errorlevel 1 (
    echo 错误：输入必须是数字，您输入的是 "%choice%"
    goto retry
)

:: 验证数字范围
if %choice% lss 1 (
    echo 错误：编号不能小于 1，您输入的是 "%choice%"
    goto retry
)
if %choice% gtr %count% (
    echo 错误：编号不能大于 %count%，您输入的是 "%choice%"
    goto retry
)
echo=

:: 设置环境变量
:setenv
set "PYTHON_HOME=!dir[%choice%]!"
set "mybin=%~dp0mybin"
set "ffmpeg_path=D:\serve\ffmpeg"

if exist "%ffmpeg_path%" (
    echo ffmpeg目录为%ffmpeg_path%
) else (
    echo ffmpeg目录不存在,不使用可无视
)

:: 设置PATH环境变量
set "PATH=%ffmpeg_path%;%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%mybin%;%PATH%"

:: 调用镜像源设置脚本（如果存在）
if exist "%mybin%\cn_mirror.bat" (
    call "%mybin%\cn_mirror.bat"
) else (
    echo "cn_mirror.bat"文件不存在，使用默认源
)


:: 设置clink历史命令存放目录
set "CLINK_PROFILE=%~dp0\mybin\temp"
del /f /q %CLINK_PROFILE%\clink_errorlevel_*.txt 2>nul

:: 检查python.exe是否存在
if not exist "%PYTHON_HOME%\python.exe" (
    echo 错误：在选定的目录中未找到Python可执行文件 >&2
    pause
    exit /b 1
)
echo.

:: 显示设置成功的具体Python目录名称
for %%A in ("%PYTHON_HOME%") do (
    echoc 15 已成功设置 10 [%%~nxA] 15 环境:
)
echo PYTHON_HOME=%PYTHON_HOME%
echo.

set mypy="%~dp0py"
set mydesk="%USERPROFILE%\Desktop"
echo 输入cd /d %%mypy%% 进入%mypy%目录
echo 输入cd /d %%mydesk%% 进入%mydesk%目录
cd /d %mydesk%

pip -V
if !errorlevel! equ 1 (
    echoc 12 检测到pip命令错误,运行[pipreset.bat]或[pipsafeup.bat]
)

:: 启动Clink
cmd /k ""%~dp0mybin\clink\clink.bat" inject --quiet"

pause
exit /b