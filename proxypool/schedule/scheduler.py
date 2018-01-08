from . import UsabilityTester
from . import PoolAdder
from ..dbop import RedisOperator
from ..webapi import app
from ..config import LOGGING_CONF
from multiprocessing import Process
import logging
import logging.config
import time


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
        logging.config.dictConfig(LOGGING_CONF)
        logger = logging.getLogger('root')
        logger.info('进程1 - 代理数量监控启动，每%s秒检查一次' % self._cycle)
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
        logging.config.dictConfig(LOGGING_CONF)
        logger = logging.getLogger('root')
        logger.info('进程2 - 代理定时测试启动，每%s秒测试一次' % self._cycle)
        tester = UsabilityTester()
        pool = RedisOperator()
        while True:
            logger.debug('开始对池中所有代理进行测试')
            test_proxies = pool.get_all()
            test_total = len(test_proxies)
            if test_total < self._lower_threshold:
                logger.debug('池中代理数量低于阈值，本次不进行测试')
                time.sleep(self._cycle)
                continue
            tester.test(test_proxies)
            after_test_total = pool.usable_size
            logger.info('淘汰了 %s 个代理' % (test_total - after_test_total))
            logger.info('现可用 %s 个代理' % after_test_total)
            logger.info('本次测试结束，%s秒后再次测试' % self._cycle)
            time.sleep(self._cycle)


class AppProcess(Process):
    """Flask app 进程"""
    def __init__(self):
        Process.__init__(self)

    def run(self):
        app.run()
