import psutil
import time
import os
import platform
import subprocess
import re

def get_cpu_model():
    """获取CPU型号（适用于Windows系统）"""
    try:
        # 方法1：使用注册表查询
        cmd = 'reg query "HKLM\\HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0" /v ProcessorNameString'
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        match = re.search(r"ProcessorNameString\s+REG_SZ\s+(.+)", result)
        if match:
            return match.group(1).strip()
        
        # 方法2：回退到wmi模块
        try:
            import wmi
            c = wmi.WMI()
            return c.Win32_Processor()[0].Name.strip()
        except ImportError:
            pass
    
    except:
        pass
    
    # 最终回退方案
    try:
        return platform.processor() or "未知CPU型号"
    except:
        return "未知CPU型号"

def display_all_cores_usage():
    """实时显示所有逻辑核心的占用率"""
    # 获取CPU型号
    cpu_model = get_cpu_model()
    
    # 获取逻辑核心数量
    logical_cores = psutil.cpu_count(logical=True)
    
    try:
        # 清屏并打印标题
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        print(f"{cpu_model} 核心占用率监控:")
        print(f"逻辑核心数量: {logical_cores}")
        print("按 Ctrl+C 退出监控")
        print("-" * 60)
        
        # 初始化历史数据用于计算趋势
        prev_usage = [0] * logical_cores
        trends = ["→"] * logical_cores
        
        while True:
            # 获取所有核心的当前占用率
            current_usage = psutil.cpu_percent(interval=0.5, percpu=True)
            
            # 获取内存信息
            mem = psutil.virtual_memory()
            used_mem_gb = mem.used / (1024 ** 3)  # 转换为GB
            total_mem_gb = mem.total / (1024 ** 3)
            mem_percent = mem.percent
            
            # 清屏并重置光标位置
            print("\033[H", end="")  # 光标移动到左上角
            
            # 打印标题和分隔线
            print(f"{cpu_model} 核心占用率监控:")
            print(f"逻辑核心数量: {logical_cores}   [刷新间隔: 0.5秒]")
            print("按 Ctrl+C 退出监控")
            print("-" * 60)
            
            # 计算趋势箭头
            for i in range(logical_cores):
                if current_usage[i] > prev_usage[i] + 1:
                    trends[i] = "↑"  # 上升
                elif current_usage[i] < prev_usage[i] - 1:
                    trends[i] = "↓"  # 下降
                else:
                    trends[i] = "→"  # 稳定
                prev_usage[i] = current_usage[i]
            
            # 显示每个核心的占用情况
            for i in range(logical_cores):
                usage = current_usage[i]
                
                # 构建进度条和颜色
                bar_length = 40
                filled_length = int(bar_length * usage / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                # 根据负载设置颜色
                if usage > 80:
                    color_code = "\033[91m"  # 红色 (高负载)
                elif usage > 50:
                    color_code = "\033[93m"  # 黄色 (中等负载)
                else:
                    color_code = "\033[92m"  # 绿色 (低负载)
                
                # 打印核心状态
                print(f"核心 {i:2d} {trends[i]}: {color_code}{bar}\033[0m {usage:6.1f}%")
            
            # 打印总体CPU使用率和内存信息
            total_usage = psutil.cpu_percent()
            print("\n" + "-" * 60)
            print(f"总体CPU使用率: \033[94m{total_usage:.1f}%\033[0m")
            print(f"内存占用: \033[95m{used_mem_gb:.1f}/{total_mem_gb:.1f} GB ({mem_percent:.1f}%)\033[0m")
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")

if __name__ == "__main__":
    display_all_cores_usage()