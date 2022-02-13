print()

import requests
from pprint import pprint
import json
import time
from progress.bar import IncrementalBar
from datetime import datetime

def get_vk_user_id():
    ''' Функция для получения id пользователя VK, 
        если id данного пользователя отображается в адресной строке браузера именованным значением.
    '''
    TOKEN = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    URL = 'https://api.vk.com/method/users.get'
    site_name = input("Введите идентификатор пользователя как он записан в адресной строке: ")
    params = {'user_id' : site_name,
              'access_token': TOKEN,
              'v': '5.131.',
              'fields': 'bdate, photo_id, id'
    }
    res = requests.get(URL, params=params)
    user_dict = res.json()['response'][0]
    user_id = user_dict['id']
    print(user_id)



class Extracting_photos:

    def __init__(self, token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'):
        self.token = token


    def get_profile_photo_description(self):
        '''Метод для получения характеристик заданного количества фотографий 
           с профиля пользователя ВКонтакте.
        '''
        bar = IncrementalBar('Countdown', min = self.get_profile_photo_description)
        id = int(input("Введите id пользователя: "))
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': id,
            'access_token': self.token,
            'v': '5.131.',
            'album_id': 'profile',
            'rev': 0,
            'extended': 1,
            'photo_sizes': 1,
            'count': 10
        }
        result = requests.get(url, params=params)
        bar.next()
        time.sleep(1)
        # return result.json()['response'] # проверка содержимого отклика
        items_list = result.json()['response']['items']
        bar.finish()
        return items_list # возвращается список заданного количества фотографий из профиля юзера


    def get_raw_list(self, get_profile_photo_description):
        '''Метод для получения с профиля пользователя вспомогательного списка словарей,
           описывающих фотографии максимального разрешения.
        
        '''
        bar = IncrementalBar('Countdown', max = len(get_profile_photo_description))
        raw_list = []
        for dt in get_profile_photo_description:
            bar.next()
            time.sleep(1)
            dim = dt['sizes']  # это список словарей описывающих одно фото разных форматов (x, y, z, w etc.)
            name = str(dt['likes']['count'])
            dat = str(dt['date'])
            pic_data = {'file_name': name, 'upload_date' : dat}
            sizes = list()
            for pic in dim:
                sizes.append(pic['type'])
                if 'w' in sizes:
                    pic_data['size'] = 'w'
                    pic_data['url'] = pic['url']
                else:
                    pic_data['size'] = sizes[-1]
                    pic_data['url'] = pic['url']
            raw_list.append(pic_data)
        bar.finish()
        return raw_list # возвращает вспомогательный список словарей, описывающих фотографии максимального разрешения с профиля юзера

    
    def get_same_names_inxs(self, get_raw_list):
        '''Метод для получения списка индексов элементов вспомогательного списка фото с профиля пользователя, 
            если элементы имеют одинаковое количество лайков.
        
        '''
        bar = IncrementalBar('Countdown', max = len(get_raw_list))
        names = []
        for dt in get_raw_list:
            bar.next()
            time.sleep(1)
            names.append(dt['file_name'])
            names_set = set(names)
            dub_names = []
            for name in names_set:
                if (names.count(name) > 1):
                    counting = [i for i, x in enumerate(names) if x == name]
                    dub_names.append((name, counting))
            inxs_list = []
            for tuple_ in dub_names:
                inxs_list = inxs_list + tuple_[1]
        bar.finish()
        return inxs_list # возвращает список индексов элементов списка фото с повторяющимся количеством лайков


    def get_corrected_list(self, get_raw_list, get_same_names_inxs):
        '''Метод для получения с профиля пользователя вспомогательного списка словарей,
           описывающих фотографии максимального разрешения с уникальными именами.
        '''

        for numeral in get_same_names_inxs:
            pic_data = get_raw_list[numeral]
            pic_data['file_name'] = pic_data['file_name'] + pic_data['upload_date']
        return get_raw_list # возвращает вспомогательный список словарей, описывающих фотографии с уникальными именами


    def get_picture_list(self, get_corrected_list):
        '''Метод для сохранения фотографий пользователя в текущую папку 
           и получения json-файла с информацией по загруженным с профиля фотографиям,
           с ключами 'file_name' и 'size'.
        '''
        bar = IncrementalBar('Countdown', max = len(get_corrected_list))
        for pic_data in get_corrected_list:
            bar.next()
            time.sleep(1)
            pic_data['file_name'] = pic_data['file_name'] + '.jpg'
            url = pic_data['url']
            res = requests.get(url)
            photo = res.content
            with open(pic_data['file_name'], 'wb') as f:
                f.write(photo)
            del(pic_data['url'])
            del(pic_data['upload_date'])
            json.dumps(get_corrected_list)
        bar.finish()
        return get_corrected_list # загружает фотографии пользователя по списку в текущую папку и возвращает искомый список фотографий с профиля юзера

    def get_pictures(self, get_picture_list):
        '''Метод для получения списка загруженных фотографий.
        
        '''
        pictures = list()
        for pic_data in get_picture_list:
            pictures.append(pic_data['file_name'])
        return pictures # возвращает список с именами загруженных в текущую папку фотографиями


print()


class YaUploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_a_disk_folder(self):
        '''Метод для создания на Яндекс.Диске папки с уникальным именем по дате и времени создания,
           для последующего сохранения файлов. 
        '''
        create_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        moment = str(datetime.now())[:-7]
        moment_list = moment.split(' ')
        m_list = moment_list[0].split('-') + moment_list[1].split(':')
        f_name = ''.join(m_list)
        folder_name = 'date' + f_name[:8] + 'time' + f_name[8:]
        params = {"path": folder_name, "overwrite": "true"}
        response = requests.put(create_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 201:
            print("The folder's created successfully")
        return folder_name # для проверки метода выводом на печать

    
    def find_file_path(self, *pictures):
        '''Метод для получения списка путей до файлов на компьютере 
           по полученному списку.
        
        '''
        import os
        bar = IncrementalBar('Countdown', max = len(pictures))
        file_roots = []
        for picture in pictures:
            bar.next()
            time.sleep(1)
            filename = picture
            file_path = os.path.join(os.getcwd())
            file_path = file_path + '\\' + filename
            ft = file_path.split('\\')
            path_to_file = ft[-2:]
            f_p = path_to_file[0] + '\\' + path_to_file[1]
            file_roots.append(f_p)
        bar.finish()
        return file_roots
        

    def disk_file_path(self, find_file_path, create_a_disk_folder):
        '''Метод для получения списка путей для загрузки файлов
           из текущей папки компьютера во вновь созданную на Яндекс.Диске папку. 
        
        '''

        folder = create_a_disk_folder
        disk_roots = []
        bar = IncrementalBar('Countdown', max = len(find_file_path))
        for elm in find_file_path:
            bar.next()
            time.sleep(1)
            ffp = elm
            f_n = ffp.split('\\')
            f_name = f_n[-1]
            path_to_disk = folder + '/' + f_name
            disk_roots.append(path_to_disk)
        bar.finish()
        return disk_roots # возвращает список отдельных путей для сохранения каждой фотографии из VK во вновь созданную папку
        

    def _get_upload_link(self, disk_file_path):
        '''Метод для получения списка словарей-json, 
           описывающих ссылки для загрузки фото на Яндекс-диск.
        '''
        bar = IncrementalBar('Countdown', max = len(disk_file_path))
        roots_json = []
        for elm in disk_file_path:
            bar.next()
            time.sleep(1)
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = self.get_headers()
            params = {"path": elm, "overwrite": "true"}
            response = requests.get(upload_url, headers=headers, params=params)
            roots_json.append(response.json())
        bar.finish()
        return roots_json # возвращает список словарей-json, описывающих ссылки для загрузки фото на Яндекс-диск

    def get_hrefs(self, _get_upload_link):
        '''Метод для получения списка строк, содержащих ссылки для загрузки 
           файлов на Яндекс.Диск во вновь созданную по дате и времени папку.
        
        '''
        hrefs = []
        for i in _get_upload_link:
            hrefs.append(i['href'])
        # pprint(hrefs)
        return hrefs # возвращает софрмированный список ссылок для загрузки фотографий на Яндекс-диск

    def upload(self, get_hrefs, find_file_path):
        """Метод принимает на вход списки ссылок для загрузки файлов и путей до файла на компьютере.
           Сохраняет файлы на Яндекс.Диск с таким же именем во вновь созданную папку с уникальным
           именем
        """
        zip_list = list(zip(get_hrefs, find_file_path))
        bar = IncrementalBar('Countdown', max = len(zip_list))
        for i in zip_list:
            bar.next()
            time.sleep(1)
            href = i[0]
            response = requests.put(href, data=open(i[1].split('\\')[1], 'rb'))
            response.raise_for_status()
            if response.status_code != 201:
                print("Something's going wrong!")
        bar.finish()
        print('Loading is complete')

    

if __name__ == '__main__':

    # vk_user_id = get_vk_user_id() # запустить код, если id пользователя в строке браузера с именованным значением  

    vk_user = Extracting_photos()

    items_list = vk_user.get_profile_photo_description()
    raw_list = vk_user.get_raw_list(items_list)
    indexes = vk_user.get_same_names_inxs(raw_list)
    unique_names = vk_user.get_corrected_list(raw_list, indexes)
    picture_list = vk_user.get_picture_list(unique_names)
    pprint(picture_list)
    pictures = vk_user.get_pictures(picture_list)
    # pprint(pictures)

    token = input("Введите токен, полученный на полигоне Яндекса: ")
    loader = YaUploader(token)
    folder_name = loader.create_a_disk_folder()
    # print(folder_name) # проверка для создания папки на Яндекс.Диске
    file_roots = loader.find_file_path(*pictures)
    # print(file_roots) # проверка получения списка относительных путей до загруженных фотографий на компьютере
    disk_roots = loader.disk_file_path(file_roots, folder_name)
    # print(disk_roots) # проверка получения списка путей для сохранения файлов на Яндекс.Диске
    roots_json = loader._get_upload_link(disk_roots)
    # pprint(roots_json) # проверка получения списка словарей, содержащих ссылки для загрузки файлов на Яндекс.Диск
    hrefs = loader.get_hrefs(roots_json)
    # pprint(hrefs) # проверка получения списка ссылок для загрузки файлов на Яндекс.Диск
    result = loader.upload(hrefs, file_roots)
    