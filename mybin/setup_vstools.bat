@echo off
setlocal enabledelayedexpansion

:: --- ���ű��߼�������ԭ���ܣ���ʹ�� --passive ��� --p��---
set "downloadUrl=https://aka.ms/vs/17/release/vs_BuildTools.exe"
set "installerFile=vs_BuildTools.exe"
set "layoutDir=C:\VS2022_Offline"
set "setupExe=%layoutDir%\vs_setup.exe"

:: 1. ���� VS Build Tools
echo �������� VS Build Tools ��װ����...
curl -L -o "%installerFile%" "%downloadUrl%"
if not exist "%installerFile%" (
    echo [����] ����ʧ�ܣ���������� URL �Ƿ���Ч��
    exit /b 1
)
echo ���سɹ����ļ�·��: %CD%\%installerFile%

:: 2. �������߲���
echo �����������߰�װ����Ŀ¼: %layoutDir%��...
"%installerFile%" --layout "%layoutDir%" --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools --includeRecommended --lang en-US
if not exist "%setupExe%" (
    echo [����] ���߲�������ʧ�ܣ�������̿ռ��Ȩ�ޣ�
    exit /b 1
)
echo ���߲����Ѵ����ɹ���

:: 3. ��װ��ʹ�� --passive ģʽ��
echo ���ڰ�װ VS Build Tools������ģʽ��...
"%setupExe%" --noweb --norestart --passive --wait
if %errorlevel% equ 3010 (
    echo [����] ��װ�ɹ�����Ҫ����ϵͳ (�������: 3010)
    exit /b 0
) else if %errorlevel% neq 0 (
    echo [����] ��װʧ�ܣ��������: %errorlevel%
    exit /b %errorlevel%
)

:: ���
echo ---------------------------------------------------
echo VS Build Tools �ѳɹ���װ��
echo ���߰�·��: %layoutDir%
echo ������ʱ�ļ�: del "%installerFile%"
pause