#!/bin/bash


# 容器名称 随便写，测试用的
CONTAINER_NAME="bchmx_5_sjshd_con"

# 输入输出路径根目录, 绝对路径，用于挂载数据卷
INPUT_PATH=d/work/lkybch/bch_model_template/data/
OUTPUT_PATH=d/work/lkybch/bch_model_template/output/


# image name read from json
sudo apt install jq -y # 安装yq命令，curl地址按需修改，主要用于json文件获取imageName
IMAGE_NAME=$(jq -r '.imageName' ./build/config.json)
echo "IMAGE_NAME: ${IMAGE_NAME}"



conid=$(docker ps -a -q -f name=${CONTAINER_NAME})  # 将命令的输出赋值给变量 abc


# 判断变量 image 是否为空
# 如果非空则表示容器存在，需要删除
if [ -z "$conid" ]; then
    echo "Container '${CONTAINER_NAME}' does not exist."
else
    echo "Container '${CONTAINER_NAME}' exists. Removing it..."
    docker rm ${CONTAINER_NAME}
fi

echo "Running docker container:'${CONTAINER_NAME}'..."

# 容器运行,-v 是 挂载数据卷，--name 是容器名称，最后是镜像名称，后面是参数与json文件对应
docker run -v /mnt/${INPUT_PATH}:/input:ro \
           -v /mnt/${OUTPUT_PATH}:/output:rw \
           --name ${CONTAINER_NAME}\
           ${IMAGE_NAME} \
           --input_path \
              /input/image1.jpg \
              /input/image2.jpg \
           --ref_files\
             /input/image3.jpg \
           --output_path=/output \
           --noise=100 \
           --seed=1 \
           --is_valid=True
