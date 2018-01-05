from . import UsabilityTester
from . import PoolAdder
from ..dbop import RedisOperator
from multiprocessing import Process
import time
from ..webapi import app


class ProxyCountCheckProcess(Process):
    """proxy 数量监控进程，负责监控 Pool 中的代理数。当 Pool 中的
    代理数量低于下阈值时，将触发添加器，启动爬虫补充代理，当代理的数量
    打到上阈值时，添加器停止工作。
    """
    def __init__(self, lower_threshold, upper_threshold, cycle):
        """
        :param lower_threshold: 下阈值
        :param upper_threshold: 上阈值
        :param cycle: 扫描周期
        """
        Process.__init__(self)
        self._lower_threshold = lower_threshold
        self._upper_threshold = upper_threshold
        self._cycle = cycle

    def run(self):
        adder = PoolAdder()
        pool = RedisOperator()
        while True:
            if pool.usable_size < self._lower_threshold:
                adder.add_to_pool()
            time.sleep(self._cycle)


class ExpireCheckProcess(Process):
    """过期性检验进程，每隔一段时间从 Pool 中提取出最多200个代理进行测试
    """
    def __init__(self, lower_threshold, cycle):
        """
        :param cycle: 扫描周期
        :param lower_threshold: 下阈值
        """
        Process.__init__(self)
        self._cycle = cycle
        self._lower_threshold = lower_threshold

    def run(self):
        tester = UsabilityTester()
        pool = RedisOperator()
        print('定时代理测试进程启动...')
        while True:
            test_proxies = pool.get_all()
            test_total = len(test_proxies)
            if test_total < self._lower_threshold:
                continue
            tester.test(test_proxies)
            after_test_total = pool.usable_size
            print('='*20, '\n 淘汰了 ', test_total - after_test_total,
                  ' 个代理', sep='')
            print('=' * 20, '\n 现可用 ', after_test_total,
                  ' 个代理\n', '=' * 20, sep='')
            print('%s秒后进行下次测试...' % self._cycle)
            time.sleep(self._cycle)


class AppProcess(Process):
    """Flask app 进程"""
    def __init__(self):
        Process.__init__(self)

    def run(self):
        app.run()
