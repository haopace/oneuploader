import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from onedriveUpload import onedrive



token_file = sys.argv[1] # 'token.json' # 保存token的文件路径

print(f'token_file: {token_file}')

client_id = '5c9f6a5c-8928-4cc5-b221-ee822ff26f8c'  # 应用ID
client_secret = '7qN8Q~KYSP5VhjKDXWDoqeGWGxtrdbSAl2PeXaN5'  # 应用密码
# 实例化onedrive对象
one = onedrive(client_id=client_id, client_secret=client_secret, token_file=token_file)
# 获取shell脚本里的变量
# 本地文件路径
filePath = sys.argv[2] # '/workspaces/131588624/pythonProject/'

#上传至onedirve的路径
remotePath = sys.argv[3] # 'OneDrive/Documents/pythonProject/'
flag = one.upload_files(filePath, remotePath)

if flag:
    sys.exit(0) # 上传成功
else:
    sys.exit(1)# 上传失败