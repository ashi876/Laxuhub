LaxuHub 使用说明 

功能：快速切换和管理多版本开发环境（Python/Node.js/Go/Java/Rust等） 

基本用法 

	交互模式（首次推荐） 
		LaxuHub.exe 
	静默模式（使用上次配置） 
		LaxuHub.exe -q 
	指定工作目录启动 
		LaxuHub.exe "D:\MyProject" 

操作流程 

	首次运行： 
	进入交互选择界面
	输入环境编号（可多选，空格分隔）
	示例：1 3 5（选择第1、3、5个环境）后回车

后续使用： 

	默认显示上次配置选项
	回车确认使用上次配置
	输入 N 重新选择环境
	用LaxuHub.exe -q 静默模式直接进入上次配置

目录结构 

	LaxuHub/ 
	├── LaxuHub.exe # 主程序 
	├── green_dir.json # 环境配置（必需） 
	├── mybin/ # 工具目录 
	│ ├── cn_mirror.bat # 镜像源设置脚本 
	│ └── sub_*/ # 工具子目录（如sub_clink） 
	└── green_*/ # 环境目录（按语言命名） 
	├── green_python/ # Python环境 
	│ ├── python3.9/ # Python 3.9版本 
	│ ├── python3.10/ # Python 3.10版本 
	│ └── python3.11/ # Python 3.11版本 
	├── green_node/ # Node.js环境 
	│ ├── node16/ # Node.js 16版本 
	│ └── node18/ # Node.js 18版本 
	├── green_go/ # Go环境 
	├── green_java/ # Java环境 
	└── green_rust/ # Rust环境 

环境目录命名规则 

语言目录格式：

	green_{语言名}（如 green_python, green_node）
		示例：green_python/, green_node/
		
	版本目录： 
		必须包含语言名前缀（符合配置中的 version_pattern）
		
	示例格式：
		green_python/ 
			├── python3.9/ # 符合 "python*" 模式 
			├── python-3.10/ # 符合 "python*" 模式 
			└── python_3.11/ # 符合 "python*" 模式 注意LaxuHub.bat模式对下划线敏感（系统的锅）
	错误示例（不会被识别）：
		green_python/ 
			├── 3.9/ # ❌ 缺少语言前缀 
			└── v3.10/ # ❌ 不符合 "python*" 模式 

用户可定义用于扩展新语言留下的三重接口:

	green_dir.json + green_XX 目录：
		
		作用：定义如何集成一个复杂的、需要特殊环境变量和路径设置的正式语言环境（如 Python, Java, Go）。
		扩展方式：任何新语言，只要遵循在 json 中定义配置、在对应 green_xxx 目录下放置发行版的规则，就能被自动识别和集成。
		
	mybin目录及sub_ 子目录*：： 
	
		存放全局工具和脚本
		自动添加到PATH最前，确保工具优先级
		支持子目录扩展（通过 sub_* 命名）
		sub_ 子目录*： 
		存放特定工具集（如 sub_clink 存放Clink增强工具）
		自动扫描并添加到PATH
		示例： 
		mybin/ 
		├── sub_clink/ # Clink命令行增强 
		├── sub_git/ # Git工具集 
		└── sub_utils/ # 通用工具
	
	sub_clink目录下的clink_start.cmd，运行时环境个性化协议

		作用：在核心环境变量设置完成后，提供一个最后的钩子 (Hook)，允许用户执行任意bat命令（call 其他脚本）或设置临时、会话特有的环境变量（set）。
		扩展方式：用户可以用它来做任何事情：启动后台服务、设置项目特有的变量、连接网络驱动器、定义别名（alias）等。
	
	其它设置:
	cn_mirror.bat： 
	
		自动配置国内镜像源
		支持常见包管理器（pip/npm/go等）
		启动时自动执行，显著提升包下载速度
		位置：mybin/cn_mirror.bat

主环境配置 

	配置文件：green_dir.json（程序自带，按需添加环境）
	添加新环境：参考已有格式添加新语言配置
	配置包含：
		基础目录（如 green_python）
		PATH子目录（如 ["", "Scripts"]）
		环境变量（如 PYTHON_HOME）
		版本匹配模式（如 "python"）匹配green_python目录内"python"开头的子目录
	
特性 

	✅ 多环境任意组合同时激活（PATH/环境变量自动合并）
	✅ 防重复选择（同一语言只选一个版本）
	✅ 镜像源自动配置（通过cn_mirror.bat）
	✅ 语言环境目录自由扩展（通过green_dir.json）
	✅ 工具目录自由扩展（sub_*子目录）
	✅ Clink命令行增强（自动检测启用）
	✅ 工作目录支持（启动时自动切换）

注意事项 

-   **配置更新**：修改 `green_dir.json` 后需重启 LaxuHub 程序生效。
-   **Python pip 路径问题**：Python 的 `pip` 工具官方写死绝对路径。如果 LaxuHub 的安装目录**不是** `D:\` 根目录，在首次使用 Python 环境后，需要重置 `pip` 以避免后续使用中出现路径错误。
    -   **解决方案1**：程序包提供了 `pipreset.bat` (重置) 和 `pipsafeup.bat` (更新并重置) 两个辅助脚本。可直接按需选一个键入命令运行。
	-   **解决方案2**：使用pip的更现代化的包管理工具uv.速度更快，而且没写死路径在程序。
	-   **解决方案3**：用python -m命令调用模块运行pip或其它cli工具

退出环境：关闭启动的命令行窗口即可

作者: 千城真人 b站_碎辰a