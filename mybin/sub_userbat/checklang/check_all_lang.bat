@echo off
cls
echo.
echo   ================================
echo       ���������汾��鹤��
echo   ================================
echo.
echo   ��ѡ��Ҫ�������Ի�����
echo.
echo   [1] Java �汾���
echo   [2] Python �汾���  
echo   [3] Go �汾���
echo   [4] Node.js �汾���
echo   [5] Rust �汾���
echo   [6] ȫ�����
echo.
echo   [0] �˳�
echo.

set /p choice=������ѡ�� (0-6): 

if "%choice%"=="1" goto java
if "%choice%"=="2" goto python
if "%choice%"=="3" goto go
if "%choice%"=="4" goto nodejs
if "%choice%"=="5" goto rust
if "%choice%"=="6" goto all
if "%choice%"=="0" goto exit
echo ��Чѡ������������
pause
exit

:java
echo ���ڼ��Java�汾...
python %~dp0check_java.py
goto end

:python
echo ���ڼ��Python�汾...
python %~dp0check_python.py
goto end

:go
echo ���ڼ��Go�汾...
python %~dp0check_go.py
goto end

:nodejs
echo ���ڼ��Node.js�汾...
python %~dp0check_nodejs.py
goto end

:rust
echo ���ڼ��Rust�汾...
python %~dp0check_rust.py
goto end

:all
echo ���μ���������԰汾...
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
echo �˳�
exit

:end
echo.
echo �����ɣ������������LaxuHub...
pause >nul