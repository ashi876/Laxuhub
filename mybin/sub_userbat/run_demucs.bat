@echo off
setlocal enabledelayedexpansion
::win10 1903��cmdĬ����utf8,ʹ��for /f "delims="�и��﷨ʱҪ�Ĵ���ҳ���Լ���������ҲҪ��utf8
::chcp 65001 >nul
D:\Laxuhub\green_python\Python313_demucs\Scripts\demucs.exe --mp3 --mp3-bitrate 192 --filename "{stem}.mp3" %1
pause