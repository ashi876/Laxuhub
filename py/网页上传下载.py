from nicegui import app, ui
import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 如果目录不存在，则创建
directory = os.path.join(script_dir, 'upload/')
if not os.path.exists(directory):
    os.makedirs(directory)

# 添加静态文件服务，使文件可通过URL访问
app.add_static_files('/upload', directory)

# 主页按钮
with ui.row().classes('w-full justify-center mt-8'):
    with ui.button(on_click=lambda: ui.navigate.to('/uploadfile')).classes('p-4 bg-blue-500 text-white'):
        ui.icon('upload').classes('text-2xl')
        ui.label('上传文件')
    
    with ui.button(on_click=lambda: ui.navigate.to('/downloadfile')).classes('p-4 bg-green-500 text-white ml-4'):
        ui.icon('download').classes('text-2xl')
        ui.label('下载文件')

def save_file(content, filename):
    """保存文件到服务器"""
    try:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        ui.notify(f'文件 "{filename}" 保存成功!', color='positive')
    except Exception as e:
        ui.notify(f'保存失败: {str(e)}', color='negative')

def list_files():
    """获取可下载文件列表（相对路径）"""
    file_list = []
    for root, _, files in os.walk(directory):
        for name in files:
            # 获取相对于上传目录的路径
            rel_path = os.path.relpath(os.path.join(root, name), directory)
            # 转换为URL兼容格式
            rel_path = rel_path.replace('\\', '/')
            file_list.append(rel_path)
    return sorted(file_list)  # 排序文件列表

@ui.page('/uploadfile')
def upload_page():
    """文件上传页面"""
    with ui.header().classes('bg-gray-100 p-4'):
        with ui.row().classes('w-full items-center'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat')
            ui.label('文件上传').classes('text-h5 mx-auto')
            ui.button(icon='download', on_click=lambda: ui.navigate.to('/downloadfile')).props('flat')
    
    with ui.card().classes('w-2/3 mx-auto mt-8 p-8'):
        ui.label('选择文件上传到服务器').classes('text-lg mb-4')
        ui.upload(
            on_upload=lambda e: save_file(e.content.read(), e.name),
            on_rejected=lambda: ui.notify('文件类型或大小不符合要求!', color='warning')
        ).classes('max-w-full')

@ui.page('/downloadfile')
def download_page():
    """文件下载页面"""
    files = list_files()
    
    with ui.header().classes('bg-gray-100 p-4'):
        with ui.row().classes('w-full items-center'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat')
            ui.label('文件下载').classes('text-h5 mx-auto')
            ui.button(icon='upload', on_click=lambda: ui.navigate.to('/uploadfile')).props('flat')
    
    with ui.card().classes('w-2/3 mx-auto mt-8 p-8'):
        if not files:
            ui.label('暂无文件可下载').classes('text-lg text-gray-500 text-center')
        else:
            ui.label('点击文件名下载文件').classes('text-lg mb-4')
            with ui.list().classes('w-full'):
                for file in files:
                    # 生成正确的下载URL
                    download_url = f"/upload/{file}"
                    with ui.item().classes('hover:bg-gray-100 p-2 rounded'):
                        with ui.item_section().props('avatar'):
                            ui.icon('description', color='primary')
                        with ui.item_section():
                            ui.link(file, download_url).classes('text-blue-600 hover:underline')
                        with ui.item_section().props('side'):
                            # 添加下载按钮
                            ui.icon('download', color='green').classes('cursor-pointer').on('click', 
                                lambda _, url=download_url: ui.download(url))

ui.run(title='文件上传下载工具', host='0.0.0.0', port=8080)