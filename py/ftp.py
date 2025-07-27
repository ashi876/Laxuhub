from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

# 获取脚本所在目录作为根目录
# FTP_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# 或者直接使用当前工作目录（启动脚本时的目录）
FTP_DIRECTORY = os.getcwd()  # 或者直接写 "." 也可以

authorizer = DummyAuthorizer()
# 允许匿名访问，权限设置为只读（示例）或根据需求调整
authorizer.add_anonymous(FTP_DIRECTORY, perm="elr")  # 注意：这里去掉了写权限

handler = FTPHandler
handler.authorizer = authorizer
handler.encoding = "gbk"  # 设置编码

server = FTPServer(("0.0.0.0", 21), handler)
print(f"FTP服务器已启动，根目录: {FTP_DIRECTORY}")
server.serve_forever()