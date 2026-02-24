#!/usr/bin/env python3
"""
Python 预编译版本下载器 for Windows
使用 Python 标准库，无需安装额外依赖
按原版 mise 顺序排序：3.8 → 3.9 → 3.10 → 3.11 → 3.12 → 3.13 → 3.14 → 3.15
每个大版本内按版本号升序（旧到新）
"""

import urllib.request
import urllib.error
import gzip
import re
import os
import ssl
from typing import List, Tuple, Dict
from collections import defaultdict

# 配置
INDEX_URL = "https://mise-versions.jdx.dev/tools/python-precompiled-x86_64-pc-windows-msvc.gz"
TIMEOUT = 30

# 处理 SSL 证书问题（Windows 上有时需要）
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def get_version_list() -> List[Tuple[str, str, str]]:
    """获取并解析版本列表，每个版本只保留最新日期的构建"""
    print(f"正在获取版本列表...")
    
    try:
        # 创建请求对象
        req = urllib.request.Request(
            INDEX_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        # 下载 gz 文件
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl_context) as response:
            compressed_data = response.read()
        
        # 解压
        content = gzip.decompress(compressed_data).decode('utf-8')
        
        # 按版本号分组收集所有构建
        version_groups = defaultdict(list)
        pattern = r'^cpython-(\d+\.\d+\.\d+[a-z]*)\+(\d+)-x86_64-pc-windows-msvc(.*)\.tar\.gz$'
        
        for line in content.strip().split('\n'):
            match = re.match(pattern, line)
            if match:
                version = match.group(1)      # 3.13.5
                date = match.group(2)         # 20250723
                suffix = match.group(3)       # -install_only_stripped 等
                filename = f"cpython-{version}+{date}-x86_64-pc-windows-msvc{suffix}.tar.gz"
                
                # 按版本分组收集
                version_groups[version].append((version, date, filename))
        
        # 对每个版本，只保留日期最新的那个
        latest_versions = []
        for version, builds in version_groups.items():
            # 按日期排序，取最新的
            latest_build = max(builds, key=lambda x: x[1])  # x[1] 是日期字符串
            latest_versions.append(latest_build)
        
        if not latest_versions:
            print("警告: 没有解析到任何版本，可能格式已变更")
            print("前5行原始数据:")
            for line in content.strip().split('\n')[:5]:
                print(f"  {line}")
        
        print(f"成功获取 {len(latest_versions)} 个版本（每个版本仅保留最新构建）")
        return latest_versions
    
    except urllib.error.URLError as e:
        print(f"网络连接失败: {e}")
        return []
    except Exception as e:
        print(f"获取版本列表失败: {e}")
        return []

