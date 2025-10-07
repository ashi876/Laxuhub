@echo off
setlocal enabledelayedexpansion
::win10 1903后cmd默认用utf8,使用for /f "delims="切割语法时要改代码页，以及批处理本身也要用utf8
::chcp 65001 >nul
D:\Laxuhub\green_python\Python313_demucs\Scripts\demucs.exe --mp3 --mp3-bitrate 192 --filename "{stem}.mp3" %1
pause