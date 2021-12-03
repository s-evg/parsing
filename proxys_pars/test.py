import requests,time, random
from bs4 import BeautifulSoup as bs
from proxy_pars import pars


proxies = pars()


def get_sessions(proxies):
    """Создаём сессию для отправки HTTP запроса"""
    session = requests.Session()
    # Выбираем случайным образом один из адресов
    proxy = random.choice(proxies)
    session.proxies = {'http': proxy, 'https': proxy}
    return session


def my_ip(n):
    """Проверяем свой IP"""

    for i in range(n):
        s = get_sessions(proxies)
        try:
            url = 'http://icanhazip.com/'
            response = s.get(url=url, timeout=2)
            print(response.text.strip())
            print(s)
        except Exception as e:
            print('Error')


if __name__ == '__main__':
    my_ip(10)
