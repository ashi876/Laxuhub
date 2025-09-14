@echo off
setlocal enabledelayedexpansion

:: ================================
:: 强制在线更新 pip 的终极方案
:: ================================

:: 配置区域
set PIP_URL=https://bootstrap.pypa.io/get-pip.py
set OUTPUT_FILE=new-get-pip.py
set PYTHON_EXE=python

:: 检查Python是否可用
where %PYTHON_EXE% >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] 未找到Python可执行文件
    echo 请确保Python已安装并添加至系统路径
    exit /b 1
)

:: 1. 检测wget是否可用（新增）
echo [1/5] 检测下载工具...
where wget >nul 2>nul
if %errorlevel% equ 0 (
    echo  使用wget下载安装器...
    wget --show-progress -O "%OUTPUT_FILE%" "%PIP_URL%"
    if %errorlevel% equ 0 (
        if exist "%OUTPUT_FILE%" (
            echo  √ 下载成功（wget）
            goto install
        )
    )
)

:: 2. 检测curl是否可用
echo [2/5] wget不可用，尝试curl...
where curl >nul 2>nul
if %errorlevel% equ 0 (
    echo  使用curl下载安装器...
    curl -L -k -o "%OUTPUT_FILE%" "%PIP_URL%" >nul 2>&1
    if exist "%OUTPUT_FILE%" (
        echo  √ 下载成功（curl）
        goto install
    )
)

:: 3. 切换到certutil下载
echo [3/5] curl不可用，改用powershell...
powershell -Command "Invoke-WebRequest -Uri '%PIP_URL%' -OutFile '%OUTPUT_FILE%' -UseBasicParsing" >nul 2>&1
if %errorlevel% equ 0 (
    if exist "%OUTPUT_FILE%" (
        echo  √ 下载成功（PowerShell）
        goto install
    )
)

:: 4. 下载失败处理
echo [4/5] 错误：下载失败！
echo 可能原因：
echo   a) 网络不通 - 尝试ping bootstrap.pypa.io
echo   b) 代理问题 - 检查网络代理设置
echo   c) 安全软件拦截 - 暂时禁用防火墙
exit /b 1

:: 5. 执行纯净安装
:install
echo [5/5] 执行纯净网络安装...
%PYTHON_EXE% "%OUTPUT_FILE%" --no-warn-script-location --no-cache-dir

:: 验证安装
echo.
echo 验证安装结果...
%PYTHON_EXE% -m pip --version
if %errorlevel% equ 0 (
    echo ======================================
    echo √ PIP 已通过纯净网络安装完成!
    echo ======================================
) else (
    echo [!] 安装验证失败
    echo 尝试手动安装: python %OUTPUT_FILE%
)

:: 清理文件
::del /q "%OUTPUT_FILE%" >nul 2>&1
exit /b