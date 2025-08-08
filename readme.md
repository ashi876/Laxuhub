### PortablePythonHub 使用指南  
（win平台绿色 Python 多版本集合包）
 https://github.com/ashi876/PortablePythonHub
 作者:千城真人 b站_碎辰

#### **核心功能**  
通过 `runall.bat` 自动检测并管理多个绿色版 Python 环境，实现：  
- 多版本 Python 隔离切换  
- 一键配置环境变量  
- 集成常用工具（pip/clink/虚拟环境等）

---

#### **目录结构说明**

	├── PythonXXX\        # 绿色版 Python 主程序 (官网提取x64版，仅含 pip+tcl)
	├── mybin\            # 扩展工具集
	│   ├── pip重置.bat        # 修复 pip 路径
	│   ├── pip安全更新.bat     # 通过 get-pip.py 安全更新
	│   ├── clink\         # CMD 增强工具 (历史记录/补全/复制粘贴)
	│   ├── gsudo.exe      # 脚本提权工具
	│   └── upx.exe        # PyInstaller 压缩工具
	├── py\               # 测试脚本目录
	│   └── Python库批量安装.py  # 一键安装常用库
	└── runall.bat         # 主入口脚本 (本文档解析对象)

使用流程
第一步：初始化环境

    双击运行 runall.bat
        自动扫描 Python* 目录（如 Python38, Python310）单个版本时直接进入
        多版本时显示选择菜单：

     检测到的Python目录列表：
     [1] Python38
     [2] Python310
     请输入要使用的Python目录编号(1-2)：
	 
第二步：首次运行必做

    重要提示：首次运行需在 runall.bat 窗口内执行：
    pip重置.bat    # 修复绿色版 pip 功能
  

第三步：常用操作

    命令	作用	示例
    cd /d %mypy%	进入脚本目录 .\py\	运行 Python库批量安装.py
    cd /d %mydesk%	跳转桌面目录	快速访问桌面文件
    myenv.bat [名称]	创建虚拟环境 (默认 myenv)	myenv.bat django_project
    pip安全更新.bat	安全升级 pip	解决旧版本兼容问题

错误处理方案

    现象	解决方案
    未找到Python目录	确认存在 PythonXXX 文件夹
    pip 不可用	首次运行必须执行 pip重置.bat
    python.exe 缺失	检查 Python 目录完整性
    路径含中文/空格	移动项目到纯英文路径

进阶技巧

    自定义工具集成
    将任何 .exe 或脚本放入 mybin\，重启 runall.bat 后可直接调用
