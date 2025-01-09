import os
from typing import Protocol, List
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from utils.geoTool import decimal_to_dms
import utils.imageTool as imageTool


class MapWidgetDrawOptions():
    position = (0,0) # x,y
    size = (800,600) # H,W
    background = 0
    fontSize = 12
    fontFamily="./utils/assets/font/simhei.ttf"
    
    def __init__(self, position=(0,0), size=(800,600)):
        '''
        position: (x,y) x is the left, y is the top
        size: (width, height)
        '''
        self.position = position
        self.size = size

    def setOptions(self, key, value):
        setattr(self, key, value)
        return self
    

class MapWidget():
    
    children: List["MapWidget"] = []
    def __init__(self):     
        self.children = []   
        

    def draw(self, canvas: np.ndarray, drawOption: MapWidgetDrawOptions=None):
        if(len(self.children) == 0):
            return canvas
        else:
            result = canvas.copy()
            for (childWidget, option) in self.children:
                result = childWidget.draw(result, option if drawOption is None else drawOption)
            return result
    
    

    def addWidget(self, widget, options: MapWidgetDrawOptions):
        self.children.append((widget,options))
        return self
        
    
    
class LegendItem(MapWidget):
    def __init__(self, value, label, color):
        super().__init__()
        self.value = value
        self.label = label
        self.color = color
        
    def draw(self, canvas, drawOption):               

        # draw symbol
        color = imageTool.covertColor2RGB(self.color)
        lt = [int(drawOption.position[0]), int(drawOption.position[1])]
        rb = [int(lt[0] + drawOption.size[1]), int(lt[1] + drawOption.size[1])]
        cv2.rectangle(canvas, lt,rb, color, -1)
        cv2.rectangle(canvas, lt,rb, [0,0,0], 1)


        # draw label
        # (tW,tH),_ = cv2.getTextSize(self.label, drawOption.font, drawOption.fontScale,1 )
        labelPosition = (
            drawOption.position[0] + drawOption.size[1] + 5,  # posX + symbolWidth + margin
            drawOption.position[1] + (drawOption.size[1] - drawOption.fontSize) / 2   # posY but center align
        )

        imageTool.drawText(canvas,  
                           self.label, 
                           labelPosition,                            
                           fontSize=drawOption.fontSize,                            
                           editRaw=True)
                
        return canvas


class Legend(MapWidget):
    def __init__(self, title=None):
        super().__init__()
        self.title = title
        self.items = []
    
    def setTitle(self, title):
        self.title = title
        
    def addItem(self, value, label, color):
        self.addWidget(LegendItem(value, label, color), MapWidgetDrawOptions())
    def addItemFromColorMapItem(self, colorMapItem: imageTool.ColorMapItem):
        self.addItem(colorMapItem.value, colorMapItem.label, colorMapItem.color)
    def addItemsFromColorMap(self,colorMap: List[imageTool.ColorMapItem]):
        for item in colorMap:
            self.addItemFromColorMapItem(item)

    def addWidget(self, widget, options: MapWidgetDrawOptions):
        return super().addWidget(widget, options)
    
    def draw(self, canvas, drawOption):   
        originalItemHeight = 30
        originalMargin = 10
        originFontSize = 12

        _tempSize = len(self.children) * (originalItemHeight + originalMargin) + originalMargin + originFontSize
           

        # font = cv2.FONT_HERSHEY_SIMPLEX      
        # text_size, _ = cv2.getTextSize("测试", font, 1, 2)
        # _tempSize = _tempSize + text_size[1] + 5

        
        sizeRatio = _tempSize / drawOption.size[1]        
        itemHeight = originalItemHeight * sizeRatio
        # 根据初始尺寸和drawOption.size的比例，调整字体大小
        # fontScaleRatio = sizeRatio 
        # * 1.5
        # fontScale = 1 * fontScaleRatio
        margin = originalMargin * sizeRatio
        fontSize = originFontSize * sizeRatio

        _temp = imageTool.creatBlankImage(drawOption.size, drawOption.background)        

        offsetHeight = 0
        if(self.title is not None):
            # draw title
            _temp= imageTool.drawText(_temp, 
                                                        self.title, 
                                                        (0, 0),                                                        
                                                        fontSize = fontSize,                                                        
                                                        color='#000',
                                                        editRaw=True)
            offsetHeight = fontSize + margin*2

        for (childWidget, option) in self.children:
            option.size = (drawOption.size[0], itemHeight)
            option.position = (0, offsetHeight)
            option.setOptions("fontSize", fontSize)
            _temp = childWidget.draw(_temp, option)
            offsetHeight = offsetHeight + itemHeight + margin        

        return imageTool.draw(canvas, _temp, drawOption.position)
    


