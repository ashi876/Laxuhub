#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import subprocess
import platform
import os
import sys
import time

def run_command(cmd):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def detect_system_info():
    """自动检测系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # 映射系统名称
    if system == "linux":
        os_type = "linux"
    elif system == "darwin":
        os_type = "darwin"
    elif system == "windows":
        os_type = "windows"
    else:
        os_type = system

    # 映射架构
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        arch = machine

    return os_type, arch

def construct_download_url(version, os_type, arch):
    """构造Go绿色包下载链接"""
    if os_type == "windows":
        extension = "zip"
    else:
        extension = "tar.gz"

    filename = f"go{version}.{os_type}-{arch}.{extension}"
    url = f"https://go.dev/dl/{filename}"
    return url

def get_go_versions():
    """从mise的versions host获取完整的Go版本列表"""
    try:
        print("正在从mise服务获取Go版本列表...")
        url = "https://mise-versions.jdx.dev/go"

        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
            # 按行分割，过滤空行和空白字符
            versions = [line.strip() for line in content.splitlines() if line.strip()]

        # 自定义排序函数，使版本号从新到旧
        def version_key(v):
            parts = v.split('.')
            # 补全为三位版本号以便排序，例如 "1.20" 变成 ["1", "20", "0"]
            while len(parts) < 3:
                parts.append('0')
            return [int(x) for x in parts]

        versions.sort(key=version_key, reverse=True)

        # 转换为与原来兼容的格式
        version_list = []
        for version in versions:
            version_list.append({
                'version': version,
                'stable': True,  # 所有Go发布版都视为稳定版
                'date': ''       # 不获取日期，保持简单
            })

        return version_list
    except Exception as e:
        print(f"获取版本列表失败: {e}")
        return []

def download_file(url, download_path="."):
    """下载文件"""
    filename = os.path.join(download_path, url.split('/')[-1])

    try:
        print(f"正在下载: {url}")
        print(f"保存到: {filename}")

        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                print(f"\r进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="", flush=True)

        urllib.request.urlretrieve(url, filename, report_progress)
        print("\n下载完成!")
        return filename
    except Exception as e:
        print(f"\n下载失败: {e}")
        return None

def display_versions_page(versions, current_version, page=1, page_size=50):
    """分页显示版本列表"""
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, len(versions))
    page_versions = versions[start_idx:end_idx]

    total_pages = (len(versions) + page_size - 1) // page_size

    print(f"\nGo版本列表 (第 {page}/{total_pages} 页, 共 {len(versions)} 个版本):")
    print("=" * 80)
    print(f"{'编号':<6} {'版本号':<15} {'稳定版':<10}")
    print("-" * 80)

    for i, ver_info in enumerate(page_versions, start_idx + 1):
        version = ver_info['version']
        stable_status = "是" if ver_info['stable'] else "否"

        # 标记当前版本和最新版本
        markers = []
        if current_version == version:
            markers.append("当前")
        if i == 1:
            markers.append("最新")
        marker_str = " ←" + ",".join(markers) if markers else ""

        print(f"{i:<6} v{version:<14} {stable_status:<10}{marker_str}")

    print("-" * 80)
    return total_pages

def get_arrow_input():
    """获取包含方向键的输入（仅支持Windows）"""
    if sys.platform == "win32":
        import msvcrt
        key = msvcrt.getch()
        if key == b'\xe0':  # 扩展键前缀
            key = msvcrt.getch()
            if key == b'K':  # 左箭头
                return 'left'
            elif key == b'M':  # 右箭头
                return 'right'
        elif key == b'\r':  # 回车
            return 'enter'
        elif key == b'q' or key == b'Q':
            return 'quit'
        elif key.isdigit():
            return key.decode('utf-8')
    else:
        # 非Windows系统（简化处理，只接收数字和q）
        try:
            # 设置原始终端模式以读取单个字符（这里简化，不实现复杂方向键）
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == 'q' or ch == 'Q':
                    return 'quit'
                elif ch.isdigit():
                    return ch
                else:
                    # 简单处理左右箭头（通过读取后续字符）
                    if ch == '\x1b':
                        ch = sys.stdin.read(2)  # 读取 '[D' 或 '[C'
                        if ch == '[D':
                            return 'left'
                        elif ch == '[C':
                            return 'right'
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            # 如果无法设置终端，降级处理
            pass
    return None

def check_go_updates():
    """检查Go版本更新并提供下载选项"""
    print("\n检查Go版本更新...")

    # 获取当前Go版本（如果有）
    go_version = run_command("go version")
    current_version = None
    if go_version:
        # 解析版本号
        parts = go_version.split()
        if len(parts) >= 3 and parts[2].startswith('go'):
            current_version = parts[2][2:]  # 去掉"go"前缀
            print(f"当前Go版本: v{current_version}")
        else:
            print("无法解析Go版本")
    else:
        print("未找到Go编译器")

    # 获取可用的Go版本列表
    versions = get_go_versions()
    if not versions:
        input("\n按回车键退出...")
        return

    # 分页显示版本列表
    page_size = 20
    current_page = 1
    total_pages = display_versions_page(versions, current_version, current_page, page_size)

    # 获取最新版本信息
    latest_version = versions[0]['version'] if versions else None

    # 检查是否有更新
    if current_version and latest_version and current_version != latest_version:
        print(f"\n有更新可用! 当前: v{current_version}, 最新: v{latest_version}")

    print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")

    # 选择版本下载
    while True:
        try:
            print("请选择: ", end='', flush=True)

            choice = get_arrow_input()

            if choice == 'quit':
                print("\n退出")
                break
            elif choice == 'left':
                current_page = current_page - 1 if current_page > 1 else total_pages
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
                continue
            elif choice == 'right':
                current_page = current_page + 1 if current_page < total_pages else 1
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
                continue
            elif choice and choice.isdigit():
                # 处理多位数输入
                number_input = choice
                print(number_input, end='', flush=True)

                # 等待更多数字输入（短暂超时）
                if sys.platform == "win32":
                    import msvcrt
                    start_time = time.time()
                    while time.time() - start_time < 1.0:
                        if msvcrt.kbhit():
                            next_char = msvcrt.getch()
                            if next_char.isdigit():
                                number_input += next_char.decode('utf-8')
                                print(next_char.decode('utf-8'), end='', flush=True)
                                start_time = time.time()
                            else:
                                # 将非数字字符放回缓冲区（例如回车）
                                msvcrt.ungetch(next_char)
                                break
                        time.sleep(0.05)

                print()  # 换行
                try:
                    index = int(number_input) - 1
                    if 0 <= index < len(versions):
                        selected_version_info = versions[index]
                        selected_version = selected_version_info['version']

                        # 检测系统信息
                        os_type, arch = detect_system_info()
                        print(f"\n检测到系统: {os_type}, 架构: {arch}")

                        # 构造下载链接
                        download_url = construct_download_url(selected_version, os_type, arch)
                        print(f"版本: v{selected_version}")
                        print(f"下载链接: {download_url}")

                        # 确认下载
                        confirm = input(f"\n确认下载 v{selected_version}? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes', '是']:
                            downloaded_file = download_file(download_url)
                            if downloaded_file:
                                print(f"下载成功! 文件保存在: {downloaded_file}")
                                print("请手动解压并安装到 green_go/ 目录")
                            break
                        else:
                            print("取消下载")
                            # 重新显示当前页
                            display_versions_page(versions, current_version, current_page, page_size)
                            print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
                            continue
                    else:
                        print(f"请输入 1-{len(versions)} 之间的数字")
                except ValueError:
                    print("无效的数字")
                # 重新显示当前页
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
            else:
                # 无效输入，重新显示提示
                print("\n无效输入，请使用方向键或输入数字")
                # 可以重新显示当前页
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")

        except KeyboardInterrupt:
            print("\n\n用户中断")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            break

    input("\n按回车键退出...")

if __name__ == "__main__":
    check_go_updates()