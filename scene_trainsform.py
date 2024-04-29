import cv2
import yaml
import os
import random
import shutil

# 随机读取某一文件夹下的任意一张图片路径作为背景
def getScene(scene_path):
    image_files = [file for file in os.listdir(scene_path) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    if len(image_files) == 0:
        raise ValueError('文件夹中没有符合条件的图片文件。')

    random_image = random.choice(image_files)
    random_image_path = os.path.join(scene_path, random_image)
    scene = cv2.imread(random_image_path)
    return scene

# 将roi绘画至场景
def DrawData(scene, roi_dict):
    scene = cv2.resize(scene, (roi_dict['img'].shape[1], roi_dict['img'].shape[0]))
    roi = roi_dict['img'][int(roi_dict['y1']):int(roi_dict['y2']), int(roi_dict['x1']):int(roi_dict['x2'])]
    scene[int(roi_dict['y1']):int(roi_dict['y2']), int(roi_dict['x1']):int(roi_dict['x2'])] = roi
    # roi_rect = cv2.rect(roi_dict['x1'],roi_dict['y1'],roi_dict['roi_w'], roi_dict['roi_h'])
    # roi_dict['img'].cv2.copyTo(scene(roi_rect))
    return scene

if __name__ == '__main__':

    # 打开yaml文件
    with open('./txt_data.yaml', 'r', encoding='utf8') as file:
        data_file = yaml.safe_load(file)

    origin_datas = os.listdir(data_file['origin_data_path'])
    print("共有：{}个文件待转化".format(len(origin_datas) / 2))
    flagcount = 0

    # 定义上一个类型与文件名
    last_name = 'null'
    last_type = 'jpg'

    # 确定有多少待处理文件
    delay_txt_num = 0
    all_txt_num = 0
    for origin_data in origin_datas:
        type = origin_data.split(".")[-1]
        if (type == 'txt'):
            all_txt_num += 1

    print("有{}个文件待处理".format(all_txt_num))
    finish_num = 0

    for origin_data in origin_datas:
        name = origin_data.split(".")[0]
        type = origin_data.split(".")[-1]
        #txt文件与图片对应
        if name == last_name and type != last_type :
            # 确定类型
            if(type == 'txt'):
                img_type = "." + last_type
            else:
                img_type = "." + type

            img = cv2.imread(data_file['origin_data_path'] + name + img_type)
            txt_path = data_file['origin_data_path'] + name + ".txt"

            seed = random.random()
            if seed < data_file["scene_transformation"] :
                with open(txt_path, "r") as label:
                    # 随机选择一张背景
                    scene = getScene(data_file["scene_path"])

                    for line in label.readlines():

                        curLine = line.strip().split(" ")
                        floatLine = map(float, curLine)
                        floatLine = list(floatLine)

                        height, width = img.shape[:2]

                        roi_w = floatLine[3]*width
                        roi_h = floatLine[4]*height
                        point1_x = floatLine[1]*width - roi_w / 2
                        point1_y = floatLine[2]*height - roi_h / 2
                        point2_x = floatLine[1]*width + roi_w / 2
                        point2_y = floatLine[2]*height + roi_h / 2

                        temp_dict = {'img':img,'x1':point1_x, 'y1':point1_y,'x2':point2_x, 'y2':point2_y,'roi_w':roi_w,'roi_h':roi_h}

                        scene = DrawData(scene,temp_dict)
                    label.close()
                # 存储图片
                save_img_path = data_file['save_path'] + "scene_" + name + img_type
                cv2.imshow(save_img_path, scene)
                cv2.waitKey(0)
                print(save_img_path)
                cv2.imwrite("D:\IROBOT\MyCode/buff\DataEnhance/temp/test/scene_origin.jpg", scene)
                # 存储txt文件
                save_txt_path = data_file['save_path'] + "scene_" + name + ".txt"
                # shutil.copy(txt_path, save_txt_path)

                finish_num += 1
                print("已完成转化:{}".format(finish_num))

        last_name = name
        last_type = type