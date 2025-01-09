from enum import Enum
import os
from typing import List, Protocol, Union
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np




class ColorMapItem():
    value: int
    color: Union[str,List[int]]
    label: str

    def __init__(self, value: int,  color: Union[str,List[int]], label: str=None):
        self.value = value
        self.label = label
        self.color = color


def hex2RGB(hex: str):
    if(hex.startswith("#")):
        hex = hex[1:]
    if(len(hex) == 3):
        hex = hex[0] * 2 + hex[1] * 2 + hex[2] * 2

    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def covertColor2RGB(color: Union[str,List[int]]) -> np.ndarray:
    if(isinstance(color, str)):
        return hex2RGB(color)
    else:
        return color
def convertColor2BGR(color: Union[str,List[int]]) -> np.ndarray:
    return covertColor2RGB(color)[::-1]

def scaleImage(image: cv2, size):
    return cv2.resize(image, size)

def symbolizeImage(image: np.ndarray, colorMap: List[ColorMapItem]):
    _image = image.copy()
    # 检查image的shape, 全部转为三维
    if(len(_image.shape) == 2):
        _image = np.stack([_image] * 3, axis=-1)

    # 针对每个值，进行颜色映射
    # 并替换三通道图像中的值    
    for i in range(_image.shape[0]):
        for j in range(_image.shape[1]):
            value = image[i, j]  # 获取灰度值
            # find equal value colorMap item        
            colorMapItem = next((item for item in colorMap if (item.value == value).any()), None)
            if colorMapItem is not None:            
                _image[i, j] = covertColor2RGB(colorMapItem.color) # 替换为对应的RGB值
        
    return _image


def creatBlankImage(size: tuple, fill: Union[str,List[int]]):
    '''
    size : (width, height)
    '''
    _temp = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    bgColor = covertColor2RGB(fill) 
    _temp[:,:] = bgColor
    return _temp


def draw(background: np.ndarray, image: np.ndarray, positionXY: tuple, editRaw=False):
    """
    在背景图上绘制图像
    position: (x,y) x is the left, y is the top
    """
    _background =  background if editRaw else background.copy()
    # convert to (y ,x) 
    position = (int(positionXY[1]), int(positionXY[0]))

    # if is rgb image
    if image.shape[2] == 3:
        # draw normal image
        _background[position[0]:position[0] + image.shape[0], position[1]:position[1] + image.shape[1]] = image
    # if is rgba image
    elif image.shape[2] == 4:
        # calculate alpha ratio
        alpha = image[:, :, 3] / 255
        # calculate background ratio
        background_ratio = 1 - alpha
        # calculate image ratio
        image_ratio = alpha
        # calculate image value
        image_value = image[:, :, :3] * image_ratio[:, :, None]
        # calculate background value
        background_value = _background[position[0]:position[0] + image.shape[0], position[1]:position[1] + image.shape[1]] * background_ratio[:, :, None]
        # calculate final value
        final_value = image_value + background_value
        # draw image
        _background[position[0]:position[0] + image.shape[0], position[1]:position[1] + image.shape[1]] = final_value
    elif image.shape[2] == 1:
        # draw gray image
        _background[position[0]:position[0] + image.shape[0], position[1]:position[1] + image.shape[1], 0] = image
        _background[position[0]:position[0] + image.shape[0], position[1]:position[1] + image.shape[1], 1] = image
        _background[position[0]:position[0] + image.shape[0], position[1]:position[1] + image.shape[1], 2] = image
    return _background




def getVerTextImage(text: str, fontSize: int = 12, fontFamily = "./utils/assets/font/simhei.ttf", color: Union[str,List[int]] = '#000'):
    """
    获取垂直文本的图像
    """
    _image = Image.new("RGBA", (fontSize, len(text) * fontSize), (255, 255, 255,0))
    draw = ImageDraw.Draw(_image)
    fp = os.path.abspath(fontFamily)
    _font = ImageFont.truetype(fp, size=fontSize, encoding="utf-8")
    _font.getbbox(text)
    draw.text((0, 0), text, covertColor2RGB(color), font=_font)
    
    a= np.array(_image)
    # 旋转90度
    return np.rot90(a, 3)




#     _image = image if editRaw else image.copy()        
#     cv2.putText(_image, text, cv2OrgPosition, font, scale, convertColor2BGR(color),thickness=thickNess,lineType=cv2.LINE_AA)
#     text_width, text_height = cv2.getTextSize(text, font, scale, thickNess)[0]
#     return _image, (text_width, text_height)
def drawText(image: np.ndarray, text: str, position: tuple, fontSize: float = 12, fontFamily = "./utils/assets/font/simhei.ttf", color: Union[str,List[int]] = '#000',editRaw=False):
    """
    在图像上绘制文本
    position: (x,y) is the textbox leftBottomCorner
    """
    

    _image = Image.fromarray(image)
    draw = ImageDraw.Draw(_image)
    fp = os.path.abspath(fontFamily)
    _font = ImageFont.truetype(fp, size=fontSize, encoding="utf-8")
    draw.text(position, text, covertColor2RGB(color), font=_font)

    na = np.array(_image)
    if(editRaw):
        image[:,:,:] = na[:,:,:]
    return na    


def read_rgb_img(path):
    bgr = cv2.imread(path)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb


class ImageFuseType(Enum):
    overlay = "overlay"
    sum = "sum"
    average = "average"
    max = "max"
    min = "min"

def negative(image: np.ndarray):
    """
    取负片
    """
    return 255 - image

def addNoise(image: np.ndarray, seed=None, noise_level=20):
    """
    添加噪声
    """
    np.random.seed(seed)
    noise = np.random.normal(0, noise_level, image.shape).astype(np.float32)
    noise_image = image + noise
    noise_image[noise_image < 0] = 0
    noise_image[noise_image > 255] = 255
    return noise_image

def fuseImages(images: np.ndarray, fusion_type:ImageFuseType = ImageFuseType.overlay):
    """
    叠加融合多个图像
    """
    # 获取最大范围，用于创建背景图
    max_shape = np.max([image.shape for image in images], axis=0)
    # 创建背景图
    if fusion_type == ImageFuseType.overlay:
        background = np.zeros(max_shape, dtype=np.uint8)      
        # 遍历每个图像，绘制到背景图上
        for image in images:
            background = draw(background, image, (0, 0), editRaw=True)        
    else:
        _images = []
        # 生成image缓存，将尺寸填充0扩展对齐尺寸
        for i in range(len(images)):
            image = images[i]
            mask = np.zeros(max_shape, dtype=bool)
            mask[:image.shape[0], :image.shape[1]] = True      
            _image = np.zeros(max_shape, dtype=image.dtype)

            _image[mask] = image.flatten()
            _image = _image.astype(np.float32)
            _image[~mask] = np.nan
            _images.append(_image)

        if fusion_type == ImageFuseType.sum:
            # 遍历每个图像，获取每个像素的值，然后求和
            # images 尺寸不一致时
            background = np.sum(_images, axis=0)

        elif fusion_type == ImageFuseType.average:
            return np.nanmean(_images, axis=0).astype(image.dtype)
        elif fusion_type == ImageFuseType.max:
            return np.nanmax(_images, axis=0).astype(image.dtype)
        elif fusion_type == ImageFuseType.min:
            return np.nanmin(_images, axis=0).astype(image.dtype)
        else:
            raise ValueError("Invalid fusion type")
    

    return background





def save(image: np.ndarray, path: str):
    if(image.dtype != np.uint8):
        image = image.astype(np.uint8)        
    cv2.imwrite(path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))