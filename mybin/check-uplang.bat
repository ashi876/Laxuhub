@echo off
setlocal enabledelayedexpansion
::win10 1903后cmd默认用utf8,使用for /f "delims="切割语法时要改代码页，以及批处理本身也要用utf8
::chcp 65001 >nul

set uplang_py_dir=%~dp0\uplang_py

python %uplang_py_dir%\check_go.py
echo=
python %uplang_py_dir%\check_rust.py
echo=
python %uplang_py_dir%\check_nodejs.py
echo=
python %uplang_py_dir%\check_java.py
echo=
python %uplang_py_dir%\check_python.py