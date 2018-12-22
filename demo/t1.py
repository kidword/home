import requests
from threading import Thread
from bs4 import BeautifulSoup
from queue import Queue


class spider:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}

        self.url_q = Queue()  # url队列
        self.html_q = Queue()  # 响应内容队列
        self.item_q = Queue()  # 提取的数据结果队列

    def url_lis(self):
        self.url = 'https://www.qiushibaike.com/8hr/page/1/'
        self.url_q.put(self.url)
        i = 1
        while True:
            self.url_q.put(self.url.format(i))
            i+=1
            print(i)

    def getHtml(self):
        while True:
            url = self.url_q.get()
            resp = requests.get(url, headers=self.headers)
            self.html_q.put(resp.content.decode('utf-8'))
            self.url_q.task_done()  # 让url_q计数-1

    def parseItem(self):
        while True:
            html_str = self.html_q.get()
            soup = BeautifulSoup(html_str, 'lxml')
            next = soup.select('span[class="next"]')[0].get_text().split()[0]
            print(next)
            if next == '下一页':
                self.url_lis()
                print(123)
            else:
                break
            # self.item_q.put(result_list)
            self.html_q.task_done()

    def run(self):
        self.url_lis()
        t_list = []
        for i in range(3):  # 开启三个发送请求的线程,来提高发送请求的效率
            t_parse = Thread(target=self.getHtml)
            t_list.append(t_parse)

        for i in range(2):
            t_content = Thread(target=self.parseItem)
            t_list.append(t_content)

        for t in t_list:
            t.setDaemon(True)  # 设置线程为守护线程:主线程结束,子线程跟着一起结束
            t.start()

        for q in [self.url_q, self.html_q, self.item_q]:
            q.join()  # 让每个q队列阻塞主线程
            # 每个q队列的计数为0的时候,才停止阻塞
        print('程序结束了')

if __name__ == '__main__':
    sp= spider()
    sp.run()
