import tkinter as tk
from tkinter import font
import time
 
# 创建窗口
root = tk.Tk()
root.title("透明数字时钟")
 
# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
 
# 设置窗口的初始大小和透明背景
root.geometry("360x120+{}+0".format(screen_width - 360))  # 将窗口放在右上角，宽度为360，高度为120
root.config(bg='black')  # 背景设为黑色，透明窗口的效果
root.overrideredirect(True)  # 去掉窗口的标题栏
root.attributes("-topmost", True)  # 确保窗口在最上层
root.attributes("-transparentcolor", "black")  # 设置透明背景颜色
 
# 设置初始字体
time_font = font.Font(family="Helvetica", size=96, weight="normal")
label = tk.Label(root, bg="black", fg="red", font=time_font)
label.pack(expand=True)
 
# 定义拖动窗口的函数
def on_press(event):
    """记录点击位置"""
    root.x = event.x
    root.y = event.y
 
def on_drag(event):
    """更新窗口位置"""
    deltax = event.x - root.x
    deltay = event.y - root.y
    root.geometry(f"+{root.winfo_x() + deltax}+{root.winfo_y() + deltay}")
 
# 绑定鼠标事件
root.bind("<Button-1>", on_press)  # 当鼠标按下时记录位置
root.bind("<B1-Motion>", on_drag)  # 当鼠标拖动时更新窗口位置
 
# 更新时钟的函数
def update_time():
    """更新时钟显示"""
    current_time = time.strftime("%H:%M:%S")  # 获取当前时间，格式为时:分:秒
    label.config(text=current_time)
    label.after(1000, update_time)  # 每秒更新一次
 
# 动态调整窗口大小的函数
def adjust_window_size():
    """调整窗口大小，以适应字体"""
    # 获取字体的大小
    font_size = time_font.cget("size")
    # 根据字体大小计算窗口的宽度和高度
    window_width = font_size * 6  # 假设宽度为字体大小的6倍
    window_height = font_size * 2  # 假设高度为字体大小的2倍
    # 调整窗口大小
    root.geometry(f"{window_width}x{window_height}+{screen_width - window_width - 20}+20")
 
# 放大字体
def increase_font_size():
    current_size = time_font.cget("size")
    new_size = current_size + 2  # 每次放大2个单位
    time_font.config(size=new_size)
    adjust_window_size()  # 调整窗口大小
    recreate_menu()  # 更新菜单显示
 
# 缩小字体
def decrease_font_size():
    current_size = time_font.cget("size")
    new_size = max(current_size - 2, 10)  # 每次缩小2个单位，最低为10
    time_font.config(size=new_size)
    adjust_window_size()  # 调整窗口大小
    recreate_menu()  # 更新菜单显示
 
# 关闭右键菜单
def close_menu(menu):
    menu.unpost()  # 隐藏菜单
 
# 创建右键菜单
def create_menu(event):
    """创建并显示菜单"""
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="放大字体", command=increase_font_size)  # 放大字体
    menu.add_command(label="缩小字体", command=decrease_font_size)  # 缩小字体
    menu.add_command(label="关闭右键菜单", command=lambda: close_menu(menu))  # 关闭右键菜单
    menu.add_command(label="关闭时钟", command=root.quit)  # 添加关闭时钟的选项
    menu.post(event.x_root, event.y_root)  # 在鼠标点击的位置弹出菜单
    return menu
 
# 重新创建菜单（在字体更新后调用）
def recreate_menu():
    """在字体更新后重新显示菜单"""
    if hasattr(recreate_menu, "current_menu"):
        recreate_menu.current_menu.unpost()  # 隐藏之前的菜单
    recreate_menu.current_menu = create_menu(recreate_menu.last_event)  # 创建新菜单
 
# 绑定右键点击事件，显示菜单
def on_right_click(event):
    """处理右键点击并弹出菜单"""
    recreate_menu.last_event = event  # 记录当前右键点击事件
    recreate_menu()  # 重新创建菜单
 
root.bind("<Button-3>", on_right_click)  # 右键点击时弹出菜单
 
# 启动时钟更新
update_time()
 
# 初始调整窗口大小
adjust_window_size()
 
# 使窗口透明并显示
root.mainloop()