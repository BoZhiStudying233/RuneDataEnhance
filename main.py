import json
import os
import cv2
import yaml
import random
import numpy as np
import sys

# name2id = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5}
name2id = {'0': 0}
name2img = ['origin', 'convert']
name2mark = ['none', 'salt', 'gaussian', 'Blur', 'Brighter']
type2path = ['train', 'test', 'val']

def CalFilePath(data_file):
    # 新建文件夹
    if(not os.path.exists(data_file['train_path'])):
            os.mkdir(data_file['train_path'])
    if(not os.path.exists(data_file['test_path'])):
            os.mkdir(data_file['test_path'])
    if(not os.path.exists(data_file['val_path'])):
            os.mkdir(data_file['val_path'])

    val_image_path = data_file['val_path'] + 'images//'
    val_label_path = data_file['val_path'] + 'labels//'

    if(not os.path.exists(val_image_path)):
            os.mkdir(val_image_path)
    if(not os.path.exists(val_label_path)):
            os.mkdir(val_label_path)

    # 确定存储文件夹
    seed = random.random()
    if seed < data_file["train_rate"]:
        return data_file['train_path'], type2path[0]
    elif seed > data_file["train_rate"] and seed < data_file['test_rate'] + data_file["train_rate"]:
        return data_file['test_path'], type2path[1]
    else:
        return data_file['val_path'], type2path[2]


def decode_json(origin_data_path, txt_outer_path, whole_type, whole_name):

    print(whole_name)
    if whole_type[0] == type2path[2]:
        txt_name = txt_outer_path + 'labels/' + whole_name[0] + '_' + whole_name[1] + '_' + whole_name[2] + '_' + whole_name[3] + '.txt'
    else:
        txt_name = txt_outer_path + whole_name[0] + '_' + whole_name[1] + '_' + whole_name[2] + '_' + whole_name[3] + '.txt'

    with open(txt_name, 'w') as f:
        json_name = whole_name[3] + ".json"
        json_path = os.path.join(origin_data_path, json_name)  # os路径融合
        data = json.load(open(json_path, 'r', encoding='gb2312', errors='ignore'))
        img_w = data['imageWidth']  # 图片的高
        img_h = data['imageHeight']  # 图片的宽
        isshape_type = data['shapes'][0]['shape_type']
        # print("类型："+ isshape_type)
        # print(isshape_type)
        # print('下方判断根据这里的值可以设置为你自己的类型，我这里是polygon'多边形)
        # len(data['shapes'])
        for i in data['shapes']:
            label_name = i['label']  # 得到json中你标记的类名

            if(label_name == 'dog'):
                label_name = '0'

            if whole_name[1] == name2img[1]:
                if int(label_name) > 2 :
                    label_name = str(int(label_name) - 3)
                else :
                    label_name = str(int(label_name) + 3)

            # print("标签名：{}".format(label_name))
            if int(label_name) < 0 or int(label_name) > 5 :
                print("文件名为{}的数据有误".format((json_name)))
                sys.exit(0)

            data_points = []
            # if (i['shape_type'] == 'polygon'):  # 数据类型为多边形 需要转化为矩形
            x_max = 0
            y_max = 0
            x_min = 1
            y_min = 1

            for lk in range(len(i['points'])):
                x1 = float(i['points'][lk][0]) / img_w
                y1 = float(i['points'][lk][1]) / img_h
                # print(x1)

                # 寻找极值点，确定外接矩形长和宽
                if x_max < x1:
                    x_max = x1
                if y_max < y1:
                    y_max = y1
                if y_min > y1:
                    y_min = y1
                if x_min > x1:
                    x_min = x1

                data_points.append(x1)
                data_points.append(y1)

            # 1.42,1.04为超参数;扩展w,h
            w = x_max - x_min
            h = y_max - y_min
            if w < h : #小的边为宽
                w *= 1.42
                h *= 1.04
            else:
                w *= 1.04
                h *= 1.42

            if w > 1 or h > 1:
                w = 1
                h = 1

            bb = [(x_max+x_min) / 2, (y_max+y_min) / 2, w, h]


            # if (i['shape_type'] == 'rectangle'):  # 为矩形不需要转换
            #     x1 = float(i['points'][0][0])
            #     y1 = float(i['points'][0][1])
            #     x2 = float(i['points'][1][0])
            #     y2 = float(i['points'][1][1])
            #     bb = (x1, y1, x2, y2)

            # print("bb",bb)
            # print("data_points",data_points)
            # bbox_points = bb + data_points
            bbox_points = bb

            try:
                f.write(str(name2id[label_name]) + " " + " ".join([str(a) for a in bbox_points]) + '\n')
            except:
                pass


