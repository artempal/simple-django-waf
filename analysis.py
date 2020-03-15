import os
from main.models import BlackList, Events
from block_ext import BlockExtension  # класс исключения
import helpers

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class Analysis:
    request = object  # запрос
    text = {}  # пребразованные в текст данные из запроса

    def __init__(self):
        self.blacklist = BlackList.objects.values_list('reg', flat=True).filter(active=True)  # получаем блэклист

    def get_blacklist(self, stable, location):
        """
        получение блэклиста
        :param location: местонахождение данного выражения
        :param stable: это просто поиск подстроки (True) или регулярное выражение (False)
        :return:
        """
        if location == 'url':
            return self.blacklist.filter(url=True, stable=stable)
        elif location == 'head':
            return self.blacklist.filter(head=True, stable=stable)
        elif location == 'args':
            return self.blacklist.filter(args=True, stable=stable)
        elif location == 'body':
            return self.blacklist.filter(body=True, stable=stable)
        else:
            return self.blacklist

    def insert_event(self, reg):
        """
        вставка события блокировки в базу
        :param reg: регулярное выражение (или строка), на котором произошла блокировка
        :return:
        """
        event = Events()
        event.url = self.request.path
        event.args = self.text['args']
        event.head = self.text['head']
        event.method = self.request.method
        event.body = self.text['body']
        event.ip = self.request.remote_ip
        event.type = BlackList.objects.get(reg=reg).type
        event.cookie = self.request.cookies
        event.reg = reg
        event.save()

    def check(self, location):
        """
        проверка по сигнатурам
        :param location: локализация сигнатуры
        :return: вернет 0, если ничего не найдено иначе выбросит исключение BlockExtension со строкой сигнатуры
        """
        try:
            helpers.stable_search(self.get_blacklist(True, location), self.text[location])
            helpers.reg_search(self.get_blacklist(False, location), self.text[location])
        except BlockExtension as reg:
            self.insert_event(reg)
            print(reg)
            raise BlockExtension(reg)
        return 0

    def process(self, req):
        """
        процесс анализа, запускаемый основной программой waf.py
        :param req: класс request (tornado HTTPServerRequest)
        :return: True - если нужно заблокировать, False - если блокировать не нужно
        """
        self.request = req
        self.text['args'] = helpers.args_to_text(self.request.arguments)
        self.text['head'] = helpers.headers_to_text(self.request.headers)
        self.text['url'] = helpers.url_decode(self.request.uri)
        self.text['body'] = str(self.request.body, 'utf-8')
        '''
        print(self.request.path)
        print(self.request.headers)
        print(self.request.cookies)
        print(self.request.arguments)
        print(self.request.body)
        print(self.request.query)
        '''
        try:  # проверяем по порядку и ждем выброса исключения на любом этапе проверки
            self.check('url')
            self.check('args')
            self.check('head')
            self.check('body')
        except BlockExtension:
            return True  # блокируем
        else:
            return False  # пропускаем
