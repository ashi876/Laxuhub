setlocal enabledelayedexpansion
title aria2c���ط���
mode con: cols=60 lines=25
@cd /d %~dp0..\sub_cli
@echo ����aria2c.exe����Ŀ¼%cd%
@echo=
@echo ��ʼִ��NG���ü�aria2c����...
::start "up_tracker" %~dp0trackerup.bat
start %~dp0..\sub_cli\aria2\index.html&&aria2c.exe --conf=%~dp0..\sub_cli\aria2\aria2.conf
