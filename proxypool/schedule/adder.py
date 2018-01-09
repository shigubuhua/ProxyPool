from ..config import POOL_UPPER_THRESHOLD
from ..dbop import RedisOperator
from ..spider import SpiderMeta
from .tester import UsabilityTester
from concurrent import futures
import logging


class PoolAdder(object):
    """添加器，负责启动爬虫补充代理"""

    def __init__(self):
        self._threshold = POOL_UPPER_THRESHOLD
        self._pool = RedisOperator()
        self._tester = UsabilityTester()
        self._logger = logging.getLogger('root')

    def is_over(self):
        """ 判断池中代理的数量是否达到阈值
        :return: 达到阈值返回 True, 否则返回 False.
        """
        return True if self._pool.usable_size >= self._threshold else False

    def add_to_pool(self):
        """补充代理
        :return: None
        """
        self._logger.info('代理数量过低，启动爬虫补充代理')
        spiders = [cls() for cls in SpiderMeta.spiders]
        flag = 1
        while not self.is_over():
            new_proxies = []
            added_proxies = []
            with futures.ThreadPoolExecutor(max_workers=len(spiders)) as executor:
                future_to_down = {executor.submit(spiders[i].get): i
                                  for i in range(len(spiders))}
                for future in futures.as_completed(future_to_down):
                    new_proxies.extend(future.result())
            for proxy in new_proxies:
                if self._pool.add(proxy):
                    added_proxies.append(proxy)
            self._logger.info('爬取增加了 %s 个代理，开始测试' % len(added_proxies))
            self._tester.test(added_proxies)
            if self.is_over():
                self._logger.debug('代理已经充足，结束补充')
                break
            if flag % 5 == 0:
                self._logger.warning('已连续补充%s次代理仍未满足，请检查爬虫和配置' % flag)
            flag += 1
            self._logger.debug('代理仍然不足，进行第%s次补充' % flag)
        for spider in spiders:
            spider.flush()
