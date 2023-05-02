import os
import shutil
import tqdm


def get_difference(source_1, source_2, target):
    # 创建目标文件夹，如果不存在
    if not os.path.exists(target):
        os.makedirs(target)

    # 获取s1中的所有文件
    print("正在获取 source_1 文件列表")
    s1_files = []
    for root, _, files in os.walk(source_1):
        for file in files:
            s1_files.append(os.path.join(root, file))

    # 使用进度条遍历s1中的所有文件
    for file_source_1 in tqdm.tqdm(s1_files, desc="正在求差集", unit="files"):
        file_source_2 = file_source_1.replace(source_1, source_2)  # s2中的文件路径
        file_target = file_source_1.replace(source_1, target)  # t中的文件路径

        # 如果文件在s1中存在但在s2中不存在，则将其复制到t中
        if not os.path.exists(file_source_2):
            target_folder = os.path.dirname(file_target)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            shutil.copy(file_source_1, file_target)

if __name__ == '__main__':
    # 第一次导出的文件夹路径
    source_1 = '/Users/zhangyiqun/Desktop/D-iCloud图库清理/F-完整备份-从MacOS照片导出-2023.5.1'
    # 第二次导出的文件夹路径
    source_2 = '/Users/zhangyiqun/Desktop/D-iCloud图库清理/F-第一次清理-从MacOS照片导出-2023.5.2'
    # 输出文件夹路径
    target = '/Users/zhangyiqun/Desktop/D-iCloud图库清理/F-第一次清理-删除部分-2023.5.2'

    get_difference(source_1, source_2, target)
