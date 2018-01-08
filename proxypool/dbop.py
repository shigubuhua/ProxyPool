from .config import HOST, PORT, POOL_NAME, INIT_SCORE, REGULATE_SCORE
from random import choice, choices
import redis
import re
import logging


class RedisOperator(object):
    """Redis 操作类
    代理以 Sorted Sets 存储在固定 key 中
    并通过增减 score 来标注代理的可用性
    同时会注册一份以代理为 name 的 key 来避免重复代理
    淘汰的代理会给 key 设置过期时间，以免长期堆积
    """

    def __init__(self):
        """初始化 Redis 连接"""
        self._conn = redis.StrictRedis(
            host=HOST, port=PORT, max_connections=20, decode_responses=True)
        # 可用代理最低分，保证获取到的至少成功连接1次
        self.usable_score = INIT_SCORE + REGULATE_SCORE
        self._logger = logging.getLogger('root')

    def get(self):
        """返回随机一个可用代理
        :return: 字符串形式
        """
        return self._weight_choices()[0]

    def gets(self, total):
        """返回随机多个可用代理
        :param total: 返回的数量
        :return: 列表形式
        """
        return self._weight_choices(total)

    def _weight_choices(self, total=1):
        """根据分数作为相对权重，随机出指定数量的可用代理并返回
        指定多个结果可能会有重复
        :param total: 返回的数量
        :return: 列表形式
        """
        if self.usable_size < total:
            self._logger.warning('可用代理低于请求返回的数量，请降低请求数量')
        proxies = []
        scores = []
        for proxy, score in self._conn.zrevrangebyscore(
                POOL_NAME, 100, self.usable_score, 0, max(200, total),
                withscores=True):
            proxies.append(proxy)
            scores.append(score)
        return choices(proxies, scores, k=total)

    def get_all(self):
        """返回所有代理
        :return: 列表形式
        """
        return self._conn.zrevrangebyscore(POOL_NAME, 100, 0)

    def add(self, proxy, score=INIT_SCORE):
        """添加一个代理，并设置初始分数
        判断符合IP:Port格式，并且池中不存在相同的
        :param proxy: 代理
        :param score: 分数
        :return: 1 or 0
        """
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', proxy) \
                and not self._conn.sadd(proxy, 'register'):
            return self._conn.zadd(POOL_NAME, score, proxy)
        return 0

    def get_best(self):
        """返回分数最高的随机一个代理
        :return: 字符串形式
        """
        proxies = self._conn.zrevrange(POOL_NAME, 0, 1)
        if proxies:
            return choice(proxies)

    def increase(self, proxy):
        """增加指定代理的分数，最高为100
        :param proxy: 代理
        :return: 修改后的分数
        """
        diff = 100 - self.score(proxy)
        if diff >= REGULATE_SCORE:
            return self._conn.zincrby(POOL_NAME, proxy, REGULATE_SCORE)
        else:
            return self._conn.zincrby(POOL_NAME, proxy, diff)

    def decrease(self, proxy):
        """减少指定代理的分数，为0则删除
        :param proxy: 代理
        :return: 修改后的分数
        """
        if self.score(proxy) > REGULATE_SCORE:
            return self._conn.zincrby(POOL_NAME, proxy, -REGULATE_SCORE)
        else:
            return self.delete(proxy)

    def delete(self, proxy):
        """删除指定的一个代理（有重复会删除多个）
        并且将对应 key 添加5天过期时间
        :param proxy: 代理
        :return: 删除数量
        """
        self._conn.expire(proxy, 432000)
        return self._conn.zrem(POOL_NAME, proxy)

    @property
    def usable_size(self):
        """返回池中可用代理总数
        :return: 整型
        """
        return self._conn.zcount(POOL_NAME, self.usable_score, 100)

    @property
    def size(self):
        """返回池中所有代理总数
        :return: 整型
        """
        return self._conn.zcount(POOL_NAME, 0, 100)

    def score(self, proxy):
        """返回指定代理的分数
        :param proxy:
        :return: 分数
        """
        score = self._conn.zscore(POOL_NAME, proxy)
        if score:
            return score
        return 0
