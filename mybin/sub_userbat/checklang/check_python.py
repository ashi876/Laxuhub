#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import subprocess
import re
import platform
import os
import sys

def get_current_python_version():
    """获取当前安装的Python版本"""
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        version_output = result.stdout.strip()
        
        # 匹配版本号格式: Python 3.9.7, Python 3.10.11, 等
        pattern = r'Python (\d+\.\d+\.\d+)'
        match = re.search(pattern, version_output)
        
        if match:
            return match.group(1)
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def detect_system_info():
    """自动检测系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "linux":
        os_type = "linux"
    elif system == "darwin":
        os_type = "mac"
    elif system == "windows":
        os_type = "windows"
    else:
        os_type = system
    
    if machine in ["x86_64", "amd64"]:
        arch = "x64"
    elif machine in ["arm64", "aarch64"]:
        arch = "aarch64"
    else:
        arch = machine
    
    return os_type, arch

def get_github_releases():
    """从GitHub获取PythonInstallExtract的release信息"""
    try:
        url = "https://api.github.com/repos/ashi876/PythonInstallExtract/releases"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        all_versions = []
        
        for release in data:
            tag_name = release['tag_name']
            
            # 获取assets文件信息
            assets = []
            for asset in release['assets']:
                # 从文件名中提取Python版本号
                version_match = re.search(r'x64Python(\d+\.\d+\.\d+)\.7z', asset['name'])
                if version_match:
                    python_version = version_match.group(1)
                    
                    assets.append({
                        'name': asset['name'],
                        'python_version': python_version,
                        'url': asset['browser_download_url'],
                        'size': asset['size']
                    })
            
            # 为每个Python版本创建单独的条目
            for asset in assets:
                version_parts = asset['python_version'].split('.')
                major_version = int(version_parts[0])
                minor_version = int(version_parts[1])
                
                all_versions.append({
                    'version': asset['python_version'],
                    'major_version': major_version,
                    'minor_version': minor_version,
                    'tag_name': tag_name,
                    'date': release['published_at'][:10],
                    'asset': asset  # 直接关联对应的asset
                })
        
        # 按版本号排序（从高到低）
        all_versions.sort(key=lambda x: tuple(map(int, x['version'].split('.'))), reverse=True)
        return all_versions
    except Exception as e:
        print(f"获取Python releases失败: {e}")
        return []

def find_matching_asset(version_data, os_type, arch):
    """查找匹配系统架构的asset"""
    # 直接返回版本数据中关联的asset
    if 'asset' in version_data:
        asset = version_data['asset']
        print(f"✅ 找到Python {version_data['version']} 便携包: {asset['name']}")
        return asset
    
    return None

def download_file(url, filename):
    """下载文件"""
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
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False

def display_versions(versions, current_version, page, total_pages):
    """显示版本列表"""
    print(f"\nPython版本列表 (第 {page}/{total_pages} 页):")
    print("=" * 70)
    print(f"{'编号':<4} {'版本号':<15} {'发布日期':<12} {'备注':<20}")
    print("-" * 70)
    
    for i, ver in enumerate(versions, 1):
        # 检查是否为当前版本
        is_current = current_version and current_version == ver['version']
        marker = " ← 当前" if is_current else ""
        
        # 检查是否为最新版本（第一页的第一个）
        if i == 1 and page == 1:
            marker = " ← 最新" + (" (也是当前)" if is_current else "")
        elif is_current:
            marker = " ← 当前"
        
        # 添加版本备注
        note = ""
        if ver['major_version'] == 2:
            note = "Python 2 (旧版)"
        elif ver['major_version'] == 3:
            if ver['minor_version'] <= 6:
                note = "Python 3.0-3.6 (较旧)"
            elif ver['minor_version'] <= 10:
                note = "Python 3.7-3.10"
            else:
                note = "Python 3.11+ (最新)"
        
        print(f"{i:<4} {ver['version']:<14} {ver['date']:<12} {note:<20}{marker}")
    
    print("-" * 70)

def get_simple_input():
    """简化输入处理，只支持左右箭头和数字"""
    if sys.platform == "win32":
        import msvcrt
        try:
            key = msvcrt.getch()
            if key == b'\xe0':  # 扩展键
                key = msvcrt.getch()
                if key == b'K': return 'left'
                if key == b'M': return 'right'
            elif key in b'123456789':
                return key.decode()
            elif key == b'0': return '0'
            elif key in b'qQ': return 'quit'
        except:
            pass
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch = sys.stdin.read(1)
                if ch == '[':
                    ch = sys.stdin.read(1)
                    if ch == 'D': return 'left'
                    if ch == 'C': return 'right'
            elif ch in '1234567890': return ch
            elif ch in 'qQ': return 'quit'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

def check_python_updates():
    """检查Python版本更新"""
    print("检查Python版本更新...")
    print("数据来源: https://github.com/ashi876/PythonInstallExtract/releases")
    print("说明: 这些是便携版Python，解压即可使用")
    
    current_version = get_current_python_version()
    if current_version:
        print(f"当前Python版本: {current_version}")
    else:
        print("未找到Python或无法获取版本")
    
    versions = get_github_releases()
    if not versions:
        print("无法从GitHub获取版本列表")
        return
    
    # 去重，保留每个版本的最新发布
    unique_versions = {}
    for version in versions:
        ver_key = version['version']
        if ver_key not in unique_versions:
            unique_versions[ver_key] = version
    
    versions = list(unique_versions.values())
    versions.sort(key=lambda x: tuple(map(int, x['version'].split('.'))), reverse=True)
    
    page_size = 20
    total_pages = (len(versions) + page_size - 1) // page_size
    current_page = 1
    
    while True:
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_versions = versions[start_idx:end_idx]
        
        display_versions(page_versions, current_version, current_page, total_pages)
        
        if total_pages > 1:
            print(f"\n导航: ← 上一页 → 下一页 | 输入编号选择版本 (1-{len(page_versions)}) | q 退出")
        else:
            print(f"\n输入编号选择版本 (1-{len(page_versions)}) | q 退出")
        print("请选择: ", end="", flush=True)
        
        choice = get_simple_input()
        print()
        
        if choice == 'quit':
            print("退出")
            break
        elif choice == 'left' and total_pages > 1:
            current_page = current_page - 1 if current_page > 1 else total_pages
        elif choice == 'right' and total_pages > 1:
            current_page = current_page + 1 if current_page < total_pages else 1
        elif choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(page_versions):
                selected = page_versions[idx]
                os_type, arch = detect_system_info()
                print(f"系统: {os_type}, 架构: {arch}")
                print(f"选择的版本: Python {selected['version']}")
                
                asset = find_matching_asset(selected, os_type, arch)
                if asset:
                    print(f"\n文件信息:")
                    print(f"文件名: {asset['name']}")
                    print(f"文件大小: {asset['size']} bytes")
                    print(f"下载链接: {asset['url']}")
                    
                    confirm = input("\n确认下载? (y/n): ").lower()
                    if confirm in ['y', 'yes', '是']:
                        filename = asset['name']
                        if download_file(asset['url'], filename):
                            print(f"\n下载成功: {filename}")
                            print("\n使用说明:")
                            print("1. 解压下载的压缩包")
                            print("2. 进入解压后的目录")
                            print("3. 运行python.exe (Windows) 或 python (Linux/Mac)")
                            print("4. 如需使用pip，可能需要重置路径或使用uv包管理器")
                        break
                else:
                    print("\n未找到匹配的便携包")
                    print(f"请手动查看: https://github.com/ashi876/PythonInstallExtract/releases")
            else:
                print(f"编号无效，请输入 1-{len(page_versions)} 之间的数字")
        else:
            print("输入无效")

if __name__ == "__main__":
    check_python_updates()