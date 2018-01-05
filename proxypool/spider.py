"""
爬虫模块，包含爬虫类的元类和基类，
如果用户需要定义自己的爬虫类，必须要继承
`SpiderMeta`元类和`BaseSpider`基类，并重写`get`方法，
`get`方法要求返回 ip:port 字符串组成的列表形式的代理。
"""

from .error import RewriteSpiderError
from .parser import PageParser
import time
import re


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
        # 解析器有parse方法进行请求，返回soup结果
        self.parser = PageParser()

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


class KuaidailiSpider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://www.kuaidaili.com/free/inha/{}/'

    def get(self, step=2):
        urls = (self.start_url.format(i)
                for i in range(self._counter, self._counter + step))
        proxies = []
        # 以下爬虫代码可自行修改
        for url in urls:
            soup = self.parser.parse(url)
            # 防止被 Ban, 加 3s 间隔。
            time.sleep(3)
            proxy_list = soup.find('table', class_='table-bordered')
            for each in proxy_list.find_all('tr')[1:]:
                tmp = each.find_all('td')
                ip = tmp[0].get_text()
                port = tmp[1].get_text()
                proxies.append(':'.join([ip, port]))
        self._counter += step
        return proxies


class XiciSpider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://www.xicidaili.com/nn/{}'

    def get(self, step=1):
        urls = (self.start_url.format(i)
                for i in range(self._counter, self._counter + step))
        proxies = []
        for url in urls:
            soup = self.parser.parse(url)
            time.sleep(5)
            # 这个网站反爬不会返回404，会返回干扰页面
            while 'block' in soup.text:
                self.parser.get_proxy()
                soup = self.parser.parse(url)
            proxy_list = soup.find('table', id='ip_list').find_all('tr')[1:]
            for each in proxy_list:
                tmp = each.find_all('td')
                ip = tmp[1].get_text()
                port = tmp[2].get_text()
                proxies.append(':'.join([ip, port]))
        self._counter += step
        return proxies


class Ip3366Spider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://www.ip3366.net/free/?stype=1&page={}'

    def get(self, step=2):
        urls = (self.start_url.format(i)
                for i in range(self._counter, self._counter + step))
        proxies = []
        for url in urls:
            soup = self.parser.parse(url)
            time.sleep(3)
            proxy_list = soup.find('table', class_='table-bordered')
            for each in proxy_list.find_all('tr')[1:]:
                tmp = each.find_all('td')
                ip = tmp[0].get_text()
                port = tmp[1].get_text()
                proxies.append(':'.join([ip, port]))
        self._counter += step
        return proxies


class Ip66Spider(BaseSpider, metaclass=SpiderMeta):
    start_url = 'http://m.66ip.cn/mo.php?tqsl=300'

    def get(self, step=1):
        soup = self.parser.parse(self.start_url)
        time.sleep(5)
        ip_port = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}',
                             soup.get_text(), flags=re.M)
        return ip_port

# 请在此处继续扩展你的爬虫类。
