from ..config import HEADERS
from ..dbop import RedisOperator
from asyncio import TimeoutError
import time
import asyncio
import aiohttp


class UsabilityTester(object):
    """代理测试器，负责检验给定代理的可用性"""

    def __init__(self):
        self.test_api = 'https://www.baidu.com'
        self.pool = RedisOperator()

    async def test_single_proxy(self, proxy):
        """异步测试单个代理"""
        async with aiohttp.ClientSession() as sess:
            real_proxy = 'http://' + proxy
            try:
                async with sess.get(self.test_api, proxy=real_proxy, headers=HEADERS,
                                    timeout=12, allow_redirects=False):
                    self.pool.increase(proxy)
            except (TimeoutError, Exception):
                self.pool.decrease(proxy)

    def test(self, proxies):
        """测试传入的代理列表，
        将在定时测试周期和每次爬虫工作后被调用
        :param proxies: 代理列表
        :return: None
        """
        print('代理测试器开始工作...')
        loop = asyncio.get_event_loop()
        # 避免并发太高和win系统报错，这里限制每批500个
        for batch in [proxies[i:i+500] for i in range(0, len(proxies), 500)]:
            tasks = [self.test_single_proxy(proxy) for proxy in batch]
            loop.run_until_complete(asyncio.wait(tasks, loop=loop))
            time.sleep(1)
