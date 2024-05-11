# 基于OneDrive API v2.0的Python文件上传程序
import os
import webbrowser
from urllib.parse import parse_qs
from urllib.parse import urlparse
import requests
import json
import time
import re
from tqdm import tqdm




class onedrive:

    def __init__(self,client_id,client_secret,token_file):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = token_file
        self.redirect_uri = 'http://localhost:9988'
        self.oauth2_uri = 'https://login.microsoftonline.com/common/oauth2/token'
        self.resource_uri = 'https://graph.microsoft.com'
        self.onedrive_uri = self.resource_uri + '/v1.0/me/drive'
        self.scope = 'offline_access onedrive.readwrite'
        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.token = self.read_token()['access_token']
        self.header['Authorization'] = f'bearer {self.token}'

    def get_code(self):
        url = f'https://login.microsoftonline.com/common/oauth2/authorize?' \
              f'response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
        webbrowser.open(url, new=0, autoraise=True)

    def get_token(self, url):
        code = parse_qs(urlparse(url).query).get('code')[0]
        data = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'resource': self.resource_uri
        }
        resp = requests.post(self.oauth2_uri, headers=self.header, data=data).json()
        return self.save_token(resp,self.token_file)

    def refresh_token(self):
        token = self.read_token(only_read=True)
        data = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'client_secret': self.client_secret,
            'refresh_token': token['refresh_token'],
            'grant_type': 'refresh_token',
            'resource': 'https://graph.microsoft.com'
        }
        resp = requests.post(self.oauth2_uri, headers=self.header, data=data).json()
        return self.save_token(resp,self.token_file)

    @staticmethod
    def save_token(resp,token_file):
        if 'error' in resp:
            return False
        token = {
            'access_token': resp['access_token'],
            'refresh_token': resp['refresh_token'],
            'expires_on': int(resp['expires_on'])
        }
        with open(token_file, 'w') as f:
            f.write(json.dumps(token))
        return token

    def read_token(self, only_read=False):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token = json.loads(f.read())
        else:
            self.get_code()
            print('请在浏览器中输入以下链接，并登录OneDrive账号，然后复制地址栏中的URL：')
            print(f'https://login.microsoftonline.com/common/oauth2/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}')
            token = self.get_token(input('请输入Url：'))
        if only_read:
            return token
        if token['expires_on'] <= int(time.time()):
            token = self.refresh_token()
        return token

    def get_path(self, path, op):
        if path[0] == '/': path = path[1:]
        if path[-1] == '/': path = path[:-1]
        if op[0] == '/': op = op[1:]
        return self.onedrive_uri + '/root:/{}:/{}'.format(path, op)

    def create_folder(self, path):
        path = list(filter(None, path.split('/')))
        pa = '/'.join(path[:len(path) - 1])
        name = path[len(path) - 1]
        data = json.dumps({
            "name": name,
            "folder": {},
        })
        r = requests.post(self.get_path(pa, 'children'), headers=self.header, data=data)
        return r.status_code

    def upload_url(self, path, conflict="fail"):
        r = requests.post(self.get_path(
            path, 'createUploadSession'
        ), headers=self.header)
        if r.status_code == 200:
            return r.json()['uploadUrl']
        else:
            return ""
    def clean_file_name(self,file_path):
        # 获取文件名
        file_name = os.path.basename(file_path)

        # 使用正则表达式去除特殊字符和空格
        cleaned_file_name = re.sub(r'[^\w\s.-]', '', file_name)
        # 去除所有空格，包括中文空格，用-空格替换
        cleaned_file_name = re.sub(r'[\s\u3000]+', '-', cleaned_file_name)
        # 去除开头和结尾的空格
        cleaned_file_name = cleaned_file_name.strip()

        return os.path.join(os.path.dirname(file_path), cleaned_file_name)

    def upload_file(self, path, file_path):
        # 上传的文件中不能有特殊字符，处理下
        path = self.clean_file_name(path)
        size = os.path.getsize(file_path)
        if size > 4000000:
            return self.upload_big_file(path, file_path)
        else:
            with open(file_path, 'rb') as f:
                data = f.read()
                r = requests.put(self.get_path(path, 'content'), headers=self.header, data=data)
                if 'error' in r:
                    return f"{path}上传失败"
                return f"{path}上传成功"



    def upload_big_file(self, path, file_path):
        url = self.upload_url(path)
        if url == "":
            return "上传取消"

        # 默认上传块大小为8MB
        chunk_size = 8 * 1024 * 1024  # 8MB
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        # 根据文件大小自动调整块大小，最大100MB
        if file_size > 100 * 1024 * 1024:
            chunk_size = 100 * 1024 * 1024  # 100MB
        elif file_size > 50 * 1024 * 1024:
            chunk_size = 50 * 1024 * 1024  # 50MB
        elif file_size > 20 * 1024 * 1024:
            chunk_size = 20 * 1024 * 1024  # 20MB
        elif file_size > 10 * 1024 * 1024:
            chunk_size = 10 * 1024 * 1024  # 10MB

        with open(file_path, 'rb') as file:
            with tqdm(total=file_size,unit='B', unit_scale=True, unit_divisor=1024,desc=file_name) as pbar:
                for i in range(0, file_size, chunk_size):
                    chunk_data = file.read(chunk_size)
                    if not chunk_data:
                        break
                    r = requests.put(url, headers={
                        'Content-Length': str(len(chunk_data)),
                        'Content-Range': 'bytes {}-{}/{}'.format(i, i + len(chunk_data) - 1, file_size)
                    }, data=chunk_data)
                    if r.status_code not in [200, 201, 202]:
                        print(f"{path}上传出错")
                        break
                    pbar.update(len(chunk_data))




    # 聚合文件上传方法
    def upload_files(self, localPaths, remotePath):
        # 判断文件时文件夹还是文件
        if os.path.isfile(localPaths):
            print(self.upload_file(remotePath, localPaths))
        else:
            for root, dirs, files in os.walk(localPaths):
                # 遍历文件
                for file in files:
                    file_absolute_path = os.path.abspath(os.path.join(root, file))
                    file_relative_path = os.path.relpath(os.path.join(root, file), localPaths)
                    remoteFilePath = os.path.join(remotePath, file_relative_path)
                    # print(os.path.join(root, file))
                    print(f'remoteFilePath:{remoteFilePath}')
                    print(self.upload_file(remoteFilePath, file_absolute_path))
        print("上传完成")
        return True

if __name__ == '__main__':
    one = onedrive(client_id='5c9f6a5c-8928-4cc5-b221-ee822ff26f8c', client_secret='7qN8Q~KYSP5VhjKDXWDoqeGWGxtrdbSAl2PeXaN5',token_file='token.json')
    # 本地文件路径
    filePath = '/workspaces/131588624/tgdonloads/1652151651/2024_05/video/164 - #assdas..mp4'
    # 上传至onedirve的路径
    remotePath = '/test/tgdonloads/1652151651/2024_05/video/164 - fdfsd..mp4'
    # one.upload_files(filePath, remotePath)
    url = one.upload_url(remotePath)
    print(url)
    # for root, dirs, files in os.walk(filePath):
    #     for file in files:
    #         file_absolute_path = os.path.abspath(os.path.join(root, file))
    #         remotepath = os.path.join(remotePath, file_absolute_path.replace(filePath, ''))

    #         with open(file_absolute_path, 'rb') as f:
    #             # 小文件会打印“上传成功”，大文件会显示上传进度条
    #             print(one.upload_file(remotepath, f.read()))
