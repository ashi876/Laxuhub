
@echo off
:: һ����������Node.js�������ߵĹ��ھ���Դ
:: ʹ�÷�ʽ��call set_npm_mirrors.bat ��ֱ��˫������

set TAOBAO_NPM=https://registry.npmmirror.com
set TENCENT_NPM=https://mirrors.cloud.tencent.com/npm/
set HUAWEI_NPM=https://mirrors.huaweicloud.com/repository/npm/
set USTC_NPM=https://npmreg.mirrors.ustc.edu.cn/

:: ����npm����Դ��Ĭ��ʹ���Ա�Դ��
set npm_config_registry=%TAOBAO_NPM%
echo npm����������Ϊ: %TAOBAO_NPM%

:: ����yarn����Դ
set YARN_REGISTRY=%TAOBAO_NPM%
echo yarn����������Ϊ: %TAOBAO_NPM%

:: ����pnpm����Դ
set PNPM_REGISTRY=%TAOBAO_NPM%
echo pnpm����������Ϊ: %TAOBAO_NPM%

:: ��ʾ��֤����
echo.
echo ��֤���
echo npm config get registry
echo yarn config get registry
echo pnpm config get registry
echo.
echo ע�⣺��Щ���ý��ڵ�ǰ�����д�����Ч
