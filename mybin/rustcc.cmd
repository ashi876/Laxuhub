@echo off
setlocal enabledelayedexpansion
::win10 1903��cmdĬ����utf8,ʹ��for /f "delims="�и��﷨ʱҪ�Ĵ���ҳ���Լ���������ҲҪ��utf8
::chcp 65001 >nul
rust %RUSTFLAGS% %1