@echo off
:: ==============================================
:: ��ʱ�޸Ŀ�����������Դ������ǰCMD������Ч��
:: �ָ�Ĭ�ϣ��رյ�ǰ���ڻ�����CMD����
:: ==============================================

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
echo [pip ��ǰԴ����]
echo PIP_INDEX_URL=%PIP_INDEX_URL%
echo PIP_TRUSTED_HOST=%PIP_TRUSTED_HOST%
if defined PIP_EXTRA_INDEX_URL echo PIP_EXTRA_INDEX_URL=%PIP_EXTRA_INDEX_URL%
if defined PIP_TIMEOUT echo PIP_TIMEOUT=%PIP_TIMEOUT%

:: ʾ������
:: pip install numpy --verbose

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
echo [UV ��ǰԴ����]
echo UV_INDEX_URL=%UV_INDEX_URL%
if defined UV_TRUSTED_HOST echo UV_TRUSTED_HOST=%UV_TRUSTED_HOST%

:: ʾ������
:: uv pip install numpy --verbose

:: ******************************
:: 3. ���� Hugging Face ����Դ
:: ******************************
:: ��ǰ��ЧԴ��hf-mirror��
set HF_ENDPOINT=https://hf-mirror.com

:: ���ùٷ�Դ
:: set HF_ENDPOINT=https://huggingface.co

:: ��ӡ����
echo [HF ��ǰԴ����]
echo HF_ENDPOINT=%HF_ENDPOINT%

:: ʾ������
:: huggingface-cli download bigscience/bloom-560m --resume-download

:: ******************************