class AxisBox(MapWidget):
    def __init__(self,geoTransform, width, height, xAxisNum = 5, yAxisNum = 3):
        '''
        geoTransform : (x0, pw, _, y0, _, ph) ; can get from gdal dataset.GetGeoTransform()
        '''
        super().__init__()
        (x0, pw, _, y0, _, ph)  = geoTransform

        self.XAxis = (x0, x0 + pw * width)
        self.YAxis = (y0, y0 + ph * height)
        self.xAxisNum = xAxisNum
        self.yAxisNum = yAxisNum
        self.extentFrom = None
    
    def extentGeoAreaByLocalDrawAreaFrom(self,drawOption):
        '''
        这里只算线性的扩展，不考虑非线性的扩展
        '''
        self.extentFrom = drawOption
        return self

        
        
    def draw(self, canvas, drawOption):     
        image = Image.fromarray(canvas)
        # 创建绘图对象
        draw = ImageDraw.Draw(image)
        fp = os.path.abspath(drawOption.fontFamily)    
        font = ImageFont.truetype(fp, size=drawOption.fontSize, encoding="utf-8")

        axisLineColor = (0,0,0)
        axisLineWidth = 1
        axisLineStepHeight = 5


        if(self.extentFrom is not None):
            # sizeDiff = (drawOption.size[0] - self.extentFrom.size[0], drawOption.size[1] - self.extentFrom.size[1])
            # positionDiff = (drawOption.position[0] - self.extentFrom.position[0], drawOption.position[1] - self.extentFrom.position[1])
            # extentHeightRatio = sizeDiff[1] / self.extentFrom.size[1]
            # extentWidthRatio = sizeDiff[0] / self.extentFrom.size[0]
            
            geoXperPixel = (self.XAxis[1] - self.XAxis[0])/self.extentFrom.size[0]
            geoYperPixel = (self.YAxis[1] - self.YAxis[0])/self.extentFrom.size[1]

            geoXStartNew = (drawOption.position[0] - self.extentFrom.position[0]) * geoXperPixel + self.XAxis[0]
            geoXEndNew = (drawOption.position[0] + drawOption.size[0] - self.extentFrom.position[0] - self.extentFrom.size[0]) * geoXperPixel + self.XAxis[1]

            geoYStartNew = (drawOption.position[1] - self.extentFrom.position[1]) * geoYperPixel + self.YAxis[0]
            geoYEndNew = (drawOption.position[1] + drawOption.size[1] - self.extentFrom.position[1] - self.extentFrom.size[1]) * geoYperPixel + self.YAxis[1]

            XGeoStep = np.linspace(geoXStartNew, geoXEndNew, self.xAxisNum)
            YGeoStep = np.linspace(geoYStartNew, geoYEndNew, self.yAxisNum)
        
            
        else:        
            XGeoStep = np.linspace(self.XAxis[0], self.XAxis[1], self.xAxisNum)
            YGeoStep = np.linspace(self.YAxis[0], self.YAxis[1], self.yAxisNum)

        startXPoistion = drawOption.position[0]
        endXPoistion = drawOption.position[0] + drawOption.size[0]


        XPositionStep = np.linspace(startXPoistion, endXPoistion, self.xAxisNum)
        
        

        startYPoistion = drawOption.position[1]
        endYPoistion = drawOption.position[1] + drawOption.size[1]
        YPositionStep = np.linspace(startYPoistion, endYPoistion, self.yAxisNum)
        


        for x, geoX in zip(XPositionStep, XGeoStep):
            # draw 上方的线
            draw.line([(startXPoistion, startYPoistion), (endXPoistion, startYPoistion)], fill=axisLineColor, width=axisLineWidth)
            text = decimal_to_dms(geoX, True)
            textSize = font.getbbox(text)
            textSize = (textSize[2] - textSize[0], textSize[3] - textSize[1])
            x = int(x)
            # step
            topLineYB = startYPoistion
            topLineYT = topLineYB - axisLineStepHeight
            draw.line([(x, topLineYB), (x, topLineYT)], fill=axisLineColor, width=axisLineWidth)
            # add label
            draw.text((x - int(textSize[0]/2), topLineYB - axisLineStepHeight - textSize[1]),text, fill=axisLineColor,font=font)

            # draw 下方的线
            draw.line([(startXPoistion, endYPoistion), (endXPoistion, endYPoistion)], fill=axisLineColor, width=axisLineWidth)
            bottomLineYB = endYPoistion + axisLineStepHeight
            bottomLineYT = bottomLineYB - axisLineStepHeight
            draw.line([(x, bottomLineYB), (x, bottomLineYT)], fill=axisLineColor, width=axisLineWidth)
            # add label
            draw.text((x -int(textSize[0]/2) , bottomLineYB), text, fill=axisLineColor,font=font)
        

        for y, geoY in zip(YPositionStep, YGeoStep):
            # draw 左边的线
            draw.line([(startXPoistion, startYPoistion), (startXPoistion, endYPoistion)], fill=axisLineColor, width=axisLineWidth)
            text = decimal_to_dms(geoY, True)
            textSize = font.getbbox(text)
            textSize = (textSize[2] - textSize[0], textSize[3] - textSize[1])
            y = int(y)
            # step
            leftLineXR = startXPoistion
            leftLineXL = leftLineXR - axisLineStepHeight
            draw.line([(leftLineXL, y), (leftLineXR, y)], fill=axisLineColor, width=axisLineWidth)
            # add label

            # # 逐个字符绘制文本
            # _y = y - int(textSize[0]/2)
            # for char in text:
            #     _labelImage = imageTool.getVerTextImage(char,drawOption.fontSize,drawOption.fontFamily, axisLineColor)
            #     _labelImage = Image.fromarray(_labelImage)
            #     image.paste(_labelImage, (leftLineXL, _y))
            #     # draw.text((leftLineXL - textSize[0], _y), char, font=font, fill='black')
            #     _y += textSize[1]  # 每绘制一个字符，y 坐标增加字符的高度

            # _labelImage = Image.fromarray(_labelImage)
            # image.paste(_labelImage, (leftLineXL - textSize[1], y - int(textSize[0]/2)))
            # draw.text((leftLineXL - textSize[0], y - int(textSize[1]/2)),text, fill=axisLineColor)
            draw.text((leftLineXL - textSize[0] -1, y - int(textSize[1]/2) + 0.5),text, fill=axisLineColor,font=font)

            # draw 右边的线
            rightLineXL = endXPoistion
            rightLineXR = rightLineXL + axisLineStepHeight
            draw.line([(endXPoistion, startYPoistion), (endXPoistion, endYPoistion)], fill=axisLineColor, width=axisLineWidth)
            draw.line([(rightLineXL, y), (rightLineXR, y)], fill=axisLineColor, width=axisLineWidth)
            # add label
            draw.text((rightLineXR+1, y - int(textSize[1]/2)), text, fill=axisLineColor,font=font)



        canvas[:,:,:] = np.array(image)
        return canvas                
       

