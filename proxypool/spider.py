"""
爬虫模块，包含爬虫类的元类、基类、异常类
如果用户需要定义自己的爬虫类，必须要继承`SpiderMeta`元类和`BaseSpider`基类，
并重写`get`方法，方法需要返回`ip:port`字符串组成的列表形式的代理。
"""

from .request import PageRequest
import time
import re
import logging


class SpiderMeta(type):
    """爬虫类的元类，用于将子类注册到列表中
    """
    spiders = []

    def __new__(mcs, *args, **kwargs):
        """构造子类
        :param args: args[0] = name, args[1] = bases, args[2] = attrs.
        :param kwargs: No.
        :return: 新类
        """
        SpiderMeta.spiders.append(type.__new__(mcs, *args, **kwargs))
        return type.__new__(mcs, *args, **kwargs)


class BaseSpider(object):
    """爬虫类的基类，必须继承该类，并改写get方法
    """

    def __init__(self):
        """子类的构造方法
        :return: None
        """
        # 页数计数器
        self._counter = 1
        # 解析器有get_resp方法进行请求，返回soup结果
        self._request = PageRequest()
        self._logger = logging.getLogger('root')

    def increment(self, count):
        """子类用于增加计数器的方法
        :param count: 计数器增加量
        :return: None
        """
        self._counter += count

    def flush(self):
        """将计数器刷新为 1
        :return: None
        """
        self._counter = 1

    def get(self, step=1):
        """爬虫类必须有get方法，其中包含爬虫代码
        :param step: 每次爬取页数，如一次没有充足，会继续累加，充足则复位
        :return: 包含 IP:Port 字符串格式的列表
        """
        raise RewriteSpiderError(__class__.__name__)


class RewriteSpiderError(Exception):
    """重写爬虫异常，当用户自己编写的爬虫类没有按照规定时，
    将触发此异常.
    """

    def __init__(self, cls_name):
        self.cls_name = cls_name
        Exception.__init__(self)

    def __str__(self):
        return repr(f'爬虫`{self.cls_name}`没有重写`gets`方法.')


class KuaidailiSpider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://www.kuaidaili.com/free/inha/{}/'

    def get(self, step=10):
        urls = (self.start_url.format(i)
                for i in range(self._counter, self._counter + step))
        proxies = []
        # 以下爬虫代码可自行修改
        for url in urls:
            resp = self._request.get_resp(url)
            ip_list = re.findall(
                r'<td.*?>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', resp.text)
            port_list = re.findall(r'<td.*?>(\d{4,5})</td>', resp.text)
            for ip, port in zip(ip_list, port_list):
                proxies.append(':'.join([ip, port]))
            # 防止被BAN，加3秒延迟
            time.sleep(3)
        self._counter += step
        self._logger.debug('%s 爬取了 %s 个代理' %
                           (self.__class__.__name__, len(proxies)))
        return proxies


class XiciSpider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://www.xicidaili.com/nn/{}'

    def get(self, step=1):
        urls = (self.start_url.format(i)
                for i in range(self._counter, self._counter + step))
        proxies = []
        for url in urls:
            resp = self._request.get_resp(url)
            # 这个网站反爬不会返回404，会返回干扰页面
            while 'block' in resp.text:
                self._logger.debug('%s 被反爬，开始使用代理' %
                                   self.__class__.__name__)
                self._request.load_proxy()
                time.sleep(5)
                resp = self._request.get_resp(url)
            ip_list = re.findall(
                r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', resp.text)
            port_list = re.findall(r'<td>(\d{4,5})</td>', resp.text)
            for ip, port in zip(ip_list, port_list):
                proxies.append(':'.join([ip, port]))
            time.sleep(10)
        self._counter += step
        self._logger.debug('%s 爬取了 %s 个代理' %
                           (self.__class__.__name__, len(proxies)))
        return proxies


class Ip3366Spider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://www.ip3366.net/free/?stype=1&page={}'

    def get(self, step=10):
        urls = (self.start_url.format(i)
                for i in range(self._counter, self._counter + step))
        proxies = []
        for url in urls:
            resp = self._request.get_resp(url)
            ip_list = re.findall(
                r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', resp.text)
            port_list = re.findall(r'<td>(\d{4,5})</td>', resp.text)
            for ip, port in zip(ip_list, port_list):
                proxies.append(':'.join([ip, port]))
            time.sleep(3)
        self._counter += step
        self._logger.debug('%s 爬取了 %s 个代理' %
                           (self.__class__.__name__, len(proxies)))
        return proxies


class Ip66Spider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://m.66ip.cn/mo.php?tqsl=300'

    def get(self, step=1):
        resp = self._request.get_resp(self.start_url)
        time.sleep(5)
        proxies = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}',
                             resp.text)
        self._logger.debug('%s 爬取了 %s 个代理' %
                           (self.__class__.__name__, len(proxies)))
        return proxies

# 请在此处继续扩展你的爬虫类。
