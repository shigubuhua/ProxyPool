from .config import HEADERS
from .dbop import RedisOperator
from bs4 import BeautifulSoup
from requests.exceptions \
    import ProxyError, ConnectionError, Timeout, ChunkedEncodingError
import requests
import asyncio
import aiohttp


class PageParser(object):
    """爬虫类使用的解析页面的类
    支持自动切换代理
    """

    def __init__(self):
        # 存储 requests 代理参数（首次不使用代理）
        self.proxies_arg = None
        self._pool = RedisOperator()

    def _request(self, url, retry=2):
        """带有重试功能的 requests
        :param url: 请求链接
        :param retry: 重试次数
        :return: requests结果
        """
        try:
            return requests.get(url, headers=HEADERS, timeout=30,
                                proxies=self.proxies_arg)
        except (ProxyError, ConnectionError, Timeout,
                ChunkedEncodingError):
            if retry > 0:
                return self._request(url, retry=retry-1)

    def parse(self, url):
        """将网页解析为 BeautifulSoup 对象并返回
        解析请求若出错，从池中更换代理重新请求
        :param url: 解析链接
        :return: BeautifulSoup对象
        """
        try:
            r = self._request(url)
        except (ProxyError, ConnectionError, Timeout,
                ChunkedEncodingError):
            print('爬虫连续请求失败，正在加载代理请求')
            # 请求失败，从池中获取代理进行重试
            self.get_proxy()
            return self._request(url)
        try:
            soup = BeautifulSoup(r.content.decode("utf-8"), 'lxml')
        except UnicodeDecodeError:
            soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def get_proxy(self):
        """从代理池中取一个代理用于requests"""
        print(self.__class__.__name__)
        self.proxies_arg = {'http': self._pool.get()}
