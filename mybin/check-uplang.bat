@echo off
setlocal enabledelayedexpansion
::win10 1903��cmdĬ����utf8,ʹ��for /f "delims="�и��﷨ʱҪ�Ĵ���ҳ���Լ���������ҲҪ��utf8
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