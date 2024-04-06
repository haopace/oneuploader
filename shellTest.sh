#!/bin/bash

File="$1";
# 使用单引号包裹File，防止路径中有空格
# File="'$File'";
LocalDIR="/workspaces/131588624/pythonProject/downloads/";
tmpFile="$(echo "${File/#$LocalDIR}" |cut -f1 -d'/')"
echo 'tmpFile:'${tmpFile}
FileLoad="${LocalDIR}${tmpFile}"
echo 'FileLoad:'${FileLoad}
