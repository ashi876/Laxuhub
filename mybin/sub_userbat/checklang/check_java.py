#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import subprocess
import re
import platform
import os
import sys

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

def get_github_releases(major_version):
    """从GitHub获取release信息"""
    try:
        url = f"https://api.github.com/repos/adoptium/temurin{major_version}-binaries/releases"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        versions = []
        for release in data:
            tag_name = release['tag_name']
            version_match = None
            
            # 适配不同版本的tag_name格式
            if major_version == 8:
                # JDK 8格式: jdk8u462-b08
                version_match = re.search(r'jdk8u(\d+)-b(\d+)', tag_name)
                if version_match:
                    update_version = version_match.group(1)  # 如462
                    build_number = version_match.group(2)    # 如08
                    full_version = f"1.8.0_{update_version}+b{build_number}"
            else:
                # JDK 11+ 格式: jdk-11.0.20+8
                version_match = re.search(r'jdk-([\d\.]+)\+(\d+)', tag_name)
                if version_match:
                    base_version = version_match.group(1)
                    build_number = version_match.group(2)
                    full_version = f"{base_version}+{build_number}-LTS"
            
            if version_match:
                # 获取assets文件信息
                assets = []
                for asset in release['assets']:
                    assets.append({
                        'name': asset['name'],
                        'url': asset['browser_download_url'],
                        'size': asset['size']
                    })
                
                versions.append({
                    'version': full_version,
                    'major_version': major_version,
                    'tag_name': tag_name,
                    'date': release['published_at'][:10],
                    'assets': assets
                })
        
        return versions
    except Exception as e:
        print(f"获取JDK {major_version} releases失败: {e}")
        return []

def get_java_versions():
    """获取所有可用的Java版本"""
    print("正在从GitHub获取Java版本列表...")
    
    versions = []
    lts_versions = [8, 11, 17, 21, 25]
    
    for major_version in lts_versions:
        print(f"获取JDK {major_version}版本...")
        releases = get_github_releases(major_version)
        if releases:
            # 只取最新版本
            latest_release = releases[0]
            versions.append({
                'version': latest_release['version'],
                'major_version': major_version,
                'lts': True,
                'lts_name': f'JDK {major_version}',
                'date': latest_release['date'],
                'assets': latest_release['assets'],
                'tag_name': latest_release['tag_name']
            })
            print(f"JDK {major_version}最新版本: {latest_release['version']}")
        else:
            print(f"JDK {major_version}无可用版本")
    
    # 按主版本号排序
    versions.sort(key=lambda x: x['major_version'], reverse=True)
    return versions

