import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from onedriveUpload import onedrive
config_file  = sys.argv[1] # 'config.json'
token_file = sys.argv[2] # 'token.json'
with open(config_file, 'r') as f:
    config = json.loads(f.read())
client_id = config['client_id']  # 应用ID
client_secret = config['client_secret']  # 应用密码
# 实例化onedrive对象
one = onedrive(client_id=client_id, client_secret=client_secret, token_file=token_file)
# 获取shell脚本里的变量
# 本地文件路径
filePath = sys.argv[3] # '/workspaces/131588624/pythonProject/'

#上传至onedirve的路径
remotePath = sys.argv[4] # 'OneDrive/Documents/pythonProject/'
flag = one.upload_files(filePath, remotePath)

if flag:
    sys.exit(0) # 上传成功
else:
    sys.exit(1)# 上传失败