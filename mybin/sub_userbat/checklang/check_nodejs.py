#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import subprocess
import re
import platform
import os
import sys

def get_current_node_version():
    """获取当前安装的Node.js版本"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
        version = result.stdout.strip().lstrip('v')
        return version
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_node_versions():
    """获取所有可用的Node.js版本"""
    try:
        print("正在获取Node.js版本列表...")
        with urllib.request.urlopen('https://nodejs.org/download/release/index.json') as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # 提取版本信息并排序（从新到旧）
        versions = []
        for item in data:
            version = item['version'].lstrip('v')
            lts = item.get('lts', False)
            lts_name = item.get('lts') if lts else None
            
            versions.append({
                'version': version,
                'lts': lts,
                'lts_name': lts_name,
                'date': item.get('date', '')
            })
        
        # 按版本号排序（从新到旧）
        versions.sort(key=lambda x: [int(part) for part in x['version'].split('.')], reverse=True)
        
        return versions
    except Exception as e:
        print("获取版本列表失败: " + str(e))
        return []

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
        os_type = "win"
    else:
        os_type = system
    
    # 映射架构
    if machine in ["x86_64", "amd64"]:
        arch = "x64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        arch = machine
    
    return os_type, arch

def construct_node_download_url(version, os_type, arch):
    """构造Node.js绿色包下载链接"""
    # Node.js的下载链接格式
    if os_type == "linux":
        filename = f"node-v{version}-{os_type}-{arch}.tar.xz"
    elif os_type == "darwin":
        filename = f"node-v{version}-{os_type}-{arch}.tar.gz"
    elif os_type == "win":
        filename = f"node-v{version}-{os_type}-{arch}.zip"
    else:
        filename = f"node-v{version}-{os_type}-{arch}.tar.gz"
    
    url = f"https://nodejs.org/dist/v{version}/{filename}"
    return url

def download_file(url, download_path="."):
    """下载文件"""
    filename = os.path.join(download_path, url.split('/')[-1])
    
    try:
        print("正在下载: " + url)
        print("保存到: " + filename)
        
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                print("\r进度: {:.1f}% ({}/{})".format(percent, downloaded, total_size), end="", flush=True)
        
        urllib.request.urlretrieve(url, filename, report_progress)
        print("\n下载完成!")
        return filename
    except Exception as e:
        print("\n下载失败: " + str(e))
        return None

def display_versions_page(versions, current_version, page=1, page_size=50):
    """分页显示版本列表"""
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_versions = versions[start_idx:end_idx]
    
    total_pages = (len(versions) + page_size - 1) // page_size
    
    print(f"\nNode.js版本列表 (第 {page}/{total_pages} 页, 共 {len(versions)} 个版本):")
    print("=" * 80)
    print(f"{'编号':<6} {'版本号':<15} {'LTS状态':<20} {'发布日期':<12}")
    print("-" * 80)
    
    for i, ver_info in enumerate(page_versions, start_idx + 1):
        version = ver_info['version']
        lts_status = f"LTS: {ver_info['lts_name']}" if ver_info['lts'] else "非LTS"
        
        # 标记当前版本和最新版本
        markers = []
        if current_version == version:
            markers.append("当前")
        if i == 1:  # 第一个是最新版本
            markers.append("最新")
        marker_str = " ←" + ",".join(markers) if markers else ""
        
        # 格式化日期
        date_str = ver_info['date'][:10] if ver_info['date'] else "未知"
        
        print(f"{i:<6} v{version:<14} {lts_status:<20} {date_str:<12}{marker_str}")
    
    print("-" * 80)
    return total_pages

def get_arrow_input():
    """获取包含方向键的输入"""
    if sys.platform == "win32":
        # Windows系统
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
        # Unix/Linux/macOS系统
        import termios
        import tty
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC序列
                ch = sys.stdin.read(1)
                if ch == '[':
                    ch = sys.stdin.read(1)
                    if ch == 'D':  # 左箭头
                        return 'left'
                    elif ch == 'C':  # 右箭头
                        return 'right'
            elif ch == '\r' or ch == '\n':  # 回车
                return 'enter'
            elif ch == 'q' or ch == 'Q':
                return 'quit'
            elif ch.isdigit():
                return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    return None

def check_node_updates():
    """检查Node.js版本更新并提供下载选项"""
    print("\n检查Node.js版本更新...")
    
    # 获取当前版本
    current_version = get_current_node_version()
    if current_version:
        print("当前Node版本: v" + current_version)
    else:
        print("未找到Node.js")
    
    # 获取可用的Node.js版本列表
    versions = get_node_versions()
    if not versions:
        print("无法获取版本列表")
        return
    
    # 分页显示版本列表
    page_size = 20  # 每页显示20个版本
    current_page = 1
    total_pages = display_versions_page(versions, current_version, current_page, page_size)
    
    # 获取最新版本信息
    latest_version = versions[0]['version'] if versions else None
    
    # 检查是否有更新
    if current_version and latest_version:
        current_parts = list(map(int, current_version.split('.')))
        latest_parts = list(map(int, latest_version.split('.')))
        
        if current_parts < latest_parts:
            print(f"\n有更新可用! 当前: v{current_version}, 最新: v{latest_version}")
    
    print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
    
    # 选择版本下载
    while True:
        try:
            print("请使用方向键 ← → 翻页，或输入版本编号: ", end='', flush=True)
            
            choice = get_arrow_input()
            
            if choice == 'quit' or choice == 'q':
                print("\n退出")
                break
            elif choice == 'left':
                # 上一页
                if current_page > 1:
                    current_page -= 1
                else:
                    current_page = total_pages  # 循环到最后一页
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
                continue
            elif choice == 'right':
                # 下一页
                if current_page < total_pages:
                    current_page += 1
                else:
                    current_page = 1  # 循环到第一页
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
                    import time
                    start_time = time.time()
                    while time.time() - start_time < 1.0:  # 1秒超时
                        if msvcrt.kbhit():
                            next_char = msvcrt.getch()
                            if next_char.isdigit():
                                number_input += next_char.decode('utf-8')
                                print(next_char.decode('utf-8'), end='', flush=True)
                                start_time = time.time()
                            else:
                                break
                        time.sleep(0.05)
                else:
                    import select
                    import termios
                    import tty
                    
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)
                        timeout = 1.0  # 1秒超时
                        start_time = time.time()
                        while time.time() - start_time < timeout:
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                next_char = sys.stdin.read(1)
                                if next_char.isdigit():
                                    number_input += next_char
                                    print(next_char, end='', flush=True)
                                    start_time = time.time()
                                else:
                                    break
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                print()  # 换行
                index = int(number_input) - 1
                if 0 <= index < len(versions):
                    selected_version_info = versions[index]
                    selected_version = selected_version_info['version']
                    
                    # 检测系统信息
                    os_type, arch = detect_system_info()
                    print(f"\n检测到系统: {os_type}, 架构: {arch}")
                    
                    # 构造下载链接
                    download_url = construct_node_download_url(selected_version, os_type, arch)
                    print(f"下载链接: {download_url}")
                    
                    # 显示版本信息
                    lts_info = f" (LTS: {selected_version_info['lts_name']})" if selected_version_info['lts'] else ""
                    print(f"版本信息: v{selected_version}{lts_info}")
                    print(f"发布日期: {selected_version_info['date']}")
                    
                    # 确认下载
                    confirm = input(f"\n确认下载 v{selected_version}? (y/n): ").lower().strip()
                    if confirm in ['y', 'yes', '是']:
                        downloaded_file = download_file(download_url)
                        if downloaded_file:
                            print(f"下载成功! 文件: {downloaded_file}")
                            print("请手动解压并安装")
                        break
                    else:
                        print("取消下载")
                        # 重新显示当前页
                        display_versions_page(versions, current_version, current_page, page_size)
                        print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
                        continue
                else:
                    print(f"请输入 1-{len(versions)} 之间的数字")
                    display_versions_page(versions, current_version, current_page, page_size)
                    print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
            else:
                print("请输入有效的选择")
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
                
        except KeyboardInterrupt:
            print("\n用户中断")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    check_node_updates()