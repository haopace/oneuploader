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
flag = one.upload_files(filePath, remotePath)

if flag:
    sys.exit(0) # 上传成功
else:
    sys.exit(1)# 上传失败