def find_matching_asset(assets, os_type, arch):
    """查找匹配系统架构的asset"""
    # 优先匹配的文件命名模式 - 按优先级排序
    priority_patterns = [
        # 最高优先级: 标准JDK安装包 (非debugimage)
        {
            'windows': {
                'x64': r'OpenJDK\d+U-jdk_x64_windows_hotspot_[\da-zA-Z]+\.zip',
                'aarch64': r'OpenJDK\d+U-jdk_aarch64_windows_hotspot_[\da-zA-Z]+\.zip'
            },        
            'mac': {
                'x64': r'OpenJDK\d+U-jdk_x64_mac_hotspot_[\da-zA-Z]+\.tar\.gz',
                'aarch64': r'OpenJDK\d+U-jdk_aarch64_mac_hotspot_[\da-zA-Z]+\.tar\.gz'
            },
            'linux': {
                'x64': r'OpenJDK\d+U-jdk_x64_linux_hotspot_[\da-zA-Z]+\.tar\.gz',
                'aarch64': r'OpenJDK\d+U-jdk_aarch64_linux_hotspot_[\da-zA-Z]+\.tar\.gz'
            }
        }
    ]
    
    # 排除debugimage、sources、debug等非标准安装包
    exclude_patterns = [
        r'debugimage', r'sources', r'debug', r'sbom', 
        r'json', r'sha256', r'sig', r'metadata', r'aqavit'
    ]
    
    # 按优先级查找匹配的asset
    for priority_set in priority_patterns:
        if os_type in priority_set and arch in priority_set[os_type]:
            pattern = priority_set[os_type][arch]
            for asset in assets:
                # 排除非安装包文件
                if any(exclude in asset['name'].lower() for exclude in exclude_patterns):
                    continue
                    
                if re.search(pattern, asset['name'], re.IGNORECASE):
                    print(f"✅ 找到JDK安装包: {asset['name']}")
                    return asset
    
    # 如果上面的匹配失败，尝试更宽松的匹配
    print("尝试宽松匹配...")
    for asset in assets:
        # 排除非安装包文件
        if any(exclude in asset['name'].lower() for exclude in exclude_patterns):
            continue
            
        # 宽松匹配：包含jdk、windows、x64/hotspot，且是压缩包或安装包
        if ('jdk' in asset['name'].lower() and 
            'windows' in asset['name'].lower() and 
            ('x64' in asset['name'].lower() or 'x86_64' in asset['name'].lower()) and
            any(ext in asset['name'].lower() for ext in ['.zip', '.tar.gz'])):
            print(f"✅ 通过宽松匹配找到JDK安装包: {asset['name']}")
            return asset
    
    # 如果还找不到，显示相关文件
    print("未找到标准JDK安装包，相关文件列表:")
    relevant_files = []
    for asset in assets:
        if any(exclude in asset['name'].lower() for exclude in exclude_patterns):
            continue
            
        if ('windows' in asset['name'].lower() and
            ('x64' in asset['name'].lower() or 'x86_64' in asset['name'].lower())):
            relevant_files.append(asset)
    
    if relevant_files:
        for i, asset in enumerate(relevant_files[:10], 1):
            file_type = "JDK" if "jdk" in asset['name'].lower() else "JRE" if "jre" in asset['name'].lower() else "其他"
            print(f"  {i}. [{file_type}] {asset['name']}")
        
        # 自动选择第一个JDK文件
        for asset in relevant_files:
            if "jdk" in asset['name'].lower():
                print(f"✅ 自动选择JDK安装包: {asset['name']}")
                return asset
        
        # 如果没有JDK，选择第一个文件
        if relevant_files:
            print(f"✅ 自动选择: {relevant_files[0]['name']}")
            return relevant_files[0]
    
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
                print(f"\r进度: {percent:.1f}% ({downloaded}/{total_size})", end="", flush=True)
        
        urllib.request.urlretrieve(url, filename, report_progress)
        print("\n下载完成!")
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False

def display_versions(versions, current_version, page, total_pages):
    """显示版本列表"""
    print(f"\nJava版本列表 (第 {page}/{total_pages} 页):")
    print("=" * 60)
    print(f"{'编号':<4} {'版本号':<20} {'发布日期':<12}")
    print("-" * 60)
    
    for i, ver in enumerate(versions, 1):
        marker = " ← 当前" if current_version and current_version.startswith(str(ver['major_version'])) else ""
        if i == 1 and page == 1:
            marker = " ← 最新" + marker.replace("←", "")
        print(f"{i:<4} {ver['version']:<19} {ver['date']:<12}{marker}")
    
    print("-" * 60)

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
        return
    
    page_size = 20
    total_pages = (len(versions) + page_size - 1) // page_size
    current_page = 1
    
    while True:
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_versions = versions[start_idx:end_idx]
        
        display_versions(page_versions, current_version, current_page, total_pages)
        print("\n导航: ← 上一页 → 下一页 | 输入编号选择版本 | q 退出")
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
            idx = int(choice) - 1
            if 0 <= idx < len(page_versions):
                selected = page_versions[idx]
                os_type, arch = detect_system_info()
                print(f"系统: {os_type}, 架构: {arch}")
                
                # 显示所有可用的assets用于调试
                print(f"可用文件列表:")
                for i, asset in enumerate(selected['assets'][:10], 1):  # 只显示前10个
                    print(f"  {i}. {asset['name']} ({asset['size']} bytes)")
                
                asset = find_matching_asset(selected['assets'], os_type, arch)
                if asset:
                    print(f"\n找到匹配文件: {asset['name']}")
                    print(f"文件大小: {asset['size']} bytes")
                    print(f"下载链接: {asset['url']}")
                    
                    confirm = input("\n确认下载? (y/n): ").lower()
                    if confirm in ['y', 'yes', '是']:
                        filename = asset['name']
                        if download_file(asset['url'], filename):
                            print(f"下载成功: {filename}")
                        break
                else:
                    print("\n未找到匹配的安装包")
                    print(f"请手动下载: https://github.com/adoptium/temurin{selected['major_version']}-binaries/releases")
            else:
                print("编号无效")
        else:
            print("输入无效")

if __name__ == "__main__":
    check_java_updates()