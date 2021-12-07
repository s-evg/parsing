import time

import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm


url = "https://free-proxy-list.net/"
headers = {
"user-agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko)"
              "Chrome/95.0.4638.69 Mobile Safari/537.36"
}


def pars():
    """Парсим список доступных IP адресов."""

    response = requests.get(url=url, headers=headers)
    while True:
        if response.status_code == 200:
            soup = bs(response.content, 'html.parser')
            proxy_list = soup.find('textarea').get_text().split('\n')[3:-1]
            return proxy_list
        else:
            print('Не удалось получить список IP\nПереподулючение через 30 сек')
            time.sleep(30)


bad_proxies = [] # список для плохих прокси


def get_proxy(ban=[], bad=[]):
    """Создаём сессию для отправки HTTP запроса
    :param bad:
    """
    # print(f'Плохие прокси: {bad}')
    proxies = set(pars()) # преобразуем список во множество
    # получаем список IP адресов получивших бан, и выкидываем их из спика прокси

    proxies = proxies - set(ban) - set(bad)

    session = requests.Session()
    """Выбираем первый рабочий IP"""
    for proxy in tqdm(proxies):
        session.proxies = {'http': proxy, 'https': proxy}
        try:
            url = 'http://icanhazip.com/'
            response = session.get(url=url, timeout=1.618)
            if response.status_code == 200:
                print(f'Выбранный IP: {proxy}')
                return proxy, bad

        except Exception as e:
            bad.append(proxy)
            time.sleep(0.333)
            continue


def my_ip():
    """Проверяем свой IP"""

    response = requests.get('http://icanhazip.com/', timeout=2)
    return response.text.strip()


if __name__ == '__main__':
    # start = time.time()
    # get_proxy()
    # print(time.time() - start)
    print(my_ip())
