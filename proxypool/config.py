# Redis Host
HOST = 'localhost'
# Redis PORT
PORT = 6379

# Redis 中存放代理池的 Set 名
POOL_NAME = 'proxies'

# Pool 的低阈值和高阈值
POOL_LOWER_THRESHOLD = 100
POOL_UPPER_THRESHOLD = 500

# 检查代理间隔
VALID_CHECK_CYCLE = 600
# 检查 Pool 低阈值间隔
POOL_LEN_CHECK_CYCLE = 30

# 代理初始评分，百分制
INIT_SCORE = 30
# 测试代理增减评分幅度
REGULATE_SCORE = 10

# headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

# 日志模块的配置
LOGGING_CONF = {'version': 1,
                'disable_existing_loggers': False,
                'formatters': {'fh_format': {'format': '%(asctime)s - %(filename)s - %(levelname)s - %(message)s'},
                               'sh_format': {'format': '%(asctime)s [%(levelname)s] %(message)s',
                                             'datefmt': '%H:%M:%S'
                                             }
                               },
                'handlers': {'fh': {'level': 'DEBUG',
                                    'formatter': 'fh_format',
                                    'class': 'logging.FileHandler',
                                    'filename': './log.txt'
                                    },
                             'sh': {'level': 'DEBUG',
                                    'formatter': 'sh_format',
                                    'class': 'logging.StreamHandler'
                                    }
                             },
                'loggers': {'root': {'handlers': ['fh', 'sh'],
                                     'level': 'DEBUG',
                                     'encoding': 'utf8'
                                     }
                            }
                }
