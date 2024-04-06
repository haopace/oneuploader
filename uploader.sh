#!/bin/bash

GID="$1";
FileNum="$2";
File="$3";
MaxSize="15728640";


# 添加上传日志
echo "-------------------------------------------------------------" >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
echo "$(date +%Y-%m-%d\ %H:%M:%S) $GID $FileNum $File" >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
echo "$(date +%Y-%m-%d\ %H:%M:%S) $FileNum $File uploading start..." >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;

# Thread="3";  #默认3线程，自行修改，服务器配置不好的话，不建议太多
# Block="20";  #默认分块20m，自行修改
RemoteDIR="/movies/";  #上传到Onedrive的路径，默认为根目录，如果要上传到MOERATS目录，""里面请填成MOERATS
LocalDIR="/workspaces/131588624/pythonProject/downloads/";  #Aria2下载目录，记得最后面加上/
Uploader="/workspaces/131588624/pythonProject/onedrivepyupload/upload.py";  #上传的程序完整路径，默认为本文安装的目录
# Config="/root/auth.json";  #初始化生成的配置auth.json绝对路径，参考第3步骤生成的路径


if [[ -z $(echo "$FileNum" |grep -o '[0-9]*' |head -n1) ]]; then FileNum='0'; fi
if [[ "$FileNum" -le '0' ]]; then exit 0; fi
if [[ "$#" != '3' ]]; then exit 0; fi

function LoadFile(){
  if [[ ! -e "${Uploader}" ]]; then return; fi
  IFS_BAK=$IFS
  IFS=$'\n'
  tmpFile="$(echo "${File/#$LocalDIR}" |cut -f1 -d'/')"
  echo 'tmpFile:'${tmpFile} >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
  FileLoad="${LocalDIR}${tmpFile}"
  echo 'FileLoad:'${FileLoad} >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
  if [[ ! -e "${FileLoad}" ]]; then return; fi
  ItemSize=$(du -s "${FileLoad}" |cut -f1 |grep -o '[0-9]*' |head -n1)
  echo 'ItemSize:'${ItemSize} >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
  if [[ -z "$ItemSize" ]]; then return; fi
  if [[ "$ItemSize" -ge "$MaxSize" ]]; then
    echo -ne "\033[33m${FileLoad} \033[0mtoo large to spik.\n";
    return;
  fi
  RemoteDIR="${RemoteDIR}${tmpFile}";
  echo "RemoteDIR:${RemoteDIR}" >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
  sudo python "${Uploader}" "${FileLoad}" "${RemoteDIR}"

  echo "$(date +%Y-%m-%d\ %H:%M:%S) $FileNum $File uploading end..." >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
  if [[ $? == '0' ]]; then
    rm -rf "${FileLoad}";
    echo "$(date +%Y-%m-%d\ %H:%M:%S) $FileNum $File deleted" >> /workspaces/131588624/pythonProject/onedrivepyupload/logs/upload.log;
  fi
  IFS=$IFS_BAK
}
LoadFile;
