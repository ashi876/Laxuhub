@echo off
:: ==============================================
:: 请勿再此脚本内用set path=XXX修改设置系统变量！！！
:: 本脚本仅用于设置镜像源
:: ==============================================
echo 加载镜像源...
:: ******************************
:: 1. 配置 pip 镜像源
:: ******************************
:: 原始源（备用参考）
:: set ORIGINAL_INDEX_URL=https://pypi.org/simple/
:: set ORIGINAL_TRUSTED_HOST=pypi.org

:: 当前生效源（清华）
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 备用源（取消注释启用）
:: 阿里云
:: set PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
:: set PIP_TRUSTED_HOST=mirrors.aliyun.com
:: 中科大
:: set PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple/
:: set PIP_TRUSTED_HOST=pypi.mirrors.ustc.edu.cn

:: 可选设置
set PIP_EXTRA_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
set PIP_TIMEOUT=120

:: 打印配置
:: [pip 当前源配置]
set PIP_INDEX_URL
set PIP_TRUSTED_HOST
set PIP_EXTRA_INDEX_URL
set PIP_TIMEOUT


:: ******************************
:: 2. 配置 UV pip 镜像源
:: ******************************
:: 当前生效源（清华）
set UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
set UV_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 备用源（取消注释启用）
:: 阿里云
:: set UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
:: set UV_TRUSTED_HOST=mirrors.aliyun.com

:: 打印配置
REM echo [UV 当前源配置]
REM echo UV_INDEX_URL=%UV_INDEX_URL%
set UV_INDEX_URL
set UV_TRUSTED_HOST

:: ******************************
:: 3. 配置 Hugging Face 镜像源
:: ******************************
:: 当前生效源（hf-mirror）
set HF_ENDPOINT=https://hf-mirror.com

:: 备用官方源
:: set HF_ENDPOINT=https://huggingface.co

:: 打印配置
set HF_ENDPOINT

:: 示例命令
:: huggingface-cli download bigscience/bloom-560m --resume-download

:: ******************************


:: 设置所有Node.js包管理工具的国内镜像源
::[npm yarn pnpm当前源配置]
set TAOBAO_NPM=https://registry.npmmirror.com
set TENCENT_NPM=https://mirrors.cloud.tencent.com/npm/
set HUAWEI_NPM=https://mirrors.huaweicloud.com/repository/npm/
set USTC_NPM=https://npmreg.mirrors.ustc.edu.cn/

:: 设置npm镜像源（默认使用淘宝源）
set npm_config_registry=%TAOBAO_NPM%
set npm_config_registry

:: 设置yarn镜像源
set YARN_REGISTRY=%TAOBAO_NPM%
set YARN_REGISTRY

:: 设置pnpm镜像源
set PNPM_REGISTRY=%TAOBAO_NPM%
set PNPM_REGISTRY

:: 设置go镜像源
set GOPROXY=https://goproxy.cn,direct
REM set GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
REM set GOPROXY=https://repo.huaweicloud.com/repository/goproxy/,direct
set GOPROXY

@echo off
echo 设置 Rust 国内镜像源...

:: 设置 rustup cargo 镜像源环境变量
:: 中科大
set CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse
set RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static
set RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup
set CARGO_REGISTRIES_CRATES_IO_INDEX=https://mirrors.ustc.edu.cn/crates.io-index


:: 清华
REM set RUSTUP_DIST_SERVER=https://rsproxy.cn
REM set RUSTUP_UPDATE_ROOT=https://rsproxy.cn/rustup

:: 设置阿里云镜像
REM set RUSTUP_DIST_SERVER=https://mirrors.aliyun.com/rustup
REM set RUSTUP_UPDATE_ROOT=https://mirrors.aliyun.com/rustup/rustup

set CARGO_REGISTRIES_CRATES_IO_PROTOCOL
set RUSTUP_DIST_SERVER
set RUSTUP_UPDATE_ROOT




echo=


