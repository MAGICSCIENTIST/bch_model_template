import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from utils.args import initArgs
from utils import mapTool, imageTool


# 这是一个读取输入文件并处理的例子
def justFuncSample1(files, noise, seed):    
    images = []
    # 遍历输入的文件
    for file_path in files:
        image = imageTool.read_rgb_img(file_path)
        images.append(imageTool.negative(image))
    result = imageTool.fuseImages(images, imageTool.ImageFuseType.average)

    if noise is not None:
        result = imageTool.addNoise(result, int(seed), float(noise))

    return result

# 这也是一个读取输入文件并处理的例子
def justFuncSample2(files1, files2, noise, seed):

    images = []
    for file_path in files1:
        image = imageTool.read_rgb_img(file_path)
        images.append(image)
    for file_path in files2:
        image = imageTool.read_rgb_img(file_path)
        images.append(image)
    result = imageTool.fuseImages(images, imageTool.ImageFuseType.average)

    if noise is not None:
        result = imageTool.addNoise(result, int(seed), float(noise))

    return result
   



# 主函数请保证有main函数
# 代码应当尽可能的封装在函数里
def main():
    # 读取config.json文件，生成args
    configPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "build/config.json")   
    args = initArgs(configPath, configType="json")

    # 读取命令行参数
    inputFiles1 = args.input_path # 输入文件是个数组，请自行处理
    inputFiles2 = args.ref_files 
    outputFolder = args.output_path # 输出文件夹
    noise = args.noise
    seed = args.seed
    isValid = args.is_valid

    # 打出来看看
    os.system("ls /input")
    print(args)
    print(inputFiles1)
    print(inputFiles2)
    print(outputFolder)
    print("-----------------------")
    # print all files in input folder
    inputfolder = "/input"
    for root, dirs, files in os.walk(inputfolder):
        for file in files:
            print(file)
            a = cv2.imread(os.path.join(root, file))
            print(a.shape)
    


    # your code here
    if(isValid):
        try:
            result = justFuncSample1(inputFiles1, noise, seed)        
        except Exception as e:
            # print error
            print(e)            
        
    else:
        # another branch
        result = justFuncSample2(inputFiles1, inputFiles2, noise, seed)
    
        
    # save result
    # 拼接一个输出文件路径
    reslutFile = os.path.join(outputFolder, "result.jpg")
    outputFolder = os.path.dirname(reslutFile)
    # 如果文件夹不存在，创建文件夹
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)        
    imageTool.save(result, reslutFile)
    print("Done normal process!")


    # 这是一个生成地图图表的例子，不强求用，可以参考
    # 假设aggregated_data是模型的一个输出
    aggregated_data = cv2.resize(result, (512, 512)).astype(np.uint8)    
    # Create a map document，图片我想要824*482的大小
    mapDoc = mapTool.MapDocument(mapTool.MapWidgetDrawOptions(size=(824,482)).setOptions("background", "#ffffff"))
    mapGrid = mapTool.MapGrid()     
    # 图片里面的地图大小是492*346，位置是(216,66)
    mapOptions = mapTool.MapWidgetDrawOptions(size=(492,346),position=(216,66))
    mapDoc.addWidget(mapGrid, mapOptions)
    
    # 定义一个颜色映射，多用于灰度图分类数据的可视化
    colorMap = [
        mapTool.imageTool.ColorMapItem(1, '#ececec', '低'), # 像素值为1的颜色为#ececec，图例显示的文字是低
        mapTool.imageTool.ColorMapItem(2, '#ffdc80', '中'),
        mapTool.imageTool.ColorMapItem(3, '#fe0000', '高'),
    ]        
    print(len(aggregated_data[aggregated_data==1]))
    # 根据颜色映射，将数据转换为可视化图片
    visImage = mapTool.imageTool.symbolizeImage(aggregated_data, colorMap=colorMap)      
    print(len(visImage[visImage==1]))

    mapGrid.addImage(visImage) 

    # 添加图例
    legend = mapTool.Legend("预测发生等级")        
    # 图例添加颜色映射
    legend.addItemsFromColorMap(colorMap)        
    # 图例大小是108*160，位置是(88, 266)
    options = mapTool.MapWidgetDrawOptions(size=(108,160), position=(88, 266)).setOptions("background", "#ffffff")
    mapDoc.addWidget(legend, options)
    
    # define a 4490
    geoTransform = (101.20235414, 9e-05, -0.0, 22.93545815, -0.0, -9e-05)
    RasterXSize = 674
    RasterYSize = 434
    # create a axis box
    axisBox = mapTool.AxisBox(geoTransform, RasterXSize, RasterYSize)
    # 计算四个边框的经纬度
    axisBox.extentGeoAreaByLocalDrawAreaFrom(mapOptions)
    
    mapDoc.addWidget(axisBox, mapTool.MapWidgetDrawOptions(size=(674,434),position=(75,24)))

    # mapDoc.preview() # 预览地图，正式使用时请注释掉
    mapDoc.save(os.path.join(outputFolder, '_forest_insect_disease_map.jpg'))

    print("Done a map demmo!")
    return 
    


if __name__ == "__main__":
    main()