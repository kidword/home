import requests
from bs4 import BeautifulSoup

url = 'https://www.qiushibaike.com/8hr/page/1/'
response = requests.get(url)
html = response.content.decode('utf-8')
soup = BeautifulSoup(html,'lxml')
next = soup.select('span[class="next"]')[0].get_text().split()[0]

if next == '下一页':
    print(12)