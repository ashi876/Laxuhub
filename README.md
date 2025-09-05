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
			└── python_3.11/ # 符合 "python*" 模式
	错误示例（不会被识别）：
		green_python/ 
			├── 3.9/ # ❌ 缺少语言前缀 
			├── v3.10/ # ❌ 不符合 "python*" 模式 
			└── py3.11/ # ❌ 不匹配配置中的模式

核心组件说明 

	mybin 目录： 
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
	
	cn_mirror.bat： 
	自动配置国内镜像源
	支持常见包管理器（pip/npm/go等）
	启动时自动执行，显著提升包下载速度
	位置：mybin/cn_mirror.bat

环境配置 

	配置文件：green_dir.json（程序自带，按需添加环境）
	添加新环境：参考已有格式添加新语言配置

配置包含：

显示名称

	基础目录（如 green_python）
	PATH子目录（如 ["", "Scripts"]）
	环境变量（如 PYTHON_HOME）
	版本匹配模式（如 python*）
	
特性 

	✅ 多环境任意组合同时激活（PATH/环境变量自动合并）
	✅ 防重复选择（同一语言只选一个版本）
	✅ 镜像源自动配置（通过cn_mirror.bat）
	✅ 语言环境目录自由扩展（通过green_dir.json）
	✅ 工具目录自由扩展（sub_*子目录）
	✅ Clink命令行增强（自动检测启用）
	✅ 工作目录支持（启动时自动切换）

注意事项 

	环境目录必须以 green_ 前缀命名
	版本目录必须包含语言名前缀（如 python3.9 而非 3.9）
	版本目录命名需符合配置中的 version_pattern（如 python*）
	修改 green_dir.json 后需重启程序生效

退出环境：关闭启动的命令行窗口即可

作者: 千城真人 b站_碎辰a