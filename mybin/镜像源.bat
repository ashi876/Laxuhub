@echo off
:: ==============================================
:: 临时修改开发环境镜像源（仅当前CMD窗口生效）
:: 恢复默认：关闭当前窗口或重启CMD即可
:: ==============================================

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
echo [pip 当前源配置]
echo PIP_INDEX_URL=%PIP_INDEX_URL%
echo PIP_TRUSTED_HOST=%PIP_TRUSTED_HOST%
if defined PIP_EXTRA_INDEX_URL echo PIP_EXTRA_INDEX_URL=%PIP_EXTRA_INDEX_URL%
if defined PIP_TIMEOUT echo PIP_TIMEOUT=%PIP_TIMEOUT%

:: 示例命令
:: pip install numpy --verbose

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
echo [UV 当前源配置]
echo UV_INDEX_URL=%UV_INDEX_URL%
if defined UV_TRUSTED_HOST echo UV_TRUSTED_HOST=%UV_TRUSTED_HOST%

:: 示例命令
:: uv pip install numpy --verbose

:: ******************************
:: 3. 配置 Hugging Face 镜像源
:: ******************************
:: 当前生效源（hf-mirror）
set HF_ENDPOINT=https://hf-mirror.com

:: 备用官方源
:: set HF_ENDPOINT=https://huggingface.co

:: 打印配置
echo [HF 当前源配置]
echo HF_ENDPOINT=%HF_ENDPOINT%

:: 示例命令
:: huggingface-cli download bigscience/bloom-560m --resume-download

:: ******************************
