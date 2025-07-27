# -*- coding: utf-8 -*-
import Tkinter as tk
import tkFont
import time

# 创建窗口
root = tk.Tk()
root.title(u"透明数字时钟")

# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 设置窗口的初始大小和透明背景
root.geometry("360x120+%d+0" % (screen_width - 360))  # 将窗口放在右上角
root.config(bg='black')  # 背景设为黑色
root.overrideredirect(True)  # 去掉窗口的标题栏
root.attributes("-topmost", True)  # 确保窗口在最上层
root.attributes("-transparentcolor", "black")  # 设置透明背景颜色

# 设置初始字体
time_font = tkFont.Font(family="Helvetica", size=96, weight="normal")
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
    root.geometry("+%d+%d" % (root.winfo_x() + deltax, root.winfo_y() + deltay))

# 绑定鼠标事件
root.bind("<Button-1>", on_press)  # 鼠标按下事件
root.bind("<B1-Motion>", on_drag)  # 鼠标拖动事件

# 更新时钟的函数
def update_time():
    """更新时钟显示"""
    current_time = time.strftime("%H:%M:%S")  # 获取当前时间
    label.config(text=current_time)
    label.after(1000, update_time)  # 每秒更新一次

# 动态调整窗口大小的函数
def adjust_window_size():
    """调整窗口大小，以适应字体"""
    font_size = time_font.cget("size")
    window_width = font_size * 6
    window_height = font_size * 2
    root.geometry("%dx%d+%d+%d" % (
        window_width, 
        window_height,
        screen_width - window_width - 20,
        20
    ))

# 字体调整函数
def increase_font_size():
    current_size = time_font.cget("size")
    new_size = current_size + 2
    time_font.configure(size=new_size)
    adjust_window_size()
    recreate_menu()

def decrease_font_size():
    current_size = time_font.cget("size")
    new_size = max(current_size - 2, 10)
    time_font.configure(size=new_size)
    adjust_window_size()
    recreate_menu()

# 右键菜单功能
def close_menu(menu):
    menu.unpost()

def create_menu(event):
    """创建并显示菜单"""
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label=u"放大字体", command=increase_font_size)
    menu.add_command(label=u"缩小字体", command=decrease_font_size)
    menu.add_command(label=u"关闭右键菜单", command=lambda: close_menu(menu))
    menu.add_command(label=u"关闭时钟", command=root.quit)
    menu.post(event.x_root, event.y_root)
    return menu

def recreate_menu():
    """在字体更新后重新显示菜单"""
    if hasattr(recreate_menu, "current_menu"):
        recreate_menu.current_menu.unpost()
    # 确保有last_event属性
    if hasattr(recreate_menu, "last_event"):
        recreate_menu.current_menu = create_menu(recreate_menu.last_event)

def on_right_click(event):
    """处理右键点击并弹出菜单"""
    recreate_menu.last_event = event
    recreate_menu()

root.bind("<Button-3>", on_right_click)  # 绑定右键事件

# 启动时钟更新
update_time()

# 初始调整窗口大小
adjust_window_size()

# 使窗口透明并显示
root.mainloop()