def WriteData(origin_data_path, txt_outer_path, whole_type, whole_name, img):
    # 写原图
    # 写txt文件
    decode_json(origin_data_path, txt_outer_path, whole_type, whole_name)
    # 写图片
    if whole_type[0] == type2path[2]:
        img_path = txt_outer_path + 'images//' + whole_name[0] + '_' + whole_name[1] + '_' + whole_name[2] + '_' + whole_name[3] + '.' + whole_type[1]
    else:
        img_path = txt_outer_path + whole_name[0] + '_' + whole_name[1] + '_' + whole_name[2] + '_' + whole_name[3] +  '.' + whole_type[1]
    cv2.imwrite(img_path, img)


# 椒盐噪声
def SaltAndPepper(src,percetage = 0.08):
    SP_NoiseImg=src.copy()
    SP_NoiseNum=int(percetage*src.shape[0]*src.shape[1])
    for i in range(SP_NoiseNum):
        randR=np.random.randint(0,src.shape[0]-1)
        randG=np.random.randint(0,src.shape[1]-1)
        randB=np.random.randint(0,3)
        if np.random.randint(0,1)==0:
            SP_NoiseImg[randR,randG,randB]=0
        else:
            SP_NoiseImg[randR,randG,randB]=255
    return SP_NoiseImg

# 高斯噪声
def GaussianNoise(image,percetage = 0.08):
    G_Noiseimg = image.copy()
    w = image.shape[1]
    h = image.shape[0]
    G_NoiseNum=int(percetage*image.shape[0]*image.shape[1])
    for i in range(G_NoiseNum):
        temp_x = np.random.randint(0,h)
        temp_y = np.random.randint(0,w)
        G_Noiseimg[temp_x][temp_y][np.random.randint(3)] = np.random.randn(1)[0]
    return G_Noiseimg

# 高斯滤波
def Blur(img):
    blur = cv2.GaussianBlur(img, (7, 7), 1.5)
    # #      cv2.GaussianBlur(图像，卷积核，标准差）
    return blur

# 明亮
def Brighter(image, percetage=1.5):
    image_copy = image.copy()
    w = image.shape[1]
    h = image.shape[0]
    #get brighter
    for xi in range(0,w):
        for xj in range(0,h):
            image_copy[xj,xi,0] = np.clip(int(image[xj,xi,0]*percetage),a_max=255,a_min=0)
            image_copy[xj,xi,1] = np.clip(int(image[xj,xi,1]*percetage),a_max=255,a_min=0)
            image_copy[xj,xi,2] = np.clip(int(image[xj,xi,2]*percetage),a_max=255,a_min=0)
    return image_copy

# 场景变换
def SceneTranformation(image,roi, roi_rect, scene_img_path):
    scene = cv2.imread(scene_img_path)
    scene = cv2.resize(scene, image.shape)
    scene[roi_rect.y: roi_rect.y+roi_rect.height, roi_rect.x:roi_rect.x+roi_rect.width] = roi
    return scene

