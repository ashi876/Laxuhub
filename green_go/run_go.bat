@echo off
setlocal enabledelayedexpansion

:: 获取当前脚本路径和目录
set "self=%~f0"
set "dir=%~dp0"
set "count=0"

:: 列出当前目录所有go开头的文件夹
echo 正在搜索go目录...
for /d %%f in ("%dir%go*") do (
    set /a count+=1
    set "dir[!count!]=%%~ff"
    set "last_dir=%%~nxf"
)

:: 如果没有找到符合条件的文件夹
if %count% equ 0 (
    echo 错误：未找到go目录（名称应以go开头）
    pause
    exit /b
)

:: 如果只有一个go目录，自动选择
if %count% equ 1 (
    echo 检测到唯一的go目录: %last_dir%
    set "choice=1"
    goto setenv
)

:: 多个目录时显示选择菜单
echo 可用的go目录列表：
for /l %%i in (1,1,%count%) do (
    for %%A in ("!dir[%%i]!") do (
        echo [%%i] %%~nxA
    )
)

:: 用户选择部分
:retry
echo.
set /p "choice=请输入要使用的go目录编号(1-%count%)："

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
set "GO_ROOT=!dir[%choice%]!"
set "GO_HOME=!GO_ROOT!\bin"
set "mybin=%~dp0..\mybin"

:: 自动发现并添加 sub_ 开头的子目录到 mybin_sub
set "mybin_sub="
for /d %%i in ("%mybin%\sub_*") do (
    if "!mybin_sub!"=="" (
        set "mybin_sub=%%i"
    ) else (
        set "mybin_sub=!mybin_sub!;%%i"
    )
)

:: 设置PATH环境变量
set "PATH=%GO_HOME%;%mybin%;%mybin_sub%;%PATH%"

:: 调用镜像源设置脚本（如果存在）
if exist "%mybin%\cn_mirror.bat" (
    call "%mybin%\cn_mirror.bat"
) else (
    echo "cn_mirror.bat"文件不存在，使用默认源
)

:: 设置clink历史命令存放目录
set "CLINK_PROFILE=%~dp0..\data\temp"
del /f /q %CLINK_PROFILE%\clink_errorlevel_*.txt 2>nul

:: 检查go.exe是否存在
if not exist "%GO_HOME%\go.exe" (
    echo 错误：在选定的目录中未找到go可执行文件 >&2
    echo 检查路径: %GO_HOME%\go.exe
    pause
    exit /b 1
)
echo.

:: 显示设置成功的具体go目录名称（显示根目录名而不是bin）
for %%A in ("%GO_ROOT%") do (
    echoc 15 已成功设置 10 [%%~nxA] 15 环境:
)
echo GO_ROOT=%GO_ROOT%
echo GO_HOME=%GO_HOME%
echo.

set mydesk="%USERPROFILE%\Desktop"

cd /d %mydesk%

go version

:: 启动Clink
echo [独立模式] 启动Clink...
cmd /k "clink.bat inject --quiet"

pause
exit /b