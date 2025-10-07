@echo off
cls
echo.
echo   ================================
echo       开发环境版本检查工具
echo   ================================
echo.
echo   请选择要检查的语言环境：
echo.
echo   [1] Java 版本检查
echo   [2] Python 版本检查  
echo   [3] Go 版本检查
echo   [4] Node.js 版本检查
echo   [5] Rust 版本检查
echo   [6] 全部检查
echo.
echo   [0] 退出
echo.

set /p choice=请输入选择 (0-6): 

if "%choice%"=="1" goto java
if "%choice%"=="2" goto python
if "%choice%"=="3" goto go
if "%choice%"=="4" goto nodejs
if "%choice%"=="5" goto rust
if "%choice%"=="6" goto all
if "%choice%"=="0" goto exit
echo 无效选择，请重新运行
pause
exit

:java
echo 正在检查Java版本...
python %~dp0check_java.py
goto end

:python
echo 正在检查Python版本...
python %~dp0check_python.py
goto end

:go
echo 正在检查Go版本...
python %~dp0check_go.py
goto end

:nodejs
echo 正在检查Node.js版本...
python %~dp0check_nodejs.py
goto end

:rust
echo 正在检查Rust版本...
python %~dp0check_rust.py
goto end

:all
echo 依次检查所有语言版本...
echo.
echo === Java ===
python %~dp0check_java.py
echo.
echo === Python ===  
python %~dp0check_python.py
echo.
echo === Go ===
python %~dp0check_go.py
echo.
echo === Node.js ===
python %~dp0check_nodejs.py
echo.
echo === Rust ===
python %~dp0check_rust.py
goto end

:exit
echo 退出
exit

:end
echo.
echo 检查完成，按任意键返回LaxuHub...
pause >nul