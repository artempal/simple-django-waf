from setting import Setting
import urllib.parse
import re
import os
from main.models import BlackList

urls_reg = ['select', r'<script[\s>\/]']
body_reg = [r'<svg\s', r'<img\s']
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def get_reg(stable):
    list = BlackList.objects.values_list('reg', flat=True).filter(url=True, active=True, stable=stable)
    return list


def get_stable():
    return list


def url_decode(url):
    """
    декодирование url адреса
    :param url: исходный адрес
    :return:
    """
    return urllib.parse.unquote(url)


def reg_search(reg_list, text):
    """
    поиск по регулярному выражению
    :param reg_list: список регулярок
    :param text: текст для поиска
    :return:
    """
    for reg in reg_list:
        result = re.search(reg, text)
        if result is not None:
            return reg
    return 0


def stable_search(stable_list, text):
    """
    поиск по стабильным вхождениям строки (без регулярных выражений)
    :param stable_list: строка стабильных вхождений
    :param text: текст для поиска
    :return:
    """
    for stable in stable_list:
        result = text.find(stable)
        if result != -1:
            return stable
    return 0


class Analysis:
    request = object  # запрос

    def __init__(self):
        self.setting = Setting()
        self.reg_url = get_reg(stable=False)
        self.stable_url = get_reg(stable=True)

    def check_query(self):
        clean_query = url_decode(self.request.query)
        result = stable_search(self.stable_url, clean_query)  # сначала ищем стабильные вхождения
        if result == 0:  # если ничего нет
            result = reg_search(self.reg_url, clean_query)  # ищем вхождения по регулярным выражениям
        if result != 0:  # если что-то найдено
            print(result)
            return 1
        return 0

    def check_block(self):
        # запрос в базу регулярок с блокировками по месту их дислокации

        pass

    def process(self, req):
        self.request = req
        '''
        print(self.request.path)
        print(self.request.headers)
        print(self.request.body)
        print(self.request.cookies)
        print(self.request.arguments)
        print(self.request.query)
        '''

        # сначала проверяем все регулярки с блокировкой по порядку, при нахождении регулярки поиск заканчивается,
        # событие вносится в базу, запрос блокируется если включена проверка на подозриетльные запросы, происходит
        # поиск всех вхождений подозрительных и все они заносятся в базу
        status = 0  # счетчик сработки правил блокировка
        status += self.check_query()

        if status > 0:  # если было обнаружено хотя бы одно событие, попадающее к политике блокировки
            return True  # блокируем
        else:
            return False  # пропускаем
