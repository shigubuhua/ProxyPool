from flask import Flask, g
from .dbop import RedisOperator

__all__ = ['app']

app = Flask(__name__)


def get_conn():
    """获取 Redis 连接
    :return: RedisOperator
    """
    if not hasattr(g, 'redis_connect'):
        g.redis_connect = RedisOperator()
    return g.redis_connect


@app.route('/')
def index():
    """Web API 主页的 HTML 代码
    :return: HTML
    """
    return '<h1>Welcome</h1>'


@app.route('/get')
def get_proxy():
    """Web API IP获取页的 HTML 代码
    获取一个代理
    :return: HTML
    """
    conn = get_conn()
    return conn.get()


@app.route('/gets')
def gets_proxy(total=10):
    """Web API IP获取页的 HTML 代码
    获取10个代理
    :return: HTML
    """
    conn = get_conn()
    return '<br>'.join(conn.gets(total))


@app.route('/best')
def best_proxy():
    """Web API IP获取页的 HTML 代码
    获取可用性最高的一个代理
    :return: HTML
    """
    conn = get_conn()
    return conn.get_best()


@app.route('/count')
def get_counts():
    """Web API IP获取页的 HTML 代码
    获取可用代理总数
    :return: HTML
    """
    pool = get_conn()
    return str(pool.usable_size)
