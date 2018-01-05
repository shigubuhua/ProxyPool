from ..config import POOL_UPPER_THRESHOLD
from ..dbop import RedisOperator
from ..error import ResourceDepletionError
from ..spider import SpiderMeta
from .tester import UsabilityTester
from concurrent import futures


class PoolAdder(object):
    """添加器，负责启动爬虫补充代理"""

    def __init__(self):
        self._threshold = POOL_UPPER_THRESHOLD
        self._pool = RedisOperator()
        self._tester = UsabilityTester()

    def is_over(self):
        """ 判断池中代理的数量是否达到阈值
        :return: 达到阈值返回 True, 否则返回 False.
        """
        return True if self._pool.usable_size >= self._threshold else False

    def add_to_pool(self):
        """补充代理
        :return: None
        """
        print('代理数量过低，正在补充代理...')
        spiders = [cls() for cls in SpiderMeta.spiders]
        flag = 0
        while not self.is_over():
            flag += 1
            new_proxies = []
            with futures.ThreadPoolExecutor(max_workers=len(spiders)) as executor:
                future_to_down = {executor.submit(spiders[i].get, 10): i
                                  for i in range(len(spiders))}
                for future in futures.as_completed(future_to_down):
                    new_proxies.extend(future.result())
            for proxy in new_proxies:
                self._pool.add(proxy)
            print('='*20, '\n 增加 ', len(new_proxies), ' 个代理\n', '='*20, sep='')
            self._tester.test(new_proxies)
            if self.is_over():
                break
            if flag >= 30:
                raise ResourceDepletionError
            print('代理仍然不足，再次补充代理...')
        for spider in spiders:
            spider.flush()
