import os
from main.models import BlackList, Events, Configs
from block_ext import BlockExtension  # класс исключения
import helpers
from functools import wraps
from time import time
import sys
import hashlib
import redis

configs = Configs.objects.get(pk=1)

if configs.head_hash:
    r = redis.Redis(host=os.environ.get("REDIS_HOST"), password=os.environ.get("REDIS_PASSWORD"), db=0)
    r.flushdb()  # очишаем хэши при запуске

if configs.ban_enable:
    r_ban = redis.Redis(host=os.environ.get("REDIS_HOST"), password=os.environ.get("REDIS_PASSWORD"), db=1)


def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            print(f"Total execution time: {end_ if end_ > 0 else 0} ms")

    return _time_it


def generate_hash(text):
    sha = hashlib.sha1(text.encode('utf-8')).hexdigest()
    return sha


def check_hash(sha):
    return r.exists(sha)


def store_hash(sha):
    r.incr(sha)


def add_ip_to_ban(ip):
    r_ban.set(ip, "1", configs.ban_time)


def check_ip_in_ban(ip):
    return r_ban.exists(ip)


class Analysis:
    request = object  # запрос
    text = {}  # пребразованные в текст данные из запроса
    blacklist_cache_stable = {}
    blacklist_cache_reg = {}

    src_ip = object

    def __init__(self):
        self.blacklist = BlackList.objects.values_list('reg', flat=True).filter(active=True)  # получаем блэклист

        self.blacklist_cache_stable['url'] = self.blacklist.filter(url=True, stable=True)
        self.blacklist_cache_reg['url'] = self.blacklist.filter(url=True, stable=False)
        self.blacklist_cache_stable['head'] = self.blacklist.filter(head=True, stable=True)
        self.blacklist_cache_reg['head'] = self.blacklist.filter(head=True, stable=False)
        self.blacklist_cache_stable['args'] = self.blacklist.filter(args=True, stable=True)
        self.blacklist_cache_reg['args'] = self.blacklist.filter(args=True, stable=False)
        self.blacklist_cache_stable['body'] = self.blacklist.filter(body=True, stable=True)
        self.blacklist_cache_reg['body'] = self.blacklist.filter(body=True, stable=False)

    def insert_event(self, reg, location):
        """
        вставка события блокировки в базу
        :param location:
        :param reg: регулярное выражение (или строка), на котором произошла блокировка
        :return:
        """
        event = Events()
        event.url = self.request.path
        event.args = self.text['args']
        event.head = self.text['head']
        event.method = self.request.method
        event.body = self.text['body']
        event.ip = self.src_ip
        event.cookie = self.request.cookies
        event.location = location
        event.reg = reg
        event.save()

    def check(self, location):
        """
        проверка по сигнатурам
        :param location: локализация сигнатуры
        :return: вернет 0, если ничего не найдено иначе выбросит исключение BlockExtension со строкой сигнатуры
        """
        if location == 'head' and configs.head_hash:
            if check_hash(self.text['head_hash']):  # если данный хэш уже содержится в базе, пропускаем проверки
                # store_hash(self.text['head_hash'])  # увиличиваем счетчик попаданий в хэш
                return 0
        try:
            helpers.stable_search(self.blacklist_cache_stable[location], self.text[location])
            helpers.reg_search(self.blacklist_cache_reg[location], self.text[location])
            if location == 'head' and configs.head_hash:
                store_hash(self.text['head_hash'])  # если проверки успешны, то записываем хэш в Redis
        except BlockExtension as reg:
            if configs.ban_enable:
                add_ip_to_ban(self.src_ip)
            self.insert_event(reg, location)
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
        self.src_ip = self.request.headers.get("X-Real-IP") or \
                      self.request.headers.get("X-Forwarded-For") or \
                      self.request.remote_ip
        if configs.ban_enable and check_ip_in_ban(self.src_ip):
            return True
        self.text['args'] = helpers.args_to_text(self.request.arguments)
        self.text['head'] = helpers.headers_to_text(self.request.headers)
        if configs.head_hash:
            self.text['head_hash'] = generate_hash(self.text['head'])
        self.text['url'] = self.request.path
        self.text['body'] = str(self.request.body, 'utf-8')
        '''
        print(self.request.path)
        print(self.request.headers)
        print(self.request.cookies)
        print(self.request.arguments)
        print(self.request.body)
        print(self.request.query)
        print(self.text['head'])
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
