@echo off
:: ==============================================
:: �����ٴ˽ű�����set path=XXX�޸�����ϵͳ����������
:: ���ű����������þ���Դ
:: ==============================================
echo ���ؾ���Դ...
:: ******************************
:: 1. ���� pip ����Դ
:: ******************************
:: ԭʼԴ�����òο���
:: set ORIGINAL_INDEX_URL=https://pypi.org/simple/
:: set ORIGINAL_TRUSTED_HOST=pypi.org

:: ��ǰ��ЧԴ���廪��
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: ����Դ��ȡ��ע�����ã�
:: ������
:: set PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
:: set PIP_TRUSTED_HOST=mirrors.aliyun.com
:: �пƴ�
:: set PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple/
:: set PIP_TRUSTED_HOST=pypi.mirrors.ustc.edu.cn

:: ��ѡ����
set PIP_EXTRA_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
set PIP_TIMEOUT=120

:: ��ӡ����
:: [pip ��ǰԴ����]
set PIP_INDEX_URL
set PIP_TRUSTED_HOST
set PIP_EXTRA_INDEX_URL
set PIP_TIMEOUT


:: ******************************
:: 2. ���� UV pip ����Դ
:: ******************************
:: ��ǰ��ЧԴ���廪��
set UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
set UV_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: ����Դ��ȡ��ע�����ã�
:: ������
:: set UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
:: set UV_TRUSTED_HOST=mirrors.aliyun.com

:: ��ӡ����
REM echo [UV ��ǰԴ����]
REM echo UV_INDEX_URL=%UV_INDEX_URL%
set UV_INDEX_URL
set UV_TRUSTED_HOST

:: ******************************
:: 3. ���� Hugging Face ����Դ
:: ******************************
:: ��ǰ��ЧԴ��hf-mirror��
set HF_ENDPOINT=https://hf-mirror.com

:: ���ùٷ�Դ
:: set HF_ENDPOINT=https://huggingface.co

:: ��ӡ����
set HF_ENDPOINT

:: ʾ������
:: huggingface-cli download bigscience/bloom-560m --resume-download

:: ******************************


:: ��������Node.js�������ߵĹ��ھ���Դ
::[npm yarn pnpm��ǰԴ����]
set TAOBAO_NPM=https://registry.npmmirror.com
set TENCENT_NPM=https://mirrors.cloud.tencent.com/npm/
set HUAWEI_NPM=https://mirrors.huaweicloud.com/repository/npm/
set USTC_NPM=https://npmreg.mirrors.ustc.edu.cn/

:: ����npm����Դ��Ĭ��ʹ���Ա�Դ��
set npm_config_registry=%TAOBAO_NPM%
set npm_config_registry

:: ����yarn����Դ
set YARN_REGISTRY=%TAOBAO_NPM%
set YARN_REGISTRY

:: ����pnpm����Դ
set PNPM_REGISTRY=%TAOBAO_NPM%
set PNPM_REGISTRY

:: ����go����Դ
set GOPROXY=https://goproxy.cn,direct
REM set GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
REM set GOPROXY=https://repo.huaweicloud.com/repository/goproxy/,direct
set GOPROXY

@echo off
echo ���� Rust ���ھ���Դ...

:: ���� rustup cargo ����Դ��������
:: �пƴ�
set CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse
set RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static
set RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup
set CARGO_REGISTRIES_CRATES_IO_INDEX=https://mirrors.ustc.edu.cn/crates.io-index


:: �廪
REM set RUSTUP_DIST_SERVER=https://rsproxy.cn
REM set RUSTUP_UPDATE_ROOT=https://rsproxy.cn/rustup

:: ���ð����ƾ���
REM set RUSTUP_DIST_SERVER=https://mirrors.aliyun.com/rustup
REM set RUSTUP_UPDATE_ROOT=https://mirrors.aliyun.com/rustup/rustup

set CARGO_REGISTRIES_CRATES_IO_PROTOCOL
set RUSTUP_DIST_SERVER
set RUSTUP_UPDATE_ROOT




echo=


