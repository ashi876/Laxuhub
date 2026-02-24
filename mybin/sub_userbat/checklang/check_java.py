#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import json
import subprocess
import re
import platform
import os
import sys
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 创建不验证证书的SSL上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def get_current_java_version():
    """获取当前安装的Java版本"""
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        version_output = result.stderr
        
        patterns = [
            r'build\s+([\d\.]+\+\d+-LTS)',
            r'Temurin-([\d\.]+\+\d+)',
            r'openjdk\s+version\s+"([\d\.]+)',
            r'openjdk\s+([\d\.]+\+\d+)',
            r'version\s+"([\d\._]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, version_output)
            if match:
                version = match.group(1)
                if '+' in version and '-LTS' not in version:
                    version += '-LTS'
                return version
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

def make_request(url):
    """发送HTTP请求"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
        return response.read().decode('utf-8')

def fetch_version_info(major, lts_releases):
    """并发获取单个版本的信息"""
    try:
        asset_url = f"https://api.adoptium.net/v3/assets/latest/{major}/hotspot"
        asset_data = json.loads(make_request(asset_url))
        
        if not asset_data:
            return None
        
        first_item = asset_data[0]
        
        # 正确的版本号获取
        version_info = first_item.get('version', {})
        version_str = version_info.get('openjdk_version', '')
        
        if not version_str:
            version_str = version_info.get('semver', '')
        
        # 格式化版本号
        if version_str:
            if major in lts_releases and '-LTS' not in version_str:
                full_version = f"{version_str}-LTS"
            else:
                full_version = version_str
        else:
            full_version = f"JDK {major}"
        
        # 收集所有assets
        assets = []
        for item in asset_data:
            binary = item.get('binary', {})
            package = binary.get('package', {})
            if package:
                image_type = binary.get('image_type', '')
                if image_type == 'jdk' or image_type == 'jre':
                    assets.append({
                        'name': package.get('name', ''),
                        'url': package.get('link', ''),
                        'size': package.get('size', 0),
                        'os': binary.get('os', ''),
                        'arch': binary.get('architecture', ''),
                        'image_type': image_type
                    })
        
        # 发布日期
        release_date = first_item.get('release_date', '')[:10]
        if not release_date:
            release_date = first_item.get('timestamp', '')[:10]
        
        return {
            'version': full_version,
            'major_version': major,
            'lts': major in lts_releases,
            'lts_name': f'JDK {major}' if major in lts_releases else '',
            'date': release_date,
            'assets': assets,
            'tag_name': first_item.get('release_name', '')
        }
        
    except Exception as e:
        return {
            'version': f"JDK {major}",
            'major_version': major,
            'lts': major in lts_releases,
            'lts_name': f'JDK {major}' if major in lts_releases else '',
            'date': '',
            'assets': [],
            'tag_name': ''
        }

def get_java_versions():
    """从Adoptium API获取所有可用的Java版本"""
    print("正在从Adoptium API获取Java版本列表...")
    
    try:
        # 1. 先获取所有可用版本
        info_url = "https://api.adoptium.net/v3/info/available_releases"
        info_data = json.loads(make_request(info_url))
        
        available_releases = info_data.get('available_releases', [])
        lts_releases = set(info_data.get('available_lts_releases', []))
        
        print(f"找到 {len(available_releases)} 个Java版本")
        print("正在获取版本详细信息...")
        
        # 2. 并发获取每个版本的信息
        versions = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_major = {
                executor.submit(fetch_version_info, major, lts_releases): major 
                for major in available_releases
            }
            
            completed = 0
            total = len(available_releases)
            
            for future in as_completed(future_to_major):
                major = future_to_major[future]
                try:
                    result = future.result(timeout=10)
                    if result:
                        versions.append(result)
                    completed += 1
                    # 单行刷新进度
                    bar_length = 30
                    filled = int(bar_length * completed / total)
                    bar = '=' * filled + '-' * (bar_length - filled)
                    print(f"\r进度: [{bar}] {completed}/{total}", end='', flush=True)
                except Exception as e:
                    completed += 1
                    print(f"\nJDK {major} 处理失败: {e}")
        
        print("\n")  # 换行
        
        # 按主版本号从大到小排序
        versions.sort(key=lambda x: x['major_version'], reverse=True)
        print(f"成功获取 {len(versions)} 个Java版本")
        
        return versions
        
    except Exception as e:
        print(f"获取版本列表失败: {e}")
        return []

def find_matching_asset(assets, os_type, arch):
    """查找匹配系统架构的asset"""
    if not assets:
        return None
    
    # 优先找JDK，没有的话找JRE
    for image_type in ['jdk', 'jre']:
        for asset in assets:
            if asset.get('image_type') == image_type:
                if asset['os'] == os_type and asset['arch'] == arch:
                    return asset
    
    # 宽松匹配
    for asset in assets:
        if (asset['os'] == os_type and 
            asset['arch'] == arch and
            any(ext in asset['name'] for ext in ['.zip', '.tar.gz', '.msi', '.pkg'])):
            return asset
    
    return None

def download_file(url, filename):
    """下载文件 - 修复进度显示"""
    try:
        print(f"正在下载: {url}")
        print(f"保存到: {filename}")
        
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                # 修复：只显示百分比和已下载量，不重复显示total_size
                print(f"\r进度: {percent:.1f}% ({downloaded} / {total_size} bytes)", end="", flush=True)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            with open(filename, 'wb') as f:
                total_size = int(response.headers.get('Content-Length', 0))
                block_num = 0
                chunk_size = 8192
                
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    block_num += 1
                    report_progress(block_num, chunk_size, total_size)
        
        print("\n下载完成!")
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False

def display_versions(versions, current_version, page, total_pages):
    """显示版本列表"""
    print(f"\nJava版本列表 (第 {page}/{total_pages} 页):")
    print("=" * 80)
    print(f"{'编号':<4} {'版本号':<35} {'LTS状态':<15} {'发布日期':<12}")
    print("-" * 80)
    
    for i, ver in enumerate(versions, 1):
        version = ver['version']
        lts_status = f"LTS: {ver['lts_name']}" if ver['lts'] else "非LTS"
        
        markers = []
        if current_version and current_version.startswith(str(ver['major_version'])):
            markers.append("当前")
        if i == 1 and page == 1:
            markers.append("最新")
        marker_str = " <-" + ",".join(markers) if markers else ""
        
        date_str = ver['date'] if ver['date'] else "未知"
        
        print(f"{i:<4} {version:<35} {lts_status:<15} {date_str:<12}{marker_str}")
    
    print("-" * 80)

def get_simple_input():
    """简化输入处理"""
    if sys.platform == "win32":
        import msvcrt
        try:
            key = msvcrt.getch()
            if key == b'\xe0':
                key = msvcrt.getch()
                if key == b'K': return 'left'
                if key == b'M': return 'right'
            elif key in b'123456789':
                return key.decode()
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
            elif ch in '123456789': return ch
            elif ch in 'qQ': return 'quit'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

def check_java_updates():
    """检查Java版本更新"""
    print("检查Java版本更新...")
    
    current_version = get_current_java_version()
    if current_version:
        print(f"当前Java版本: {current_version}")
    else:
        print("未找到Java")
    
    versions = get_java_versions()
    if not versions:
        print("无法获取版本列表")
        input("\n按回车键退出...")
        return
    
    page_size = 20
    total_pages = (len(versions) + page_size - 1) // page_size
    current_page = 1
    
    while True:
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_versions = versions[start_idx:end_idx]
        
        display_versions(page_versions, current_version, current_page, total_pages)
        print("\n导航: 左箭头上一页 右箭头下一页 输入编号选择版本 q退出")
        print("请选择: ", end="", flush=True)
        
        choice = get_simple_input()
        print()
        
        if choice == 'quit':
            print("退出")
            break
        elif choice == 'left':
            current_page = current_page - 1 if current_page > 1 else total_pages
        elif choice == 'right':
            current_page = current_page + 1 if current_page < total_pages else 1
        elif choice and choice.isdigit():
            print(choice)  # 显示输入的数字
            idx = int(choice) - 1
            if 0 <= idx < len(page_versions):
                selected = page_versions[idx]
                os_type, arch = detect_system_info()
                print(f"系统: {os_type}, 架构: {arch}")
                
                if selected['assets']:
                    asset = find_matching_asset(selected['assets'], os_type, arch)
                    if asset:
                        print(f"\n找到匹配文件: {asset['name']}")
                        print(f"下载链接: {asset['url']}")
                        
                        confirm = input("\n确认下载? (y/n): ").lower()
                        if confirm in ['y', 'yes', '是']:
                            filename = asset['name']
                            if download_file(asset['url'], filename):
                                print(f"下载成功: {filename}")
                            break
                    else:
                        print("\n未找到匹配的安装包")
                        print(f"可用的平台: {set((a['os'], a['arch']) for a in selected['assets'])}")
                else:
                    print("\n该版本没有可用的下载文件")
            else:
                print("编号无效")
        else:
            print("输入无效")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    check_java_updates()