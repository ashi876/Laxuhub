@echo off
setlocal enabledelayedexpansion
::win10 1903��cmdĬ����utf8,ʹ��for /f "delims="�и��﷨ʱҪ�Ĵ���ҳ���Լ���������ҲҪ��utf8
::chcp 65001 >nul
npx webdav-cli --host 0.0.0.0 --path D:\webdav --port 8081 --username admin --password 123 --rights canRead,canWrite