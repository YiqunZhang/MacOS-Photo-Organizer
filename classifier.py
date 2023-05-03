import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFile
import os
import xml.etree.ElementTree as ET
import tqdm
import collections
from pillow_heif import register_heif_opener
import shutil
import time
from PIL.ExifTags import TAGS
import csv

register_heif_opener()
image_extension_list = ['jpg', 'jpeg', 'png', 'heic', 'heif', 'gif', 'JPG', 'JPEG', 'PNG', 'HEIC', 'HEIF', 'GIF']


class GPSConverter():
    def __init__(self, data_path_list):
        self.data_path_list = data_path_list
        self.address_list = []
        self._load_geonames_data()

    def _load_geonames_data(self):
        print("正在加载地理位置数据库")
        for data_path in self.data_path_list:
            with open(data_path, encoding="utf-8") as file:
                reader = csv.reader(file, delimiter="\t")
                for row in reader:
                    city = {
                        'name1': row[1],
                        'name2': row[3].split(',')[-1],
                        'latitude': float(row[4]),
                        'longitude': float(row[5])
                    }
                    self.address_list.append(city)

    def get_address(self, lat, lon):
        address_1 = ''
        address_2 = ''

        nearest_distance = float('inf')

        for address in self.address_list:
            distance = ((address['latitude'] - lat) ** 2 + (address['longitude'] - lon) ** 2) ** 0.5
            if distance < nearest_distance:
                nearest_distance = distance
                address_1 = address['name1']
                address_2 = address['name2']

        return address_1, address_2


class ClassDetail():
    def __init__(self, name, target_path, move_xmp, filename_attach_location, filename_attach_time):
        self.name = name
        self.target_path = target_path
        self.move_xmp = move_xmp
        self.filename_attach_location = filename_attach_location
        self.filename_attach_time = filename_attach_time


