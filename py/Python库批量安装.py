import subprocess
import time
import sys
import io
 
# 设置标准输出和错误输出的编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
 
# 需要安装的包列表
PACKAGES = [
    "pywin32",
    "pyinstaller",
    "glances",
    "Flask",
    "pyperclip",
    "pillow",
    "requests",
    "pystray",
    "pandas",
    "docxtpl",
    "openpyxl",
    "lxml",
    "retrying",
    "bs4",
    "mysql-connector-python",
    "faker",
    "pysimplegui",
    "opencv-python",
    "tqdm",
    "ttkbootstrap",
    "pyecharts",
    "fitz",
    "PySide6",
    "waitress",
    "PyQt6"
]
 
def install_package(package, max_retries=3, retry_delay=10):
    """
    安装指定的Python包，优先使用国内镜像源，如果失败会自动重试
    :param package: 要安装的包名
    :param max_retries: 最大重试次数
    :param retry_delay: 重试间隔(秒)
    """
    retry_count = 0
     
    # 国内镜像源列表
    MIRRORS = [
        "https://pypi.tuna.tsinghua.edu.cn/simple/",
        "https://mirrors.aliyun.com/pypi/simple/",
        "https://pypi.mirrors.ustc.edu.cn/simple/"
    ]
     
    while retry_count < max_retries:
        try:
            print(f"正在安装 {package}... (尝试 {retry_count + 1}/{max_retries})")
             
            # 前3次尝试使用国内镜像源
            if retry_count < 3:
                mirror = MIRRORS[retry_count % len(MIRRORS)]
                print(f"使用镜像源: {mirror}")
                cmd = [sys.executable, "-m", "pip", "install", package, "-i", mirror, "--trusted-host", mirror.split("//")[1]]
            else:
                # 3次失败后使用默认源
                print("切换至默认源")
                cmd = [sys.executable, "-m", "pip", "install", package]
             
            subprocess.check_call(cmd, shell=True, encoding='utf-8')
            print(f"成功安装 {package}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"安装 {package} 失败: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
     
    print(f"安装 {package} 失败，已达到最大重试次数 {max_retries}")
    return False
 
def check_and_install_pip(max_retries=3, retry_delay=10):
    """
    检查并安装pip，如果失败会自动重试
    :param max_retries: 最大重试次数
    :param retry_delay: 重试间隔(秒)
    :return: 是否安装成功
    """
    retry_count = 0
     
    while retry_count < max_retries:
        try:
            print(f"检查pip安装状态... (尝试 {retry_count + 1}/{max_retries})")
            subprocess.check_call([sys.executable, "-m", "pip", "--version"], shell=True, encoding='utf-8')
            print("pip已安装")
             
            # 检查并更新pip到最新版本
            try:
                print("正在检查pip更新...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                                    shell=True, encoding='utf-8')
                print("pip已更新到最新版本")
            except subprocess.CalledProcessError as e:
                print(f"pip更新失败: {e}")
                 
            return True
        except subprocess.CalledProcessError:
            print("pip未安装，正在尝试安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade", "--default-pip"], 
                                    shell=True, encoding='utf-8')
                print("pip安装成功")
                return True
            except subprocess.CalledProcessError as e:
                print(f"pip安装失败: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
     
    print(f"pip安装失败，已达到最大重试次数 {max_retries}")
    return False
 
def main():
    """主函数，依次安装所有包"""
    success_count = 0
    failure_count = 0
     
    # 先检查并安装pip
    if not check_and_install_pip():
        print("pip安装失败，无法继续安装其他包")
        return
     
    print(f"开始安装 {len(PACKAGES)} 个Python包...")
     
    for package in PACKAGES:
        if install_package(package):
            success_count += 1
        else:
            failure_count += 1
     
    print(f"\n安装完成: 成功 {success_count} 个, 失败 {failure_count} 个")
 
if __name__ == "__main__":
    main()