# -*- coding: utf-8 -*-
"""
pip图形化管理工具主程序
功能：提供图形化界面管理Python包，支持安装/卸载/升级和镜像源切换
"""

# 系统模块导入
import sys  # 系统相关功能
import subprocess  # 执行外部命令
import json  # JSON配置文件处理
import os  # 操作系统接口
from datetime import datetime  # 时间处理

# PyQt6模块导入
from PyQt6.QtWidgets import *  # 修改点1：PyQt5 → PyQt6
from PyQt6.QtCore import *  # Qt核心功能
from PyQt6.QtGui import *  # 图标处理


class PipManager(QMainWindow):
    """
    pip图形化管理工具主窗口类
    提供完整的包管理功能界面和逻辑
    """

    def __init__(self):
        super().__init__()

        self.is_admin = False
        try:
            import ctypes
            self.is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            pass
        
        # 窗口基本设置
        title = 'pip图形化管理工具'
        if self.is_admin:
            title += ' (管理员)'
        self.setWindowTitle(title)  # 窗口标题
        self.setGeometry(100, 100, 800, 600)  # 窗口位置和大小
        
        # 初始化成员变量
        self.current_mirror = None  # 当前使用的镜像源
        self.installed_packages = []  # 已安装包列表缓存
        self.operation_history = []  # 操作历史记录
        self.searched_packages = [] # 搜索到的包列表
        self.requests_available = False  # 初始化requests可用标志
        
        # 检查requests库是否可用
        try:
            import requests
            self.requests_available = True
        except ImportError:
            self.requests_available = False
            QMessageBox.warning(self, '警告', '需要requests库来搜索远程包，请先安装: pip install requests')
        
        # 初始化UI
        self.init_ui()
        
        # 加载配置
        self.load_config()
        
        # 初始化包列表
        self.refresh_package_list()
        # 初始化右键菜单
        self.init_context_menu()

    def init_ui(self):
        """初始化用户界面组件"""
        
        # 1. 创建菜单栏
        self.init_menu_bar()
        
        # 2. 创建工具栏
        self.init_tool_bar()
        
        # 3. 创建状态栏
        self.init_status_bar()
        
        # 4. 创建主内容区
        self.init_main_content()
        
        # 5. 创建右键菜单
        self.init_context_menu()

    def init_menu_bar(self):
        """初始化菜单栏"""
        
        # 文件菜单
        file_menu = self.menuBar().addMenu('文件(&F)')
        
        # 刷新操作
        refresh_action = QAction('刷新包列表', self)
        refresh_action.triggered.connect(self.refresh_package_list)
        file_menu.addAction(refresh_action)
        
        # 退出操作
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设置
        edit_menu = self.menuBar().addMenu('设置(&E)')
        
        # 设置镜像源
        mirror_action = QAction('设置镜像源', self)
        mirror_action.triggered.connect(self.show_mirror_dialog)
        edit_menu.addAction(mirror_action)

         # 添加以管理员身份运行选项
        self.admin_action = QAction('以管理员身份运行', self)
        self.admin_action.triggered.connect(self.run_as_admin)
        if self.is_admin:
            self.admin_action.setEnabled(False)  # 已经是管理员则禁用
        edit_menu.addAction(self.admin_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu('帮助(&H)')
        
        # 关于操作
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def run_as_admin(self):
        """以管理员身份重新运行程序"""
        try:
            import ctypes
            import sys
            
            # 检查是否已经是管理员权限
            if ctypes.windll.shell32.IsUserAnAdmin():
                QMessageBox.information(self, '提示', '当前已经是管理员权限')
                return
                
            # 重新以管理员权限运行
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            
            # 退出当前实例
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'请求管理员权限失败: {str(e)}')


    def init_tool_bar(self):
        """初始化工具栏"""
        
        toolbar = QToolBar('主工具栏')
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # 安装按钮
        install_btn = QPushButton('安装包')
        install_btn.clicked.connect(self.install_package)
        toolbar.addWidget(install_btn)
        
        # 卸载按钮
        uninstall_btn = QPushButton('卸载包')
        uninstall_btn.clicked.connect(self.uninstall_package)
        toolbar.addWidget(uninstall_btn)
        
        # 升级按钮
        upgrade_btn = QPushButton('升级包')
        upgrade_btn.clicked.connect(self.upgrade_package)
        toolbar.addWidget(upgrade_btn)
        
        # 刷新按钮
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.refresh_package_list)
        toolbar.addWidget(refresh_btn)

        # 设置镜像源
        jxy_btn = QPushButton('设置镜像源')
        jxy_btn.clicked.connect(self.show_mirror_dialog)
        toolbar.addWidget(jxy_btn)

    def init_status_bar(self):
        """初始化状态栏"""
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 显示当前镜像源
        self.mirror_label = QLabel('镜像源: 未设置')
        self.status_bar.addPermanentWidget(self.mirror_label)
        
        # 显示状态信息
        self.status_bar.showMessage('准备就绪', 3000)

    def init_main_content(self):
        """初始化主内容区域"""
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 左侧布局 (包列表)
        left_layout = QVBoxLayout()
        
        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('搜索包名...')
        self.search_box.textChanged.connect(self.filter_packages)
        left_layout.addWidget(self.search_box)
        
        # 包列表
        self.package_list = QListWidget()
        self.package_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.package_list)
        
        # 右侧布局 (包详情)
        right_layout = QVBoxLayout()
        
        # 包详情标签
        self.package_detail = QTextEdit()
        self.package_detail.setReadOnly(True)
        right_layout.addWidget(self.package_detail)
        
        # 添加到主布局
        main_layout.addLayout(left_layout, 3)  # 左侧占3份
        main_layout.addLayout(right_layout, 2)  # 右侧占2份

    def init_context_menu(self):
        """初始化右键菜单"""
        
        # 设置包列表的右键菜单
        # 修改点2：Qt.CustomContextMenu → Qt.ContextMenuPolicy.CustomContextMenu
        self.package_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.package_list.customContextMenuRequested.connect(self.show_package_context_menu)
        
        # 创建菜单对象
        self.package_menu = QMenu(self)
        
        # 添加菜单项
        install_action = QAction('安装', self)
        install_action.triggered.connect(self.install_selected_package)  # 改为安装选中包
        self.package_menu.addAction(install_action)
        
        uninstall_action = QAction('卸载', self)
        uninstall_action.triggered.connect(self.uninstall_package)
        self.package_menu.addAction(uninstall_action)
        
        upgrade_action = QAction('升级', self)
        upgrade_action.triggered.connect(self.upgrade_package)
        self.package_menu.addAction(upgrade_action)
        
        self.package_menu.addSeparator()
        
        info_action = QAction('查看详情', self)
        info_action.triggered.connect(self.show_package_info)
        self.package_menu.addAction(info_action)
        
    def install_selected_package(self):
        """安装选中的包"""
        selected_item = self.package_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, '警告', '请先选择一个包')
            return
            
        pkg_name = selected_item.text().split('==')[0]
        
        # 显示使用的镜像源信息
        mirror_info = ""
        if self.current_mirror:
            mirror_info = f"\n镜像源: {self.get_mirror_name(self.current_mirror)}"
        
        # 确认安装
        # 修改点4：QMessageBox.Yes → QMessageBox.StandardButton.Yes
        confirm = QMessageBox.question(
            self, '确认安装',
            f'确定要安装 {pkg_name} 吗?{mirror_info}',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.run_pip_command('install', pkg_name)
            except Exception as e:
                QMessageBox.critical(self, '安装错误', f'安装过程中出错\n{str(e)}')

    def load_config(self):
        """加载配置文件"""
        
        config_path = os.path.expanduser('~/.pip-gui-config')
        
        # 默认镜像源配置
        self.mirrors = {
            "清华": "https://pypi.tuna.tsinghua.edu.cn/simple",
            "阿里云": "https://mirrors.aliyun.com/pypi/simple",
            "腾讯云": "https://mirrors.cloud.tencent.com/pypi/simple",
            "官方源": "https://pypi.org/simple"
        }
        
        try:
            # 尝试加载配置文件
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_mirror = config.get('current_mirror')
                    self.mirror_label.setText(f'镜像源: {self.get_mirror_name(self.current_mirror)}')
        except Exception as e:
            QMessageBox.warning(self, '配置错误', f'加载配置文件失败: {str(e)}')

    def save_config(self):
        """保存配置文件"""
        
        config_path = os.path.expanduser('~/.pip-gui-config')
        config = {
            'current_mirror': self.current_mirror
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, '配置错误', f'保存配置文件失败: {str(e)}')

    def get_mirror_name(self, url):
        """根据URL获取镜像源名称"""
        for name, mirror_url in self.mirrors.items():
            if mirror_url == url:
                return name
        return '自定义源'

    def refresh_package_list(self):
        """刷新已安装包列表"""
        
        try:
            # 执行pip list命令获取已安装包
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # 解析JSON结果
                self.installed_packages = json.loads(result.stdout)
                self.update_package_list_display()
                self.status_bar.showMessage('包列表刷新成功', 3000)
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取包列表失败: {str(e)}')
            self.status_bar.showMessage('获取包列表失败', 3000)

    def update_package_list_display(self):
        """更新包列表显示"""
        self.package_list.clear()
        
        # 按名称排序
        sorted_packages = sorted(self.installed_packages, key=lambda x: x['name'].lower())
        
        # 添加到列表控件
        for pkg in sorted_packages:
            item = QListWidgetItem(f"{pkg['name']}=={pkg['version']}")
            # 修改点5：QColor('black') → QColor('black').name()
            item.setForeground(QColor(QColor('black').name()))  # 本地包用黑色
            self.package_list.addItem(item)
        
        # 添加搜索到的包（如果有）
        for pkg in self.searched_packages:
            item = QListWidgetItem(f"{pkg['name']}=={pkg['version']} (可安装)")
            # 修改点5：QColor('blue') → QColor('blue').name()
            item.setForeground(QColor(QColor('blue').name()))  # 可安装包用蓝色
            self.package_list.addItem(item)


    def search_remote_package(self, package_name):
        """搜索远程包"""
        try:
            import requests
            print(f"正在搜索: {package_name}")  # 调试输出
            
            # 设置正确的请求头
            headers = {
                "Accept": "application/json",
                "User-Agent": "pip-gui-tool/1.0"
            }
            
            # 使用PyPI的JSON API端点
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json",
                headers=headers,
                timeout=10
            )
            
            print(f"响应状态码: {response.status_code}")  # 调试输出
            print(f"响应内容: {response.text[:200]}...")  # 只打印前200字符
            
            # 检查响应状态
            response.raise_for_status()
                
            data = response.json()
            
            self.searched_packages = []
            # 解析API返回的数据格式
            if 'info' in data:
                self.searched_packages.append({
                    'name': data['info']['name'],
                    'version': data['info'].get('version', '最新')
                })
                    
            if self.searched_packages:
                self.update_package_list_display()
                self.status_bar.showMessage(f"找到包: {self.searched_packages[0]['name']}", 3000)
            else:
                self.status_bar.showMessage("未找到匹配包", 3000)
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.status_bar.showMessage(f"未找到包: {package_name}", 3000)
            else:
                error_msg = f"网络请求失败: {str(e)}"
                print(error_msg)
                QMessageBox.critical(self, '错误', error_msg)
        except Exception as e:
            error_msg = f"搜索失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, '错误', error_msg)



    def filter_packages(self):
        """根据搜索框内容过滤包列表"""
        search_text = self.search_box.text().strip()
        
        if not search_text:
            self.searched_packages = []
            self.update_package_list_display()
            return
            
        # 如果requests不可用，直接返回
        if not self.requests_available:
            QMessageBox.warning(self, '警告', 'requests库未安装，无法搜索远程包')
            return
            
        # 先显示本地匹配项
        has_local_match = False
        for i in range(self.package_list.count()):
            item = self.package_list.item(i)
            match = search_text.lower() in item.text().lower()
            item.setHidden(not match)
            if match:
                has_local_match = True
                
        # 如果没有本地匹配，才进行远程搜索
        if not has_local_match:
            self.search_remote_package(search_text)



    def show_package_context_menu(self, pos):
        """显示包列表的右键菜单"""
        
        # 确保有选中的项才显示菜单
        if self.package_list.currentItem():
            # 修改点3：exec_() → exec()
            self.package_menu.exec(self.package_list.mapToGlobal(pos))

    def show_package_info(self):
        """显示选中包的详细信息"""
        
        selected_item = self.package_list.currentItem()
        if not selected_item:
            return
            
        pkg_name = selected_item.text().split('==')[0]
        
        try:
            # 执行pip show命令获取包详情
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', pkg_name],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                self.package_detail.setText(result.stdout)
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取包信息失败: {str(e)}')

    def install_package(self):
        """安装Python包"""
        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('安装包')
        layout = QFormLayout()
        
        # 包名输入框
        pkg_name_edit = QLineEdit()
        layout.addRow('包名:', pkg_name_edit)
        
        # 版本号输入框
        version_edit = QLineEdit()
        version_edit.setPlaceholderText('可选，如: 1.0.0')
        layout.addRow('版本号:', version_edit)
        
        # 确定和取消按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)
        
        dialog.setLayout(layout)
        
        # 修改点3：exec_() → exec()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pkg_name = pkg_name_edit.text().strip()
            version = version_edit.text().strip()
            
            if not pkg_name:
                QMessageBox.warning(self, '警告', '包名不能为空')
                return
                
            if version and not all(c.isdigit() or c == '.' for c in version):
                QMessageBox.warning(self, '错误', '版本号格式不正确，请使用数字和点(.)')
                return
                
            # 显示使用的镜像源信息
            mirror_info = ""
            if self.current_mirror:
                mirror_info = f"\n镜像源: {self.get_mirror_name(self.current_mirror)}"
            
            # 确认安装
            # 修改点4：QMessageBox.Yes → QMessageBox.StandardButton.Yes
            confirm = QMessageBox.question(
                self, '确认安装',
                f'确定要安装 {pkg_name}{"=="+version if version else ""} 吗?{mirror_info}',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    self.run_pip_command('install', pkg_name, version)
                except Exception as e:
                    if "Could not find a version" in str(e):
                        QMessageBox.warning(self, '版本错误', f"找不到指定版本的包\n{e}")
                    elif "No matching distribution" in str(e):
                        QMessageBox.warning(self, '包名错误', f"找不到指定的包\n{e}")
                    else:
                        QMessageBox.critical(self, '安装错误', f"安装过程中出错\n{e}")

    def uninstall_package(self):
        """卸载Python包"""
        
        selected_item = self.package_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, '警告', '请先选择一个包')
            return
            
        pkg_name = selected_item.text().split('==')[0]
        
        # 确认卸载
        # 修改点4：QMessageBox.Yes → QMessageBox.StandardButton.Yes
        confirm = QMessageBox.question(
            self, '确认卸载',
            f'确定要卸载 {pkg_name} 吗?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.run_pip_command('uninstall', pkg_name)

    def upgrade_package(self):
        """升级Python包"""
        
        selected_item = self.package_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, '警告', '请先选择一个包')
            return
            
        pkg_name = selected_item.text().split('==')[0]
        
        # 确认升级
        # 修改点4：QMessageBox.Yes → QMessageBox.StandardButton.Yes
        confirm = QMessageBox.question(
            self, '确认升级',
            f'确定要升级 {pkg_name} 吗?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.run_pip_command('install', pkg_name, upgrade=True)

    def run_pip_command(self, command, pkg_name, version=None, upgrade=False):
        """执行pip命令的通用方法"""
        
         # 构建命令
        cmd = [sys.executable, '-m', 'pip', command, pkg_name]
        
        # 卸载时自动确认
        if command == 'uninstall':
            cmd.append('--yes')
        
        # 添加版本号
        if version:
            cmd.append(f'=={version}')
            
        # 添加升级标志
        if upgrade:
            cmd.append('--upgrade')
            
        # 添加镜像源(卸载操作不需要)
        if self.current_mirror and command != 'uninstall':
            cmd.extend(['-i', self.current_mirror])
            host = self.current_mirror.split('//')[1].split('/')[0]
            cmd.extend(['--trusted-host', host])
        
        try:
            # 执行命令并实时输出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 清空并准备显示输出
            self.package_detail.clear()
            
            # 实时读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.package_detail.append(output.strip())
            
            # 获取最终返回码
            return_code = process.wait()
            
            # 记录操作历史
            self.operation_history.append({
                'command': ' '.join(cmd),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success': return_code == 0,
                'output': self.package_detail.toPlainText()
            })
            
            # 限制历史记录数量
            if len(self.operation_history) > 20:
                self.operation_history.pop(0)
            
            # 显示结果
            if return_code == 0:
                QMessageBox.information(
                    self, '操作成功',
                    f'操作执行成功'
                )
                self.refresh_package_list()
            else:
                error_output = process.stderr.read()
                self.package_detail.append(f"\n错误信息:\n{error_output}")
                raise Exception(error_output)
                
        except Exception as e:
            QMessageBox.critical(
                self, '操作失败',
                f'操作执行失败:\n{str(e)}'
            )
            self.package_detail.append(f"\n错误信息:\n{str(e)}")


    def show_mirror_dialog(self):
        """显示镜像源设置对话框"""
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('设置镜像源')
        layout = QVBoxLayout()
        
        # 添加镜像源选项
        mirror_group = QButtonGroup()
        for i, (name, url) in enumerate(self.mirrors.items()):
            radio = QRadioButton(name)
            radio.url = url
            if url == self.current_mirror:
                radio.setChecked(True)
            mirror_group.addButton(radio, i)
            layout.addWidget(radio)
        
        # 自定义镜像源输入
        custom_radio = QRadioButton('自定义')
        mirror_group.addButton(custom_radio, len(self.mirrors))
        layout.addWidget(custom_radio)
        
        custom_edit = QLineEdit()
        # 修改这里：总是显示当前镜像源URL（如果有）
        if self.current_mirror:
            custom_edit.setText(self.current_mirror)
        else:
            custom_edit.setPlaceholderText('输入镜像源URL')
        
        # 设置默认选中状态
        if not self.current_mirror:
            # 如果没有设置镜像源，默认选中第一项
            mirror_group.buttons()[0].setChecked(True)
            custom_edit.setText(mirror_group.buttons()[0].url)
        
        layout.addWidget(custom_edit)
        
        # 添加单选按钮点击事件
        def on_radio_clicked(button):
            if button != custom_radio:
                custom_edit.setText(button.url)
        
        mirror_group.buttonClicked.connect(on_radio_clicked)
        
        # 确定和取消按钮
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        dialog.setLayout(layout)
        
        # 处理对话框结果
        # 修改点3：exec_() → exec()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = mirror_group.checkedButton()
            if selected == custom_radio and custom_edit.text():
                self.current_mirror = custom_edit.text()
            elif selected != custom_radio:
                self.current_mirror = selected.url
            else:
                return
                
            # 更新UI和配置
            self.mirror_label.setText(f'镜像源: {self.get_mirror_name(self.current_mirror)}')
            self.save_config()
            self.status_bar.showMessage('镜像源设置成功', 3000)




    def show_about(self):
        """显示关于对话框"""
        
        QMessageBox.about(
            self, '关于 pip图形化管理工具',
            'pip图形化管理工具 v1.0\n\n'
            '一个简单的pip包管理图形界面\n'
            '支持安装/卸载/升级和镜像源切换'
        )

    def closeEvent(self, event):
        """重写关闭事件，保存配置"""
        
        self.save_config()
        event.accept()

def main():
    """主程序入口"""
    app = QApplication(sys.argv)
    window = PipManager()
    window.show()
    # 修改点6：app.exec_() → app.exec()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()  # 只有直接运行时才执行