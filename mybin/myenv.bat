@echo off

REM 创建 Python 虚拟环境的批处理脚本
setlocal enabledelayedexpansion

set "mybin=%~dp0"
set "clink=%mybin%clink\clink.bat inject --quiet"

REM 设置默认环境名称
set "env_name=myenv"
if not "%1"=="" set "env_name=%1"

REM 检查虚拟环境目录是否已存在
if exist "%env_name%" (
    echo 错误：目录 "%env_name%" 已存在
    echo 请选择其他名称或删除现有目录
    pause
    exit /b 1
)

:: 查找Python解释器（优先使用调用脚本的Python）
set "python_exe=python"
where !python_exe! >nul 2>nul || (
    echo 错误：未找到 Python 解释器
    echo 请确保 Python 已安装并添加到 PATH
    pause
    exit /b 1
)

REM 创建虚拟环境
echo 正在创建虚拟环境: %env_name%
%python_exe% -m venv "%env_name%"

if errorlevel 1 (
    echo 错误：创建虚拟环境失败
    pause
    exit /b 1
)

echo 虚拟环境创建成功！
echo 正在启动虚拟环境新窗口...
:: 写入一键启动虚拟环境窗口的脚本
set tmp_name=%env_name%

echo @echo off>%cd%\%env_name%.bat
echo set tmp_name=%env_name%>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo title %%tmp_name%% 虚拟环境>>%cd%\%env_name%.bat
echo set path=%%path%%;%mybin%>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo cd /d %cd%\%%tmp_name%%>>%cd%\%env_name%.bat
echo call Scripts\activate>>%cd%\%env_name%.bat
echo call 镜像源.bat>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo echo 使用%%tmp_name%% 虚拟环境>>%cd%\%env_name%.bat
echo python -V>>%cd%\%env_name%.bat
echo=>>%cd%\%env_name%.bat
echo cmd /k %clink%>>%cd%\%env_name%.bat

start %cd%\%env_name%.bat
