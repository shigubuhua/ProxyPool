# Redis Host
HOST = 'localhost'
# Redis PORT
PORT = 6379

# Redis 中存放代理池的 Set 名
POOL_NAME = 'proxies'

# Pool 的低阈值和高阈值
POOL_LOWER_THRESHOLD = 50
POOL_UPPER_THRESHOLD = 500

# 检查代理间隔
VALID_CHECK_CYCLE = 600
# 检查 Pool 低阈值间隔
POOL_LEN_CHECK_CYCLE = 30

# 代理初始评分，百分制
INIT_SCORE = 30
# 评分增减，连接成功增，反之减
CHANGE_SCORE = 10

# headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}
