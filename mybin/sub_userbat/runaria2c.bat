setlocal enabledelayedexpansion
title aria2c下载服务
mode con: cols=60 lines=25
@cd /d %~dp0..\sub_cli
@echo 进入aria2c.exe工作目录%cd%
@echo=
@echo 开始执行NG配置及aria2c服务...
::start "up_tracker" %~dp0trackerup.bat
start %~dp0..\sub_cli\aria2\index.html&&aria2c.exe --conf=%~dp0..\sub_cli\aria2\aria2.conf
