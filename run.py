from proxypool.schedule import ProxyCountCheckProcess, CyclicTestProcess, AppProcess
from proxypool.config import VALID_CHECK_CYCLE, POOL_LEN_CHECK_CYCLE, \
    POOL_UPPER_THRESHOLD, POOL_LOWER_THRESHOLD


def cli():
    p1 = ProxyCountCheckProcess(POOL_LOWER_THRESHOLD, POOL_UPPER_THRESHOLD, POOL_LEN_CHECK_CYCLE)
    p2 = CyclicTestProcess(POOL_LOWER_THRESHOLD, VALID_CHECK_CYCLE)
    p3 = AppProcess()
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()


if __name__ == '__main__':
    cli()
