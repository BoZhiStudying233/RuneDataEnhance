# 能量机关数据增强
## main.py
总处理文件
### 功能
将原图进行处理，按概率进行椒盐噪声、高斯噪声等处理，概率调节可在data.yaml进行。
把json文件转化为txt文件
把图像按比例放到train，val，test文件夹里。
主要配置全部在data.yaml里进行设置。
## GetJsonAndPic.py
### 功能
把包含已标注的图片（有对应的json文件）和未标注的图片（无json文件的）区分开来，把已经标注过的提取到相应文件夹里。
## scene_trainsform.py
进行场景变换，暂时没试过

