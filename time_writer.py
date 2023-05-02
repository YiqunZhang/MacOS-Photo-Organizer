import os
import xml.etree.ElementTree as ET
import datetime
import tqdm


def get_timestamp_from_xmp(xmp_path, time_zone):
    tree = ET.parse(xmp_path)
    namespace = {'photoshop': 'http://ns.adobe.com/photoshop/1.0/'}
    time_str = tree.find(".//photoshop:DateCreated", namespace).text
    creation_time_utc = datetime.datetime.fromisoformat(time_str)
    timestamp_utc = creation_time_utc.replace(tzinfo=None).timestamp()
    timestamp = timestamp_utc + time_zone * 3600

    return timestamp


def set_file_birth_time(file_path, timestamp):
    atime = os.path.getatime(file_path)
    date_str = datetime.datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y %H:%M:%S')
    os.system(f'SetFile -d "{date_str}" "{file_path}"')
    os.utime(file_path, (atime, timestamp))


def get_file_groups(path):
    file_groups = {}

    for filename in os.listdir(path):
        # 确保是文件，跳过目录
        if os.path.isfile(os.path.join(path, filename)):
            # 分离文件名和扩展名
            name, ext = os.path.splitext(filename)
            ext = ext.lstrip('.')

            # 将文件添加到组中
            if name in file_groups:
                file_groups[name] = file_groups[name] + (ext,)
            else:
                file_groups[name] = (ext,)

    return file_groups


def time_writer(path, time_zone):
    for file in tqdm.tqdm(os.listdir(path)):
        sub_path = os.path.join(path, file)
        if not os.path.isdir(sub_path):
            continue

        file_group_dict = get_file_groups(sub_path)
        for name, suffix_tuple in file_group_dict.items():
            if 'xmp' not in suffix_tuple:
                continue
            timestamp = get_timestamp_from_xmp(os.path.join(sub_path, name + '.xmp'), time_zone)
            for suffix in suffix_tuple:
                file_path = os.path.join(sub_path, name + '.' + suffix)
                set_file_birth_time(file_path, timestamp)


if __name__ == '__main__':
    # 求差集输出文件夹路径
    path = '/Users/zhangyiqun/Desktop/D-iCloud图库清理/F-第一次清理-删除部分-2023.5.2'
    # 时区, [-12,12] 的整数
    time_zone = 10
    time_writer(path, time_zone)
