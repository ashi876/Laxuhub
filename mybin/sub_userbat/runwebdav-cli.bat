@echo off
setlocal enabledelayedexpansion
::win10 1903后cmd默认用utf8,使用for /f "delims="切割语法时要改代码页，以及批处理本身也要用utf8
::chcp 65001 >nul
npx webdav-cli --host 0.0.0.0 --path D:\webdav --port 8081 --username admin --password 123 --rights canRead,canWrite