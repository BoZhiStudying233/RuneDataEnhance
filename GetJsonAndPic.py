import os
import shutil


def find_image_files(file_names, json_file_name):
    file_name_without_ext = os.path.splitext(json_file_name)[0]
    image_files = []
    for image_file in file_names:
        if image_file.startswith(file_name_without_ext) and not image_file.endswith('.json'):
            image_files.append(image_file)
    return image_files


def extract_files(folder_path, output_folder):
    print(f"Processing folder: {folder_path}")

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 获取文件夹中所有的文件名
    file_names = os.listdir(folder_path)
    print(f"Files found: {file_names}")

    # 提取JSON文件和对应的图片文件
    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.json'):
            print(f"Processing JSON file: {file_name}")
            try:
                # 复制JSON文件到输出文件夹
                shutil.copy(file_path, output_folder)

                # 查找与JSON文件名相同的图片文件
                image_files = find_image_files(file_names, file_name)
                for image_file in image_files:
                    image_path = os.path.join(folder_path, image_file)
                    print(f"Processing image file: {image_file}")
                    # 复制图片文件到输出文件夹
                    shutil.copy(image_path, output_folder)
            except Exception as e:
                print(f"Error processing file: {file_path}")
                print(f"Error message: {str(e)}")


# 指定输入文件夹和输出文件夹路径
input_folder = r'V:\XDU\contest\RM\Data_set\q\q1'
output_folder = r'V:\XDU\contest\RM\Data_set\q\q0'

# 调用函数提取文件
extract_files(input_folder, output_folder)