class MapGrid(MapWidget):
    def __init__(self):
        super().__init__()
        self.images = []

    def addImage(self, image: np.ndarray):
        self.images.append(image)
    
    def draw(self, canvas, drawOption):                     
        tempImge = imageTool.fuseImages(self.images, imageTool.ImageFuseType.overlay)
        tempImge = imageTool.scaleImage(tempImge, drawOption.size)
        return imageTool.draw(canvas, tempImge, drawOption.position)



class MapDocument(MapWidget):
    def __init__(self, options: MapWidgetDrawOptions=None):        
        super().__init__()
        self.size = options.size
        self.background = options.background
        self.title = "Map"
        
        self.clear()
        
        
    def clear(self):
        self._canvas = np.zeros((self.size[1],self.size[0],3),dtype=np.uint8)
        bgColor = imageTool.covertColor2RGB(self.background) 
        # fill with bg color
        self._canvas[:,:] = bgColor
        return self
    
    def resize(self, size):
        self.size = size
        __temp = self._canvas
        self.clear()
        self._canvas = imageTool.draw(self._canvas, __temp, (0,0))
        return self
    
    def preview(self):
        self._canvas = self.draw(canvas=self._canvas)     
        # rgb 2 bgr        
        cv2.imshow(self.title, cv2.cvtColor(self._canvas, cv2.COLOR_RGB2BGR))
        return self
   
    
    def save(self, filePath:str):
        self._canvas = self.draw(canvas=self._canvas)
        cv2.imwrite(filePath, cv2.cvtColor(self._canvas, cv2.COLOR_RGB2BGR))        
        return self