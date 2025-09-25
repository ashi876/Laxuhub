@echo off
setlocal enabledelayedexpansion

title UV 版本管理工具

echo ================================
echo        UV 版本管理工具
echo ================================

:: 检查当前版本
if exist "%~dp0uv.exe" (
    echo 当前 UV 版本信息:
    for /f "tokens=*" %%i in ('"%~dp0uv.exe" --version 2^>^&1') do (
        set "current_version=%%i"
        echo %%i
    )
    echo.
) else (
    echo 未找到 uv.exe，开始下载...
    echo.
)

:: 获取最新版本号
echo 正在获取最新版本信息...
for /f "tokens=*" %%i in ('powershell -Command "(Invoke-RestMethod -Uri 'https://api.github.com/repos/astral-sh/uv/releases/latest').tag_name"') do (
    set "latest_version=%%i"
)

if "!current_version!"=="" (
    echo 最新版本: !latest_version!
) else (
    for /f "tokens=2" %%v in ("!current_version!") do set "current_ver=%%v"
    if "!current_ver!"=="!latest_version!" (
        echo 当前已是最新版本: !latest_version!
        echo 无需更新。
        pause
        exit /b 0
    ) else (
        echo 当前版本: !current_ver!
        echo 最新版本: !latest_version!
        echo.
        set /p confirm="是否更新到最新版本？(y/n): "
        if /i not "!confirm!"=="y" (
            echo 操作已取消。
            pause
            exit /b 0
        )
    )
)

echo.
echo 正在下载并安装最新版 UV...

set "download_url=https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
set "zip_file=uv-latest.zip"
set "backup_file=uv-backup.exe"

:: 备份旧版本
if exist "%~dp0uv.exe" (
    echo 备份旧版本...
    copy "%~dp0uv.exe" "!backup_file!" >nul
)

echo 步骤1: 下载 UV...
powershell -Command "Invoke-WebRequest -Uri '%download_url%' -OutFile '%zip_file%'"

if not exist "%zip_file%" (
    echo 下载失败！
    if exist "!backup_file!" (
        echo 恢复备份...
        move "!backup_file!" "%~dp0uv.exe" >nul
    )
    pause
    exit /b 1
)

echo 步骤2: 解压文件...
powershell -Command "Expand-Archive -Path '%zip_file%' -DestinationPath '%~dp0' -Force"

echo 步骤3: 清理临时文件...
if exist "%zip_file%" del "%zip_file%"
if exist "!backup_file!" del "!backup_file!"

if exist "%~dp0uv.exe" (
    echo.
    echo 安装成功！
    echo 更新后 UV 版本信息:
    "%~dp0uv.exe" --version
    echo.
    echo 使用说明：
    echo - 直接运行 uv 命令即可
    echo - 无需配置环境变量
    echo - 绿色便携，随目录携带
) else (
    echo 错误：解压后未找到 uv.exe
    if exist "!backup_file!" (
        echo 恢复备份...
        move "!backup_file!" "%~dp0uv.exe" >nul
    )
)

echo.
pause