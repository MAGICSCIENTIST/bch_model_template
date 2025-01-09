import os
import sys
import pickle
import numpy as np
from osgeo import ogr, gdal, gdalconst
import utils.graph_utils as graph_utils


def getFileList(path, ext=".p"):
	# check path is folder or file
	if os.path.isfile(path):
		return [path]
	elif os.path.isdir(path):
		# 递归获取所有文件
		fileList = []
		for root, dirs, files in os.walk(path):
			for file in files:
				if file.endswith(ext):
					fileList.append(os.path.join(root, file))
		return fileList