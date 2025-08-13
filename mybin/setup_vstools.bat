@echo off
setlocal enabledelayedexpansion

:: --- 主脚本逻辑（保持原功能，但使用 --passive 替代 --p）---
set "downloadUrl=https://aka.ms/vs/17/release/vs_BuildTools.exe"
set "installerFile=vs_BuildTools.exe"
set "layoutDir=C:\VS2022_Offline"
set "setupExe=%layoutDir%\vs_setup.exe"

:: 1. 下载 VS Build Tools
echo 正在下载 VS Build Tools 安装程序...
curl -L -o "%installerFile%" "%downloadUrl%"
if not exist "%installerFile%" (
    echo [错误] 下载失败，请检查网络或 URL 是否有效！
    exit /b 1
)
echo 下载成功！文件路径: %CD%\%installerFile%

:: 2. 创建离线布局
echo 正在生成离线安装包（目录: %layoutDir%）...
"%installerFile%" --layout "%layoutDir%" --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools --includeRecommended --lang en-US
if not exist "%setupExe%" (
    echo [错误] 离线布局生成失败，请检查磁盘空间或权限！
    exit /b 1
)
echo 离线布局已创建成功！

:: 3. 安装（使用 --passive 模式）
echo 正在安装 VS Build Tools（被动模式）...
"%setupExe%" --noweb --norestart --passive --wait
if %errorlevel% equ 3010 (
    echo [警告] 安装成功但需要重启系统 (错误代码: 3010)
    exit /b 0
) else if %errorlevel% neq 0 (
    echo [错误] 安装失败，错误代码: %errorlevel%
    exit /b %errorlevel%
)

:: 完成
echo ---------------------------------------------------
echo VS Build Tools 已成功安装！
echo 离线包路径: %layoutDir%
echo 清理临时文件: del "%installerFile%"
pause