class DisplayApp(tk.Tk):
    def __init__(self, classifier, gps_converter, class_trash, class_list):
        super().__init__()
        self.classifier = classifier
        self.class_trash = class_trash
        self.class_list = class_list
        self.gps_converter = gps_converter

        self.attributes("-fullscreen", True)
        self.title('MacOS 照片整理器')
        self.configure(bg='gray')

        # 左侧信息栏
        self.label_info = tk.Label(self, text='', bg='white', font=('Arial', 25), anchor='nw', justify='left',
                                   padx=20, pady=20, wraplength=410)
        self.label_info.place(x=50, y=50, width=450, height=650)

        self.label_progress = tk.Label(self, text='0 / 0', bg='white', font=('Arial', 35), foreground='#CC0033',
                                       padx=20, pady=20)
        self.label_progress.place(x=50, y=750, width=450, height=100)

        # 右侧分类区

        self.frame_classifier = tk.Frame(self, bg='white')
        self.frame_classifier.place(x=1400, y=50, width=350, height=800)

        self.button_C0 = tk.Button(self.frame_classifier, text=self.class_list[0].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[0]))
        self.button_C0.pack(side=tk.TOP, fill=tk.X, padx=20, pady=15)
        self.button_C1 = tk.Button(self.frame_classifier, text=self.class_list[1].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[1]))
        self.button_C1.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.button_C2 = tk.Button(self.frame_classifier, text=self.class_list[2].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[2]))
        self.button_C2.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.button_C3 = tk.Button(self.frame_classifier, text=self.class_list[3].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[3]))
        self.button_C3.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.button_C4 = tk.Button(self.frame_classifier, text=self.class_list[4].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[4]))
        self.button_C4.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.button_C5 = tk.Button(self.frame_classifier, text=self.class_list[5].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[5]))
        self.button_C5.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.button_C6 = tk.Button(self.frame_classifier, text=self.class_list[6].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[6]))
        self.button_C6.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.button_C7 = tk.Button(self.frame_classifier, text=self.class_list[7].name, font=('Arial', 25),
                                   command=lambda: self._operatioan_move(self.class_list[7]))
        self.button_C7.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

        self.label_revoke = tk.Label(self.frame_classifier, text='', font=('Arial', 25))
        self.label_revoke.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        self.button_revoke = tk.Button(self.frame_classifier, text='撤销一步', font=('Arial', 25), foreground='blue',
                                       command=self._operatioan_revoke)
        self.button_revoke.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        self.button_skip = tk.Button(self.frame_classifier, text='跳过', font=('Arial', 25), foreground='green',
                                     command=self._operatioan_skip)
        self.button_skip.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        self.button_delete = tk.Button(self.frame_classifier, text='删除', font=('Arial', 25), foreground='red',
                                       command=lambda: self._operatioan_delete())
        self.button_delete.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        # 画布
        self.label_image = tk.Label(self, bg='white')
        self.label_image.place(x=550, y=50, width=800, height=800)

        self._load_next_image()

    def _operatioan_skip(self):
        self.classifier.move_description = '跳过'
        self._load_next_image()

    def _operatioan_delete(self):
        self.classifier.move_description = '删除'
        self.classifier.move_image_group(class_trash.target_path, self.key_current, class_trash.move_xmp,
                                         class_trash.filename_attach_time, class_trash.filename_attach_location)
        self._load_next_image()

    def _load_last_image(self):
        self.classifier.curosr -= 1
        self._laod_image()

    def _load_next_image(self):
        self.classifier.curosr += 1
        self._laod_image()

    def _laod_image(self):
        # load image
        self.key_current = self.classifier.get_curosr_key()
        image = self.classifier.get_image_by_key(self.key_current)
        image.thumbnail((800, 800), Image.ANTIALIAS)
        image_tk = ImageTk.PhotoImage(image)
        self.label_image.config(image=image_tk)
        self.label_image.image = image_tk

        # load revoke description
        self.label_revoke.config(text='可撤销: ' + self.classifier.move_description)

        # load image info
        latitude_str, longitude_str, altitude_str = self.classifier._get_gps_info_from_xmp(
            os.path.join(self.classifier.album_root_path, self.key_current + '.xmp'))

        if latitude_str == '无数据' or longitude_str == '无数据':
            address_name1 = '无数据'
            address_name2 = '无数据'
        else:
            print(float(latitude_str), float(longitude_str))
            address_name1, address_name2 = self.gps_converter.get_address(float(latitude_str), float(longitude_str))

        image_info = ''
        image_info += '时刻组: ' + self.key_current.split('/')[0] + '\n'
        image_info += '文件名: ' + self.key_current.split('/')[1] + '\n'
        image_info += '拓展名: ' + ', '.join(classifier.file_dict[self.key_current]) + '\n'
        image_info += '时间: ' + self.classifier._get_time_str_from_xmp(
            os.path.join(self.classifier.album_root_path, self.key_current + '.xmp')) + '\n'
        image_info += '海拔: ' + altitude_str + '\n'
        image_info += '地点[英]: ' + address_name1 + '\n'
        image_info += '地点[中]: ' + address_name2 + '\n'
        image_info += '\n'

        exif_data = image.getexif()
        for tagid in exif_data:
            tagname = TAGS.get(tagid, tagid)
            value = exif_data.get(tagid)
            image_info += tagname + ': ' + str(value) + '\n'

        self.label_info.config(text=image_info)

        # load progress
        progress_str = str(self.classifier.curosr + 1) + ' / ' + str(len(self.classifier.file_key_list))
        self.label_progress.config(text=progress_str)

    def _operatioan_move(self, class_detail):
        self.classifier.move_description = '分类 ' + class_detail.name
        self.classifier.move_image_group(class_detail.target_path, self.key_current, class_detail.move_xmp,
                                         class_detail.filename_attach_time, class_detail.filename_attach_location)
        self._load_next_image()

    def _operatioan_revoke(self):
        if classifier.move_description == '无':
            return
        elif classifier.move_description == '跳过':
            self._load_last_image()
        else:
            self.classifier.revoke()
            self._load_last_image()
        self.classifier.move_description = '无'
        self.label_revoke.config(text='可撤销: ' + self.classifier.move_description)


