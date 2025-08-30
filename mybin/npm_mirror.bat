
@echo off
:: 一键设置所有Node.js包管理工具的国内镜像源
:: 使用方式：call set_npm_mirrors.bat 或直接双击运行

set TAOBAO_NPM=https://registry.npmmirror.com
set TENCENT_NPM=https://mirrors.cloud.tencent.com/npm/
set HUAWEI_NPM=https://mirrors.huaweicloud.com/repository/npm/
set USTC_NPM=https://npmreg.mirrors.ustc.edu.cn/

:: 设置npm镜像源（默认使用淘宝源）
set npm_config_registry=%TAOBAO_NPM%
echo npm镜像已设置为: %TAOBAO_NPM%

:: 设置yarn镜像源
set YARN_REGISTRY=%TAOBAO_NPM%
echo yarn镜像已设置为: %TAOBAO_NPM%

:: 设置pnpm镜像源
set PNPM_REGISTRY=%TAOBAO_NPM%
echo pnpm镜像已设置为: %TAOBAO_NPM%

:: 显示验证命令
echo.
echo 验证命令：
echo npm config get registry
echo yarn config get registry
echo pnpm config get registry
echo.
echo 注意：这些设置仅在当前命令行窗口有效
