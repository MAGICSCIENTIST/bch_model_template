#!/bin/bash
# image name
sudo apt install jq -y # 安装yq命令，curl地址按需修改，主要用于json文件获取imageName
IMAGE_NAME=$(jq -r '.imageName' ./build/config.json)

echo "Building docker image..."
docker build -t ${IMAGE_NAME} -f ./build/Dockerfile_linux .

echo "save the container to an image"
docker save -o ${IMAGE_NAME}.tar  ${IMAGE_NAME}

echo "done!"

