import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from onedriveUpload import onedrive
from config import settings

one = onedrive(client_id=settings.client_id, client_secret=settings.client_secret)
# 获取shell脚本里的变量
# 本地文件路径
filePath = sys.argv[1] # '/workspaces/131588624/pythonProject/'

#上传至onedirve的路径
remotePath = sys.argv[2] # 'OneDrive/Documents/pythonProject/'
one.upload_files(filePath, remotePath)

# # 本地文件路径
# filePath = '/workspaces/131588624/pythonProject/nginx'
# # 上传至onedirve的路径
# remotePath = '/test/nginx'
# one.upload_folder(filePath, remotePath)