class Classifier:
    def __init__(self, album_root_path, log_path, start_index=1):
        self.file_dict = collections.defaultdict(list)
        self.file_key_list = []

        self.album_root_path = album_root_path
        self.log_path = log_path

        self._get_file_list()
        self.curosr = start_index - 2
        self.move_history = []
        self.move_description = '无'

    def get_curosr_key(self):
        return self.file_key_list[self.curosr]

    def get_image_by_key(self, key):
        if key is None:
            image = Image.new('RGB', (256, 256), (0, 0, 0))
        else:
            extension_list = self.file_dict[key]
            extension = None
            for image_extension in image_extension_list:
                if image_extension in extension_list:
                    extension = image_extension
                    break
            image = Image.open(os.path.join(self.album_root_path, key + '.' + extension))
        return image

    def _get_file_list(self):
        for folder in tqdm.tqdm(os.listdir(self.album_root_path), desc="正在扫描文件列表", unit="files"):
            sub_path = os.path.join(self.album_root_path, folder)
            if os.path.isfile(sub_path):
                continue

            for filename in os.listdir(sub_path):
                # 确保是文件，跳过目录
                if os.path.isdir(os.path.join(sub_path, filename)):
                    continue

                # 分离文件名和扩展名
                name, extension = os.path.splitext(filename)
                extension = extension[1:]  # 去掉扩展名前面的点
                self.file_dict[folder + '/' + name].append(extension)

        for key in self.file_dict.keys():
            extension_list = self.file_dict[key]
            has_image_extension = False
            for image_extension in image_extension_list:
                if image_extension in extension_list:
                    has_image_extension = True
                    break
            if has_image_extension:
                self.file_key_list.append(key)

    def _get_time_str_from_xmp(self, xmp_path):
        tree = ET.parse(xmp_path)
        namespace = {'photoshop': 'http://ns.adobe.com/photoshop/1.0/'}
        time_str = tree.find(".//photoshop:DateCreated", namespace).text
        time_str = 'D' + time_str.replace('-', '.').replace(':', '.').replace('+', 'E')

        return time_str

    def _get_gps_info_from_xmp(self, xmp_path):
        try:
            tree = ET.parse(xmp_path)
            namespace = {'exif': 'http://ns.adobe.com/exif/1.0/'}
            latitude_str = tree.find(".//exif:GPSLatitude", namespace).text
            longitude_str = tree.find(".//exif:GPSLongitude", namespace).text
            altitude_str = tree.find(".//exif:GPSAltitude", namespace).text.split('.')[0]
        except:
            latitude_str = '无数据'
            longitude_str = '无数据'
            altitude_str = '无数据'
        return latitude_str, longitude_str, altitude_str

    def move(self, source_path, target_path):
        shutil.move(source_path, target_path)

        log_message = f'MOVE {time.strftime("D%Y.%m.%dT%H.%M.%SL", time.localtime())} {source_path} {target_path}'
        with open(self.log_path, 'a') as f:
            f.write(log_message + '\n')
        # print(log_message)

    def revoke(self):
        for source_path, target_path in self.move_history:
            self.move(target_path, source_path)

    def move_image_group(self, target_dir_path, key, move_xmp, filename_attach_time,
                         filename_attach_location):
        self.move_history = []
        extension_list = self.file_dict[key]

        file_name_prefix = key.split('/')[1]
        target_file_name_prefix = file_name_prefix

        location_text = key.split('/')[0].split(',')[0]
        time_text = self._get_time_str_from_xmp(os.path.join(self.album_root_path, key + '.xmp'))

        if filename_attach_location and location_text[0] != '2':
            target_file_name_prefix = target_file_name_prefix + '-' + location_text

        if filename_attach_time:
            target_file_name_prefix = target_file_name_prefix + '-' + time_text

        for extension in extension_list:
            if extension == 'xmp' and not move_xmp:
                continue

            source_path = os.path.join(self.album_root_path, key + '.' + extension)
            target_path = os.path.join(target_dir_path, target_file_name_prefix + '.' + extension)
            self.move_history.append((source_path, target_path))
            self.move(source_path, target_path)


if __name__ == "__main__":
    album_root_path = '/Users/zhangyiqun/Desktop/D-iCloud图库清理/F-第一次清理-删除部分-2023.5.2'
    log_path = '/Users/zhangyiqun/Desktop/D-iCloud图库清理/log.txt'
    gps_data_path_list = ['gps_data/AU.txt', 'gps_data/CN.txt']

    class_list = [
        ClassDetail('🐼 表情包', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-表情包', False, False,
                    False),
        ClassDetail('🟡 网络黄图', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-网络黄图', False, False,
                    False),
        ClassDetail('🇨🇳 国内政治', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-国内政治', False, False,
                    False),
        ClassDetail('😂 普通梗图', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-普通梗图', False,
                    False, False),
        ClassDetail('🌐 网络图片和截图', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-网络图片和截图',
                    False, False, True),
        ClassDetail('📝 记录照片和截图',
                    '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-记录照片和截图', False,
                    False, True),
        ClassDetail('📷 照片', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-照片', True, False,
                    True),
        ClassDetail('↩️ 导回相册', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-导回相册', True, False,
                    False),
    ]

    class_trash = ClassDetail('Trash', '/Users/zhangyiqun/Desktop/D-iCloud图库清理/B-手机图片转移/D-回收站', True,
                              False, False)

    start_index = 100  # 从第几张开始, 从1开始计数

    gps_converter = GPSConverter(gps_data_path_list)
    classifier = Classifier(album_root_path, log_path, start_index)
    app = DisplayApp(classifier, gps_converter, class_trash, class_list)
    app.mainloop()
