from block_ext import BlockExtension
import urllib.parse
import re


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
            raise BlockExtension(reg)  # выбрасываем исключени о блокировке
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
            raise BlockExtension(stable)  # выбрасываем исключени о блокировке
    return 0


def headers_to_text(headers):
    """
    преобразование заголовков в строку
    :param headers: заголовки в list
    :return: заголовки в str
    """
    text = ""
    for header in headers:
        text += header + ": " + headers[header] + "; "
    return text


def args_to_text(args):
    """
    преобразование аргументов в строку
    :param args: аргументы в словаре с значеним в виде списка с данными в типе байт
    :return: строка
    """
    encoding = 'utf-8'
    text = ""
    for key, value in args.items():
        text += key + ": "
        for val in value:
            text += str(val, encoding) + " "
        text += " "
    return text

