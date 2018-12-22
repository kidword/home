import requests
from threading import Thread
from bs4 import BeautifulSoup
import pymysql as py
from queue import Queue
import datetime


class LianjiaSpider():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.url_q = Queue()  # url队列
        self.html_q = Queue()  # 响应内容队列
        self.item_q = Queue()  # 提取的数据结果队列

    def url_lis(self):
        self.url = 'https://bj.lianjia.com/zufang/dongcheng/pg{}/#contentList'  # 1-13
        # for i in range(27, 28):
        self.url_q.put(self.url.format(26))

    def getHtml(self):
        """发送请求获取响应,并添加队列"""
        while True:
            url = self.url_q.get()
            resp = requests.get(url, headers=self.headers)
            # print(resp.text)
            self.html_q.put(resp.text)
            self.url_q.task_done()  # 让url_q计数-1

    def parseItem(self):
        while True:
            html_str = self.html_q.get()
            next = html_str.find('下一页')
            html = BeautifulSoup(html_str)
            div_list = html.select('div[class="content__list--item--main"]')
            result_list = []
            for div in div_list:
                item = {}
                item['name'] = div.select('.content__list--item--des a')[1].get_text()
                item['content'] = div.select('.content__list--item--des i')[0].next_sibling.strip()
                item['huxing'] = div.select('.content__list--item--des i')[2].next_sibling.strip()
                item['chaoxiang'] = div.select('.content__list--item--des i')[1].next_sibling.strip()
                item['price'] = div.select('.content__list--item-price em')[0].get_text()
                result_list.append(item)
            ne = html.select('#content > div.content__article > div.content__pg > a.next')
            print(ne)
            # next_page = html.findAll('div',attrs={'data-totalpage':True})
            # for i in next_page:
            #     print(i.attrs['data-totalpage'])
            # print(next_page)
            self.item_q.put(result_list)
            self.html_q.task_done()  # 计数-1


    def excuteItem(self):
        """处理或保存结果列表中的每一条数据"""
        while True:
            # conn = py.connect(host='localhost', user='root', passwd='hh226752', db='flightradar24', charset='utf8')
            result_list = self.item_q.get()
            for item in result_list:
                pass
                # con = conn.cursor()
                # sql = "insert into lianjia(area,mianji,huxing,chaoxiang,price) values(%s,%s,%s,%s,%s)"
                # params = (item['name'], item['content'], item['huxing'], item['chaoxiang'], item['price'])
                # con.execute(sql, params)
                # conn.commit()
                # print(item)
            self.item_q.task_done()  # 计数-1
            # conn.close()

    def run(self):
        """逻辑"""
        # 构造url_list
        self.url_lis()
        t_list = []
        for i in range(3):  # 开启三个发送请求的线程,来提高发送请求的效率
            t_parse = Thread(target=self.getHtml)
            t_list.append(t_parse)

        for i in range(2):
            t_content = Thread(target=self.parseItem)
            t_list.append(t_content)

        t_save = Thread(target=self.excuteItem)
        t_list.append(t_save)

        for t in t_list:
            t.setDaemon(True) # 设置线程为守护线程:主线程结束,子线程跟着一起结束
            t.start()

        for q in [self.url_q, self.html_q, self.item_q]:
            q.join() # 让每个q队列阻塞主线程
            # 每个q队列的计数为0的时候,才停止阻塞

        print('程序结束了')

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    spider = LianjiaSpider()
    spider.run()
    end_time = datetime.datetime.now()
    print(end_time - start_time)