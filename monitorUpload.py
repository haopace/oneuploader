import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from onedriveUpload import onedrive

import time
import schedule
import shutil
from functools import partial
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


token_file = "./token.json"

client_id = '5c9f6a5c-8928-4cc5-b221-ee822ff26f8c'  # 应用ID
client_secret = '7qN8Q~KYSP5VhjKDXWDoqeGWGxtrdbSAl2PeXaN5'  # 应用密码

# 实例化onedrive对象
one = onedrive(client_id=client_id, client_secret=client_secret, token_file=token_file)

# 监控文件夹的路径
tgdownloads_path = '/workspaces/131588624/tgdonloads'

# 远程保存路径
remotePath = '/telegram'

# 存储已上传文件的列表
uploaded_files = []

# 定义上传函数
def upload_files(local_folder_path, remote_folder_path):
    files = os.listdir(local_folder_path)  # 获取文件夹中所有文件的列表
    for file in files:
        if file not in uploaded_files:  # 只处理未上传的文件
            file_path = os.path.join(local_folder_path, file)
            # 在这里添加调用上传文件的逻辑，以及将已上传文件添加到uploaded_files列表的代码
            print(f'Uploading file: {file_path}')
             # 上传文件
            remoteFilePath = os.path.join(remote_folder_path,os.path.basename(file))
            flag = one.upload_files(file_path, remoteFilePath)
            if flag:
                uploaded_files.append(file)  # 将已上传的文件添加到列表中
                print(f'File {file} has been uploaded')
                # 删除文件
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    shutil.rmtree(file_path)
                print(f'File {file} has been deleted after upload')

# 使用functools.partial创建包裹函数
partial_upload_files = partial(upload_files, tgdownloads_path, remotePath)


# 定义定时任务，每5分钟执行一次上传函数
schedule.every(5).minutes.do(partial_upload_files)

# 主循环
while True:
    schedule.run_pending()  # 运行定时任务
    time.sleep(1)


 