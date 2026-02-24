#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import subprocess
import platform
import os
import sys
import time

def get_current_rust_version():
    """获取当前安装的Rust版本"""
    try:
        result = subprocess.run(['rustc', '--version'], capture_output=True, text=True, check=True)
        version = result.stdout.strip().split()[1]
        return version
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_rust_versions():
    """从mise的versions host获取完整的Rust版本列表"""
    try:
        print("正在从mise服务获取Rust版本列表...")
        url = "https://mise-versions.jdx.dev/rust"

        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
            # 按行分割，过滤空行
            all_versions = [line.strip() for line in content.splitlines() if line.strip()]

        # 过滤掉 "nightly", "beta", "stable" 这些不是具体版本号的条目
        # 同时过滤掉 1.0.0-alpha 这类预览版，只保留数字版本如 1.84.0
        versions = []
        for v in all_versions:
            # 跳过非数字开头的特殊条目
            if not v[0].isdigit():
                continue
            # 简单的过滤：如果包含字母（如alpha, rc），通常不是稳定版，可以选择跳过
            # 这里为了与原始脚本逻辑一致（原始脚本过滤了beta/nightly），我们只保留纯数字和点组成的版本
            if all(part.isdigit() for part in v.split('.')):
                versions.append(v)

        # 自定义排序函数，使版本号从新到旧
        def version_key(v):
            parts = v.split('.')
            # 补全为三位版本号以便排序，例如 "1.2" 变成 ["1", "2", "0"]
            while len(parts) < 3:
                parts.append('0')
            return [int(x) for x in parts]

        versions.sort(key=version_key, reverse=True)

        # 转换为与原脚本兼容的格式
        version_list = []
        for version in versions:
            version_list.append({
                'version': version,
                'stable': True,  # 我们过滤后留下的都视为稳定版
                'date': ''       # 不获取日期，保持简单
            })

        return version_list
    except Exception as e:
        print(f"获取版本列表失败: {e}")
        return []

def detect_system_info():
    """自动检测系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "linux":
        os_type = "linux"
    elif system == "darwin":
        os_type = "darwin"
    elif system == "windows":
        os_type = "windows"
    else:
        os_type = system

    if machine in ["x86_64", "amd64"]:
        arch = "x86_64"
    elif machine in ["arm64", "aarch64"]:
        arch = "aarch64"
    else:
        arch = machine

    return os_type, arch

def construct_rust_download_url(version, os_type, arch):
    """构造Rust下载链接"""
    if os_type == "windows":
        filename = f"rust-{version}-{arch}-pc-windows-msvc.tar.gz"
    else:
        filename = f"rust-{version}-{arch}-unknown-{os_type}-gnu.tar.gz"
    url = f"https://static.rust-lang.org/dist/{filename}"
    return url

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

    print(f"\nRust版本列表 (第 {page}/{total_pages} 页, 共 {len(versions)} 个版本):")
    print("=" * 80)
    print(f"{'编号':<6} {'版本号':<15} {'稳定版':<10}")
    print("-" * 80)

    for i, ver_info in enumerate(page_versions, start_idx + 1):
        version = ver_info['version']
        stable_status = "是" if ver_info['stable'] else "否"

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
    """获取包含方向键的输入（保留原有实现）"""
    if sys.platform == "win32":
        import msvcrt
        key = msvcrt.getch()
        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'K':
                return 'left'
            elif key == b'M':
                return 'right'
        elif key == b'\r':
            return 'enter'
        elif key == b'q' or key == b'Q':
            return 'quit'
        elif key.isdigit():
            return key.decode('utf-8')
    else:
        # 保留原有的Unix方向键处理逻辑
        try:
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch = sys.stdin.read(1)
                    if ch == '[':
                        ch = sys.stdin.read(1)
                        if ch == 'D':
                            return 'left'
                        elif ch == 'C':
                            return 'right'
                elif ch in ('\r', '\n'):
                    return 'enter'
                elif ch in ('q', 'Q'):
                    return 'quit'
                elif ch.isdigit():
                    return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            pass
    return None

def check_rust_updates():
    """检查Rust版本更新并提供下载选项"""
    print("\n检查Rust版本更新...")

    current_version = get_current_rust_version()
    if current_version:
        print(f"当前Rust版本: v{current_version}")
    else:
        print("未找到Rust")
        print("注意: Rust通常使用rustup工具管理版本")
        print("建议使用rustup安装和管理Rust: https://rustup.rs/")

    versions = get_rust_versions()
    if not versions:
        input("\n按回车键退出...")
        return

    page_size = 20
    current_page = 1
    total_pages = display_versions_page(versions, current_version, current_page, page_size)

    latest_version = versions[0]['version'] if versions else None
    if current_version and latest_version and current_version != latest_version:
        print(f"\n有更新可用! 当前: v{current_version}, 最新: v{latest_version}")

    print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")

    # 交互循环（完全保留原有逻辑）
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
                number_input = choice
                print(number_input, end='', flush=True)

                # 多位数输入等待
                if sys.platform == "win32":
                    import msvcrt
                    start_time = time.time()
                    while time.time() - start_time < 1.0:
                        if msvcrt.kbhit():
                            next_char = msvcrt.getch()
                            if next_char.isdigit():
                                number_input += next_char.decode()
                                print(next_char.decode(), end='', flush=True)
                                start_time = time.time()
                            else:
                                break
                        time.sleep(0.05)

                print()
                try:
                    index = int(number_input) - 1
                    if 0 <= index < len(versions):
                        selected_version_info = versions[index]
                        selected_version = selected_version_info['version']

                        os_type, arch = detect_system_info()
                        print(f"\n检测到系统: {os_type}, 架构: {arch}")

                        download_url = construct_rust_download_url(selected_version, os_type, arch)
                        print(f"版本: v{selected_version}")
                        print(f"下载链接: {download_url}")

                        confirm = input(f"\n确认下载 v{selected_version}? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes', '是']:
                            downloaded_file = download_file(download_url)
                            if downloaded_file:
                                print(f"下载成功! 文件: {downloaded_file}")
                                print("请手动解压并安装到 green_rust/ 目录")
                            break
                        else:
                            print("取消下载")
                    else:
                        print(f"请输入 1-{len(versions)} 之间的数字")
                except ValueError:
                    print("无效的数字")

                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
            else:
                print("\n无效输入")
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
    check_rust_updates()