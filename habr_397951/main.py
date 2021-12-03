import requests, lxml
from bs4 import BeautifulSoup as bs


URL = 'http://www.columbia.edu/~fdc/sample.html'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
           'accept': '*/*'}


def links():

    req = requests.get(URL, HEADERS)

    if req.status_code != 200:
        print('Error | The site is unavailable!')

    soup = bs(req.content, 'lxml')
    link = soup.select('a')
    link_list = []

    for l in link:
        l = l.get('href')
        if ('http' or 'https') in l:
            l = l.split('//')
            link_list.append(l[-1])

    link_list.sort()
    return '\n'.join(link_list)


if __name__ == '__main__':
    print(links())
