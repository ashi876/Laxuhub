#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import subprocess
import platform
import os
import sys
import time

def get_current_go_version():
    """获取当前安装的Go版本"""
    try:
        result = subprocess.run(['go', 'version'], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        # 解析 "go version go1.21.6 windows/amd64" 格式
        parts = output.split()
        if len(parts) >= 3 and parts[2].startswith('go'):
            version = parts[2][2:]  # 去掉"go"前缀
            return version
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def detect_system_info():
    """自动检测系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 映射系统名称（与Go官方命名一致）
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
    elif machine.startswith("armv6"):
        arch = "armv6l"
    elif machine == "i386" or machine == "i686":
        arch = "386"
    else:
        arch = machine
    
    return os_type, arch

def get_go_versions():
    """从官方API获取可用的Go版本列表"""
    try:
        print("正在从官方API获取Go版本列表...")
        api_url = "https://go.dev/dl/?mode=json"
        
        req = urllib.request.Request(
            api_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        version_list = []
        for item in data:
            version = item['version'][2:]  # 去掉"go"前缀，如 "go1.26.0" → "1.26.0"
            version_list.append({
                'version': version,
                'stable': item.get('stable', True),
                'files': item['files']  # 保存文件列表供下载使用
            })
        
        return version_list
    except Exception as e:
        print(f"获取版本列表失败: {e}")
        return []

def find_download_url(version_info, os_type, arch):
    """从files数组中查找匹配的下载链接"""
    files = version_info['files']
    
    # 优先查找 archive 类型的文件（绿色压缩包）
    for file in files:
        if (file['os'] == os_type and 
            file['arch'] == arch and 
            file['kind'] == 'archive'):
            return f"https://go.dev/dl/{file['filename']}"
    
    # 如果没有找到archive，尝试installer类型
    for file in files:
        if (file['os'] == os_type and 
            file['arch'] == arch and 
            file['kind'] == 'installer'):
            return f"https://go.dev/dl/{file['filename']}"
    
    return None

def download_file(url, download_path="."):
    """下载文件并显示进度"""
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

def display_versions_page(versions, current_version, page=1, page_size=20):
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
        marker_str = " <-" + ",".join(markers) if markers else ""
        
        print(f"{i:<6} v{version:<14} {stable_status:<10}{marker_str}")
    
    print("-" * 80)
    return total_pages

def get_arrow_input():
    """获取包含方向键的输入（跨平台）"""
    if sys.platform == "win32":
        import msvcrt
        key = msvcrt.getch()
        if key == b'\xe0':  # 扩展键
            key = msvcrt.getch()
            if key == b'K': return 'left'
            if key == b'M': return 'right'
        elif key == b'\r': return 'enter'
        elif key in (b'q', b'Q'): return 'quit'
        elif key.isdigit(): return key.decode()
    else:
        import termios
        import tty
        import select
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch = sys.stdin.read(1)
                    if ch == '[':
                        ch = sys.stdin.read(1)
                        if ch == 'D': return 'left'
                        if ch == 'C': return 'right'
                elif ch in ('\r', '\n'): return 'enter'
                elif ch in ('q', 'Q'): return 'quit'
                elif ch.isdigit(): return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

def check_go_updates():
    """检查Go版本更新并提供下载选项"""
    print("\n检查Go版本更新...")
    print("=" * 50)
    
    # 获取当前版本
    current_version = get_current_go_version()
    if current_version:
        print(f"当前Go版本: v{current_version}")
    else:
        print("未找到Go编译器")
    
    # 获取版本列表
    versions = get_go_versions()
    if not versions:
        print("无法获取版本列表，请检查网络连接")
        input("\n按回车键退出...")
        return
    
    # 分页显示
    page_size = 20
    current_page = 1
    total_pages = display_versions_page(versions, current_version, current_page, page_size)
    
    # 检查更新
    if current_version and versions:
        latest_version = versions[0]['version']
        if current_version != latest_version:
            print(f"\n有更新可用! 当前: v{current_version}, 最新: v{latest_version}")
    
    print(f"\n导航: 左箭头上一页 右箭头下一页 输入编号选择版本 q退出")
    
    # 交互循环
    while True:
        try:
            print("\n请选择: ", end='', flush=True)
            choice = get_arrow_input()
            
            if choice == 'quit':
                print("\n退出")
                break
            elif choice == 'left':
                current_page = current_page - 1 if current_page > 1 else total_pages
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: 左箭头上一页 右箭头下一页 输入编号选择版本 q退出")
            elif choice == 'right':
                current_page = current_page + 1 if current_page < total_pages else 1
                display_versions_page(versions, current_version, current_page, page_size)
                print(f"\n导航: 左箭头上一页 右箭头下一页 输入编号选择版本 q退出")
            elif choice and choice.isdigit():
                # 处理多位数输入
                number = choice
                print(number, end='', flush=True)
                
                # 等待更多数字输入
                if sys.platform == "win32":
                    import msvcrt
                    import time
                    start = time.time()
                    while time.time() - start < 1.0:
                        if msvcrt.kbhit():
                            nxt = msvcrt.getch()
                            if nxt.isdigit():
                                number += nxt.decode()
                                print(nxt.decode(), end='', flush=True)
                                start = time.time()
                            else:
                                break
                        time.sleep(0.05)
                
                print()
                idx = int(number) - 1
                
                if 0 <= idx < len(versions):
                    selected = versions[idx]
                    
                    # 检测系统
                    os_type, arch = detect_system_info()
                    print(f"\n检测到系统: {os_type}, 架构: {arch}")
                    
                    # 查找下载链接
                    download_url = find_download_url(selected, os_type, arch)
                    
                    if download_url:
                        print(f"版本: v{selected['version']}")
                        print(f"下载链接: {download_url}")
                        
                        confirm = input(f"\n确认下载 v{selected['version']}? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes', '是']:
                            filename = download_file(download_url)
                            if filename:
                                print(f"\n下载成功: {filename}")
                                print("请手动解压并安装到合适的位置")
                            break
                        else:
                            print("取消下载")
                            display_versions_page(versions, current_version, current_page, page_size)
                            print(f"\n导航: 左箭头上一页 右箭头下一页 输入编号选择版本 q退出")
                    else:
                        print(f"\n未找到适用于 {os_type}/{arch} 的下载包")
                        print("可用的平台:", set((f['os'], f['arch']) for f in selected['files']))
                else:
                    print(f"请输入 1-{len(versions)} 之间的数字")
            else:
                print("无效输入")
                
        except KeyboardInterrupt:
            print("\n\n用户中断")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    check_go_updates()