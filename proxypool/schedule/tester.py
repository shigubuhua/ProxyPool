from ..config import HEADERS
from ..dbop import RedisOperator
from asyncio import TimeoutError
import asyncio
import aiohttp
import logging


class UsabilityTester(object):
    """代理测试器，负责检验给定代理的可用性"""

    def __init__(self):
        self.test_api = 'https://www.baidu.com'
        self._pool = RedisOperator()
        self._logger = logging.getLogger('root')

    async def test_single_proxy(self, proxy):
        """异步测试单个代理"""
        async with aiohttp.ClientSession() as sess:
            real_proxy = 'http://' + proxy
            try:
                async with sess.get(self.test_api, proxy=real_proxy, headers=HEADERS,
                                    timeout=15, allow_redirects=False):
                    self._pool.increase(proxy)
            except (TimeoutError, Exception):
                self._pool.decrease(proxy)

    def test(self, proxies):
        """测试传入的代理列表，
        将在定时测试周期和每次爬虫工作后被调用
        :param proxies: 代理列表
        :return: None
        """
        len_num = len(proxies)
        self._logger.info('测试器开始工作，本次测试 %s 个代理' % len_num)
        loop = asyncio.get_event_loop()
        # 分批进行测试，避免并发太高和win系统报错
        for batch in [proxies[i:i+200] for i in range(0, len_num, 200)]:
            tasks = [self.test_single_proxy(proxy) for proxy in batch]
            loop.run_until_complete(asyncio.wait(tasks, loop=loop))
