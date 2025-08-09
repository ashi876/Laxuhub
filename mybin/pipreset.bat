@echo off
setlocal enabledelayedexpansion

:: ================================================
:: 绿色版Python迁移修复工具
:: 功能：初始化pip + 路径固化(保持相同版本)
:: 适用：绿色版Python目录移动后使用
:: ================================================

echo.
echo [1/3] 正在定位Python解释器...
echo.

:: 查找Python解释器
set "PYTHON_EXE="
for /f "tokens=*" %%a in ('where python 2^>nul') do (
    set "PYTHON_EXE=%%a"
    set "PYTHON_DIR=%%~dpa"
    goto :python_found
)

:python_not_found
echo 错误: 未找到Python解释器
echo 请确保:
echo   1. Python已加入PATH环境变量
echo   2. 或在此目录运行: %~dp0
exit /b 1

:python_found
echo 使用Python: %PYTHON_EXE%
echo 安装目录: %PYTHON_DIR%
echo.

:: ================================================
:: 核心修复流程
:: ================================================

:: 步骤1: 初始化到内置版本
echo [2/3] 初始化pip到内置版本...
echo 执行: %PYTHON_EXE% -m ensurepip --upgrade --default-pip
"%PYTHON_EXE%" -m ensurepip --upgrade --default-pip
if errorlevel 1 (
    echo 错误: pip初始化失败
    echo 可能原因: 
    echo   - 网络连接问题
    echo   - Python环境损坏
    echo   - 权限不足
    exit /b 1
)
echo 初始化成功!
echo.

:: 步骤2: 获取当前版本
echo 获取当前pip版本...
set "CURRENT_PIP_VERSION="
for /f "tokens=1,2 delims= " %%a in ('"%PYTHON_EXE%" -m pip --version 2^>nul') do (
    if "%%a"=="pip" set "CURRENT_PIP_VERSION=%%b"
)

if not defined CURRENT_PIP_VERSION (
    echo 错误: 无法获取pip版本号
    echo 尝试手动命令: %PYTHON_EXE% -m pip --version
    exit /b 1
)
echo 当前pip版本: !CURRENT_PIP_VERSION!
echo.

:: 步骤3: 相同版本重装(路径固化)
echo [3/3] 路径固化(安装相同版本:!CURRENT_PIP_VERSION!)...
echo 执行: %PYTHON_EXE% -m pip install --force-reinstall --no-cache-dir "pip==!CURRENT_PIP_VERSION!"
"%PYTHON_EXE%" -m pip install --force-reinstall --no-cache-dir "pip==!CURRENT_PIP_VERSION!"
if errorlevel 1 (
    echo 错误: 路径固化失败
    echo 建议尝试:
    echo   1. 检查网络连接
    echo   2. 临时关闭防火墙/杀毒软件
    echo   3. 手动运行: %PYTHON_EXE% -m pip install --force-reinstall pip
    exit /b 1
)
echo 路径固化成功!
echo.

:: ================================================
:: 配置国内镜像源（原版配置）
:: ================================================

REM set "PIP_CONFIG=%APPDATA%\pip\pip.ini"
REM if not exist "%APPDATA%\pip\" mkdir "%APPDATA%\pip"

REM set "TEMP_CONFIG=%TEMP%\pip_temp_%RANDOM%.ini"
REM (
    REM echo [global]
    REM echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
    REM echo extra-index-url = https://mirrors.aliyun.com/pypi/simple/ https://pypi.mirrors.ustc.edu.cn/simple/
    REM echo trusted-host = pypi.tuna.tsinghua.edu.cn mirrors.aliyun.com pypi.mirrors.ustc.edu.cn
    REM echo timeout = 120
REM ) > "%TEMP_CONFIG%"

REM move /Y "%TEMP_CONFIG%" "%PIP_CONFIG%" > nul
REM echo 镜像源配置文件位置: %PIP_CONFIG%
REM echo 内容:
REM type "%PIP_CONFIG%"
REM echo.

:: ================================================
:: 验证结果
:: ================================================

echo 最终验证:
echo Python路径: %PYTHON_DIR%
"%PYTHON_EXE%" --version
"%PYTHON_EXE%" -m pip --version
echo.

echo 显示pip配置:
"%PYTHON_EXE%" -m pip config list
echo.

:: ================================================
:: 完成提示
:: ================================================

echo [成功] %PYTHON_DIR% 环境修复完成!
echo 操作总结:
echo   1. 初始化pip到内置版本
echo   2. 路径固化(保持版本 !CURRENT_PIP_VERSION!)
echo.
echo 提示: 移动Python目录后需要重新运行此脚本
echo.
endlocal