if __name__ == '__main__':
    # 打开yaml文件
    with open('./data.yaml', 'r', encoding='utf8') as file:
        data_file = yaml.safe_load(file)
    # print(data_file)

    origin_datas = os.listdir(data_file['origin_data_path'])
    print("共有：{}个文件待转化".format(len(origin_datas) / 2))
    flagcount = 0

    special_name = data_file['school_name'] + "_" + data_file['origin_data_path'].split('/')[-2]#即学校名字+源数据集路径的上一个文件夹名

    # 定义上一个类型与文件名
    last_name = 'null'
    last_type = 'png'

    # 确定有多少待处理文件
    delay_json_num = 0
    all_json_num = 0
    for origin_data in origin_datas:
        type = origin_data.split(".")[-1]
        if (type == 'json'):
            all_json_num += 1

    print("有{}个文件待处理".format(all_json_num))

    for origin_data in origin_datas:
        name = origin_data.split(".")[0]
        type = origin_data.split(".")[-1]

        if type != 'json':  #设置了格式，
            continue

        #json文件与图片对应
        img_type = 'png'


        img = cv2.imread(data_file['origin_data_path'] + name + '.' + img_type)

        # 写原图
        #确定txt存储路径
        txt_outer_path, path_type = CalFilePath(data_file)
        whole_type = [path_type, img_type]
        whole_name = [special_name, name2img[0], name2mark[0], name]
        # print(whole_name)
        # print((whole_type))
        WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, img)
        flagcount += 1

        # 使图片产生椒盐噪声
        seed = random.random()
        if(seed < data_file['salt_rate']):
            img_salt = SaltAndPepper(img)
            txt_outer_path, path_type = CalFilePath(data_file)
            whole_type = [path_type, img_type]
            whole_name = (special_name, name2img[0], name2mark[1], name)
            WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, img_salt)
            flagcount += 1

        # 使图片产生高斯噪声 -
        seed = random.random()
        if(seed < data_file['gaussian_rate']):
            img_guassian = GaussianNoise(img)
            txt_outer_path, path_type = CalFilePath(data_file)
            whole_type = [path_type, img_type]
            whole_name = (special_name, name2img[0], name2mark[2], name)
            WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, img_guassian)
            flagcount += 1

        # 使图片产生高斯滤波
        seed = random.random()
        if(seed < data_file['gaussian_rate']):
            img_blur = Blur(img)
            txt_outer_path, path_type = CalFilePath(data_file)
            whole_type = [path_type, img_type]
            whole_name = (special_name, name2img[0], name2mark[3], name)
            WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, img_blur)
            flagcount += 1

        # 使图片增亮
        seed = random.random()
        if(seed < data_file['Brighter_rate']):
            img_brighter = Brighter(img)
            txt_outer_path, path_type = CalFilePath(data_file)
            whole_type = [path_type, img_type]
            whole_name = (special_name, name2img[0], name2mark[4], name)
            WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, img_brighter)
            flagcount += 1

        # 写转换后的图
        if data_file['is_transform'] == 1:
            img_b,img_g,img_r = cv2.split(img)
            convert_img = cv2.merge([img_r, img_g, img_b])
            #确定txt存储路径
            txt_outer_path, path_type = CalFilePath(data_file)
            whole_type = [path_type, img_type]
            whole_name = (special_name, name2img[1], name2mark[0], name)
            WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, convert_img)
            flagcount += 1

            # 使图片产生椒盐噪声
            seed = random.random()
            if(seed < data_file['salt_rate']):
                convert_img_salt = SaltAndPepper(convert_img)
                txt_outer_path, path_type = CalFilePath(data_file)
                whole_type = [path_type, img_type]
                whole_name = (special_name, name2img[1], name2mark[1], name)
                WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, convert_img_salt)
                flagcount += 1

            # 使图片产生高斯噪声
            seed = random.random()
            if(seed < data_file['gaussian_rate']):
                convert_img_guassian = GaussianNoise(convert_img)
                txt_outer_path, path_type = CalFilePath(data_file)
                whole_type = [path_type, img_type]
                whole_name = (special_name, name2img[1], name2mark[2], name)
                WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, convert_img_guassian)
                flagcount += 1

            # 使图片产生高斯滤波
            seed = random.random()
            if(seed < data_file['gaussian_rate']):
                convert_img_blur = Blur(convert_img)
                txt_outer_path, path_type = CalFilePath(data_file)
                whole_type = [path_type, img_type]
                whole_name = (special_name, name2img[1], name2mark[3], name)
                WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, convert_img_blur)
                flagcount += 1

            # 使图片增亮
            seed = random.random()
            if(seed < data_file['Brighter_rate']):
                img_brighter = Brighter(convert_img)
                txt_outer_path, path_type = CalFilePath(data_file)
                whole_type = [path_type, img_type]
                whole_name = (special_name, name2img[0], name2mark[4], name)
                WriteData(data_file['origin_data_path'], txt_outer_path, whole_type, whole_name, img_brighter)
                flagcount += 1

        delay_json_num += 1
        print("转化完成文件：{}".format(delay_json_num))
        print("未转化文件：{}".format(all_json_num - delay_json_num))
        print("转化后目标总文件数量：{}".format((flagcount)))
        print("\n")