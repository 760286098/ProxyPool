import re
import time

import requests

from proxypool.db import RedisClient
from proxypool.setting import SLEEP_TIME

headers = {
    'Host': 'weixin.sogou.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://weixin.sogou.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
url = 'https://weixin.sogou.com/weixin?type=2&query=nba&s_from=input&_sug_=n&_sug_type_=&w=01019900&sut=5296&sst0' \
      '=1543167134916&lkt=10%2C1543167129476%2C1543167134813 '


class Spider:
    def __init__(self):
        self.redis = RedisClient()

    def run(self):
        proxy = self.redis.random()
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy,
        }
        r = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies, timeout=3)
        # r = requests.get(url, allow_redirects=False, headers=headers, timeout=3)
        print('正在使用：', proxy)
        if r.status_code == 200:
            header = r.headers
            print(header)
            snuid = re.findall('(SNUID=.*?;)', header['Set-Cookie'])
            print(1)
            if len(snuid) != 0:
                self.redis.push(snuid[0])
                print('Redis插入:', snuid[0])
                while snuid is not None:
                    self.circle(proxy)
                    time.sleep(SLEEP_TIME)
                else:
                    self.redis.decrease(proxy)
            else:
                self.redis.decrease(proxy)
        else:
            print(r.status_code)

    def circle(self, proxy):
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy,
        }
        try:
            # r = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
            r = requests.get(url, allow_redirects=False, headers=headers)
            print('循环代理：', proxy)
            if r.status_code == 200:
                header = r.headers
                print(header)
                snuid = re.findall('(SNUID=.*?;)', header['Set-Cookie'])
                if len(snuid) != 0:
                    self.redis.push(snuid[0])
                    print('Redis插入:', snuid[0])
        except Exception as e:
            print('cookie发生错误', e.args)


if __name__ == '__main__':
    spider = Spider()
    while True:
        spider.run()
