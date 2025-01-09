# fim_model_template
[TOC]
- [fim\_model\_template](#fim_model_template)
  - [简介](#简介)
  - [使用方法](#使用方法)
    - [1. 安装依赖](#1-安装依赖)
    - [2. 配置环境](#2-配置环境)
      - [2.1 放置代码](#21-放置代码)
      - [2.2 配置config.json](#22-配置configjson)
      - [2.3 配置运行环境](#23-配置运行环境)
      - [2.4 配置environment.yml](#24-配置environmentyml)
      - [2.5 配置Dockerfile](#25-配置dockerfile)
    - [3. 运行](#3-运行)
      - [3.1 正常调试python代码](#31-正常调试python代码)
      - [3.2 构建镜像 build.sh](#32-构建镜像-buildsh)
      - [3.3 测试镜像 run.sh](#33-测试镜像-runsh)
    - [Q\&A](#qa)
      - [1. 如何安装docker](#1-如何安装docker)
      - [2. vscode 如何运行bash脚本](#2-vscode-如何运行bash脚本)
      - [3. 如何调试docker](#3-如何调试docker)
      - [4. 我如何知道怎么填enviroment.yml](#4-我如何知道怎么填enviromentyml)
      - [5. 我的模型有多个输入文件，如何处理](#5-我的模型有多个输入文件如何处理)
      - [6. 我的模型有多个入口文件，如何处理](#6-我的模型有多个入口文件如何处理)
      - [7.代码中如何请求和获取参数](#7代码中如何请求和获取参数)
      - [8. 我的输出有什么要求？](#8-我的输出有什么要求)
      - [9 还有什么要求？](#9-还有什么要求)
      - [9. utils文件夹是干什么的](#9-utils文件夹是干什么的)


## 简介
这是一个用于快速搭建模型的模板，主要用于快速搭建模型与build docker，方便快速迭代与集成，模板主要针对IDE是VSCODE，其他IDE可参考相关内容自行配置。模版本身提供了一个简单的执行一个混合图片py文件的模板，按下述章节的使用方法执行 `build.sh`与`run.sh`后应当可看到output文件夹下有输出文件。

您的一个标准的工程目录应该类似如下：
```shell
.
├── doc -> 一些文档，可以放置模型的一些说明文档
├── build
    ├── build.sh
    ├── run.sh
    ├── Dockerfile_linux
    ├── environment.yml
    ├── config.json
├── your_model
├── utils -> 一些本工程提供的工具函数可以直接使用，如果可以达到相同功能的代码，可以不用
```





<span style="color:red; font-weight:700">特别要求</span>：
* 请不要在`build`目录下放置其他文件，这个目录是用于构建docker的，请不要放置您的模型运行文件
* 您的docker build 平台要求支持`arm64`
* 您的终端平台应当支持`bash`脚本，且为`linux`系统

## 使用方法
### 1. 安装依赖
```shell
pip install -r requirements.txt
```
### 2. 配置环境
#### 2.1 放置代码
将模型代码放置在根目录下，例如`main.py`。
#### 2.2 配置config.json
编辑`build`目录下`config.json`文件，配置模型的参数，`args`、`imageName`例如：
```json
{
    "version": "1.0.0", // 模型版本，若有更新请更改
    "args": { // 模型暴露的入参，下边的key值是参数名，可以自定义，但是不要重复
        "ppppp1": {
            "name": "我是这个参数的中文显示名称，不写默认是英文的key值",
            "type": "string", // 参数类型，支持string、int、double、bool、file
            "required": false,
            "description": "我是一段描述，随便写，也可以不写"
        },
         "is_valid":{
            "name": "分支",
            "type": "bool",
            "required": true,
            "default": false,
            "description": "一个bool类型的参数，建议有多个文件有多个方法执行的，用一些参数控制分支，不要用多个模型，这样会导致模型过多，不好维护"
        
        } ,
        
         "output_path": {
            "name": "输出路径",
            "type": "string",
            "required": true,
            "description": "输出路径，一般就是文件夹路径，有多文件输出需要的，自己join即可，推荐结果不要放在子文件夹内"
        },

        // file 类型的参数, 主要用于文件输入
        "input_path": {
            "name": "输入数据",
            "type": "file",
            "required": true,
            "description": "shp、dat等多文件的会将所有文件一并传入数组，请自行通过文件名+后缀，也可考虑多个入参参数"
        },                                   
    },
    // 指明模型的输入文件是哪些参数，是args的key的数组
    "inputFiles": [
        "input_path"
    ],
    // 指明模型的输出是哪些参数，是args的key的数组
    "outputFiles": [
        "output_path"
    ],
    // 模型的镜像名称，这个是在docker中的镜像名称，不要重复，所以建议
    "imageName": "image_fuzz",
    // 模型的一些描述
    "description": "我是一段描述，随便写，也可以不写"
}
```
#### 2.3 配置运行环境
打开`launch.json`，更改`test model py`配置项中的`program`属性，将其更改为你的主入口文件，例如`main.py`。
``` json
 {
    "name": "test model py",
    "type": "python",
    "request": "launch",
    "program": "你的模型的文件.py",
    "console": "integratedTerminal",
    "cwd": "${workspaceRoot}",
    "justMyCode": false,
    "args": [                                
        ....                
    ]
},   
```
#### 2.4 配置environment.yml
编辑`build`目录下`environment.yml`文件，配置模型的环境：
```yaml
name: lfcd  # 这个是环境的名称，可以自定义
channels:
  - defaults
  - conda-forge # 这个是conda的镜像源，可以自定义
dependencies:
  - python=3.9 # python版本,可以自定义，但推荐>3.7
  - numpy=1.20.3 # 一些其他的包，可以自定义，规则就是：包名=版本号
  - gdal=3.6.2 # gdal包 特别的，如果有用到的请放这里
  - pip # pip包管理器
  - pip:
    - opencv-python==4.10.0.84 # openCV包 没有图形化输出的可以不要
    - pyproj==3.1.0 # 一些其他conda安装不了的包，可以自定义，规则就是：包名==版本号
```
#### 2.5 配置Dockerfile
编辑`build`目录下`Dockerfile_linux`文件，配置模型的环境：
```dockerfile
# 主要修改这里的导数第三个参数"lfcd"，改为你environment.yml的name值
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "lfcd", "python", "main.py"]

```

### 3. 运行
#### 3.1 正常调试python代码
参考`launch.json`中的配置，选择`test model py`，配置好args，点击运行即可，有其他调试方法也可自行选择。
#### 3.2 构建镜像 build.sh
参考`launch.json`中的配置，选择`Bash build docker`，主要是运行build/build.sh，点击运行即可。
#### 3.3 测试镜像 run.sh
* 参考`launch.json`中的配置，选择`Bash run docker`，主要是运行build/run.sh。
* 修改`run.sh`中的参数，诸如INPUT_PATH、OUTPUT_PATH等为你的本机绝对路径，修改docker run 中的参数对应你的模型参数。
* 点击运行即可。
* 如果可以正常输出想要的结果，则模型可行，否则请继续调试。



### Q&A
#### 1. 如何安装docker
请参考[docker官网](https://docs.docker.com/desktop/setup/install/windows-install/)，根据自己的系统选择安装方式。
注意：
* windows 推荐安装docker desktop，方便调试容器
* build平台要求支持`arm64`，请注意选择安装方式
* 终端平台应当支持`bash`脚本，且为`linux`系统，方便调试命令
* 安装完成后，可以在终端输入`docker -v`查看是否安装成功

#### 2. vscode 如何运行bash脚本
左侧插件目录搜索`bash debug`，安装`Bash Debug`插件，然后在`launch.json`中配置bash脚本的运行方式（工程应该基本写好了），然后选择要执行的launch脚本，F5运行。另外工程提供的`"Bash test"`配置可执行当前文件，可打断点。


#### 3. 如何调试docker
python> 3.7的，`print()`可以直接输出到终端，如果是低版本的，可以使用`docker logs`查看输出（或者在docker destop中选择容器-你刚刚run的容器-logs面板里查看），或者在代码中写入文件，然后在容器中查看文件内容。由于比较繁琐，所以建议多打日志，且先在本地调试好代码后，再放到docker中调试。

#### 4. 我如何知道怎么填enviroment.yml
conda可以使用命令
```shell
conda env export > environment.yaml
```
pip可以使用命令
```shell
pip freeze > requirements.txt
```
需要注意的是，这两个命令是将当前环境的所有包都导出，<span style="color:red">如果有不需要的包，请手动删除</span>。

#### 5. 我的模型有多个输入文件，如何处理
如果有多个文件，可以在`config.json`中配置多个`input_path`参数，然后在`main.py`中通过`args`获取到文件路径，然后自行处理。

#### 6. 我的模型有多个入口文件，如何处理
十分抱歉，请保证一个模型只有一个入口文件，如果有多个入口文件，可以通过`args`参数控制分支，然后在`main.py`中通过`args`获取到参数，然后自行处理。

#### 7.代码中如何请求和获取参数
传参参考`launch.json`中的`test model py`配置，

接收参考示例代码中的main.py，通过`args`获取参数，然后自行处理。
```python
# 读取config.json文件，生成args
configPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "build/config.json")   
args = initArgs(configPath, configType="json")

```

#### 8. 我的输出有什么要求？
* print()的内容如果想要系统预览，请写入文件，txt就行
* 几何数据统一使用4490坐标系
* tif、dat等栅格输出请同步输出一张jpg图片，方便预览
* fig、plt等图片请savefig，后缀是jpg，请注意，<span style="color:red; font-weight:700">任何的弹出图片的show()方法都会导致docker无法运行，请正式运行时注释掉</span>：
* 输出文件请尽可能只写入`output_path`文件夹，不要放在子文件夹内，方便查看
  
#### 9 还有什么要求？
* 模型运行时，不要有弹出窗口，不要有交互式输入，不要有任何需要人工干预的操作，模型运行完全自动化，不要有任何人工干预，会卡住的。
* 模型代码请捕获异常，不要让异常直接抛出，如果有异常，请写入日志，不要让异常直接抛出，这可方便日后定位问题。

#### 9. utils文件夹是干什么的
utils文件夹是一些本工程提供的工具函数，随缘更新，可以直接使用，如果有可以达到相同功能的代码，可以不用。
目前提供一堆诸如：
* `initArgs`：读取`config.json`文件，生成`args`参数
* 各类图片处理函数，例如读取、颜色转换、保存等
* 一个地图输出函数，可以输出图片，有输出tif的建议参考一下也输出一个jpg的结果，方便预览


TIPS:
仓库地址：[bch_model_template](https://github.com/MAGICSCIENTIST/bch_model_template) 随缘更新，有问题请提issue。

模板测试数据来自：
Photo by <a href="https://unsplash.com/@mohamadaz?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Mohammad Alizade</a> on <a href="https://unsplash.com/photos/a-close-up-of-a-red-object-with-a-blurry-background-O0cJ9QZT8ys?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>
Photo by <a href="https://unsplash.com/@freecx?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Alexey Golubev</a> on <a href="https://unsplash.com/photos/a-green-leaf-with-drops-of-water-on-it-FMJb3fA0TkA?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>
Photo by <a href="https://unsplash.com/@akin?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Akin Cakiner</a> on <a href="https://unsplash.com/photos/a-cat-looking-up-Iyf26znPn64?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>
      