def sort_versions(versions: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    """按原版 mise 顺序排序：3.8 → 3.9 → 3.10 → 3.11 → 3.12 → 3.13 → 3.14 → 3.15，每个大版本内按版本号升序"""
    
    # 按大版本分组
    major_groups = defaultdict(list)
    for v in versions:
        # 提取大版本号 (3.8, 3.9, 3.10, ...)
        major_parts = v[0].split('.')
        if len(major_parts) >= 2:
            major = f"{major_parts[0]}.{major_parts[1]}"
            major_groups[major].append(v)
    
    # 大版本顺序列表
    major_order = ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13', '3.14', '3.15']
    
    # 按顺序重组
    sorted_versions = []
    for major in major_order:
        if major in major_groups:
            # 每个大版本内按版本号升序排序
            # 需要将版本字符串转换为可比较的元组
            def version_key(v):
                parts = v[0].split('.')
                # 处理可能存在的字母后缀（如 3.13.0rc3）
                main_parts = []
                suffix = ''
                for p in parts:
                    match = re.match(r'^(\d+)([a-z]+\d*)?$', p)
                    if match:
                        main_parts.append(int(match.group(1)))
                        if match.group(2):
                            suffix = match.group(2)
                    else:
                        main_parts.append(0)
                # 补足到3个数字部分
                while len(main_parts) < 3:
                    main_parts.append(0)
                return (main_parts[0], main_parts[1], main_parts[2], suffix)
            
            sorted_group = sorted(major_groups[major], key=version_key)
            sorted_versions.extend(sorted_group)
    
    return sorted_versions

def group_by_major(versions: List[Tuple[str, str, str]]) -> Dict[str, List[Tuple[str, str, str]]]:
    """按大版本分组 (3.13, 3.12, ...)"""
    groups = defaultdict(list)
    for v in versions:
        # 提取大版本号 (3.13)
        major = '.'.join(v[0].split('.')[:2])
        groups[major].append(v)
    return groups

def get_latest_of_each_major(versions: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    """获取每个大版本的最新版本"""
    groups = group_by_major(versions)
    latest = []
    
    # 大版本顺序
    major_order = ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13', '3.14', '3.15']
    
    for major in major_order:
        if major in groups:
            # 每个大版本内按版本号升序，取最后一个（最新的）
            def version_key(v):
                parts = v[0].split('.')
                main_parts = []
                for p in parts:
                    match = re.match(r'^(\d+)', p)
                    if match:
                        main_parts.append(int(match.group(1)))
                    else:
                        main_parts.append(0)
                while len(main_parts) < 3:
                    main_parts.append(0)
                return (main_parts[0], main_parts[1], main_parts[2])
            
            sorted_group = sorted(groups[major], key=version_key)
            latest.append(sorted_group[-1])  # 取最后一个（最新）
    
    return latest

def display_versions(versions: List[Tuple[str, str, str]], show_all: bool = False):
    """显示版本列表"""
    print("\nPython 版本列表:")
    
    if show_all:
        # 显示所有版本（按原版顺序）
        for i, (ver, date, _) in enumerate(versions, 1):
            print(f"{i:3}. Python {ver} ({date})")
        print(f"\n总共 {len(versions)} 个版本")
    else:
        # 只显示每个大版本的最新版本
        latest = get_latest_of_each_major(versions)
        for i, (ver, date, _) in enumerate(latest, 1):
            print(f"{i:3}. Python {ver} (最新, {date})")
        
        print(f"\n{'='*50}")
        print("提示: 输入 'a' 查看所有历史小版本")

def download_file(url: str, filename: str):
    """下载文件并显示进度"""
    print(f"\n开始下载: {filename}")
    
    try:
        # 创建请求对象
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        # 下载文件
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl_context) as response:
            # 获取文件大小
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(filename, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 显示进度
                    if total_size > 0:
                        percent = downloaded * 100 / total_size
                        print(f"\r进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
        
        print(f"\n下载完成: {filename}")
        print(f"保存位置: {os.path.abspath(filename)}")
        return True
        
    except urllib.error.HTTPError as e:
        print(f"\nHTTP错误 {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"\n网络错误: {e.reason}")
        return False
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False

def main():
    print("Python 预编译版本下载器 (for Windows)")
    print("=" * 50)
    
    # 获取版本列表
    all_versions = get_version_list()
    if not all_versions:
        print("没有获取到任何版本，退出")
        input("按回车键退出...")
        return
    
    # 按原版顺序排序
    all_versions = sort_versions(all_versions)
    
    # 交互循环
    show_all = False
    while True:
        display_versions(all_versions, show_all)
        
        choice = input("\n请输入编号 (或 'a' 切换显示模式, 'q' 退出): ").strip()
        
        if choice.lower() == 'q':
            print("退出")
            break
        
        elif choice.lower() == 'a':
            show_all = not show_all
            continue
        
        try:
            idx = int(choice) - 1
            
            # 根据当前显示模式获取对应的版本列表
            if show_all:
                selected_versions = all_versions
            else:
                selected_versions = get_latest_of_each_major(all_versions)
            
            if 0 <= idx < len(selected_versions):
                ver, date, filename = selected_versions[idx]
                
                # 构建下载 URL
                download_url = f"https://github.com/astral-sh/python-build-standalone/releases/download/{date}/{filename}"
                
                # 确认下载
                confirm = input(f"\n确认下载 Python {ver}? (y/n): ").strip().lower()
                if confirm == 'y':
                    download_file(download_url, filename)
                else:
                    print("取消下载")
                
                # 下载完成后询问是否继续
                cont = input("\n是否继续选择? (y/n): ").strip().lower()
                if cont != 'y':
                    print("退出")
                    break
            else:
                print("无效编号，请重新输入")
                
        except ValueError:
            print("请输入有效的数字编号")
    
    input("按回车键退出...")

if __name__ == "__main__":
    main()