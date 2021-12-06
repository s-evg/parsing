import json
from pprint import pprint

from bs4 import BeautifulSoup as bs
import requests, time, lxml, random
from openpyxl import Workbook
from tqdm import tqdm

from worker_proxy import get_proxy, my_ip
from user_agent_mobile import user_agent


URL = input('Введите адрес раздела AVITO для парсинга:\n>>> ')
HEADERS = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"}


def page_pars():
    """
    Парсим страницы сайта, и собираем нанные из блока:
    class_='iva-item-content-UnQQ4'
    """

    content_list = []

    response = requests.get(url=URL, headers=HEADERS, timeout=9)

    if response.status_code != 200:
        return 'Сайт AVITO не доступен, попробуйте позже.'

    else:
        soup = bs(response.content, 'lxml')

        page_content = soup.find_all('div', class_='iva-item-content-UnQQ4')
        content_list.append(page_content)

        page_count = soup.find_all('span', class_="pagination-item-JJq_j")
        amount_page = int(page_count[-2].text)

        p = 2

        # for i in tqdm(range(1)): # временно для скрапа по первой странице
        for i in tqdm(range(2, amount_page + 1)):  # скрап со второй страницы
            url = URL + '?p=' + str(p)
            response = requests.get(url=url, headers=HEADERS, timeout=9)
            soup = bs(response.content, 'lxml')

            page_content = soup.find_all('div', class_='iva-item-content-UnQQ4')

            if page_content != []:
                content_list.append(page_content)
                value = random.random()
                scaled_value = 1 + value * 3 - value / 9
                time.sleep(scaled_value)
                p += 1
            else:
                print('Пусто')
                break

        return content_list


def phone_pars(id):
    """Получаем телефон, если он доступен"""

    url = f'https://m.avito.ru/api/1/items/{id}/phone'
    params = {
        'key': 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir',
        'accept': 'application/json, text/plain, */*'
    }
    agent = random.choice(user_agent)
    headers = {"user-agent": f"{agent}"}

    # ip_my = my_ip() # опционально получаем свой IP
    ban = []  # создаём список забаненых IP
    bad = []  # плохие IP

    run = True
    while run:
        try:
            response = requests.get(url=url, headers=headers, params=params)
        except requests.exceptions.ConnectionError:
            print('Кажется слишком долго нет ответа...\nЖдём одну мнуту...')
            time.sleep(60)

        if response.status_code != 200:
            print('IP временно заблокирован.\nМинуточку, выбираю другой IP...')
            proxy = get_proxy(ban, bad)
            print(proxy)
            try:
                proxy = proxy[0]
            except TypeError:
                print('Перебрали весь список, идём по новой.')
                ban.clear()
                proxy = get_proxy(ban, bad)
                proxy = proxy[0]

            ban.append(proxy)
            bad.append(proxy[-1])
            session = requests.Session()
            session.proxies = {'http': proxy, 'https': proxy}
            agent = random.choice(user_agent)
            headers = {"user-agent": f"{agent}"}

            try:
                response = session.get(url=url, headers=headers, params=params, timeout=10)
                print(response)

            except requests.exceptions.ProxyError:
                print('Переподключение к сереверам AVITO...')
                time.sleep(random.randint(7, 15))

            except requests.exceptions.SSLError:
                print('Превышено число подключений...\nПереподключение через 10 сек')
                time.sleep(random.randint(5, 11))

            except requests.exceptions.ConnectTimeout:
                print('Сервер долго не отвечает...\nЖдёмс =)')
                time.sleep(random.randint(3, 13))

            except requests.exceptions.ConnectionError:
                print('Ошибка подключения...\nЖдёмс =)')
                time.sleep(random.randint(3, 13))

            except AttributeError:
                print('Был достигнут конец списка,\nи что-то пошло не так\nПробуем ещё раз...')
                time.sleep(1.618)

            except requests.exceptions.ReadTimeout:
                print('Error ReadTimeout...')
                time.sleep(1.618)

        else:
            run = False

    try:
        phone = response.json()['result']['action']['uri'].split('=')[-1]
        phone = phone.replace('%2B', '+')

    except KeyError:
        phone = 'НЕТ'

    print(phone)
    value = random.random()
    # TODO увеличить паузу до 6__8 сек скорей всего лимит 9 запросов в минуту

    scaled_value = (5.5 + value) * 1.618  # от 8.899 до 10.517 сек
    print(f'{scaled_value} секунд')
    time.sleep(scaled_value)
    print('#' * 20 + ' Собираю данные ' + '#' * 20)
    return phone


info = {}  # карточки объявлений


def content_pars():
    """Распарсиваем полученные блоки по содержимому."""

    content_list = page_pars()

    print(f'Всего {len(content_list)} карточек.')

    for tile in content_list:
        for cell in tqdm(tile):
            title = cell.find('h3', class_="title-root-j7cja").text
            price = cell.find('span', class_="price-price-BQkOZ").text

            if cell.find('span', class_="geo-address-QTv9k"):
                address = cell.find('span', class_="geo-address-QTv9k").get_text()

            if cell.find('div', class_="geo-georeferences-Yd_m5"):
                address = cell.find('div', class_="geo-georeferences-Yd_m5").get_text()

            try:
                description = cell.find('div', class_="iva-item-text-_s_vh").get_text()
            except AttributeError:
                description = '---'

            link = 'www.avito.ru' + cell.find('a', class_="iva-item-sliderLink-bJ9Pv").get('href')
            id = link.split('_')[-1]
            phone = phone_pars(id)

            if '?' in id:
                id = id.split('?')[0]  # бывает посли id идут параметры, отсеиваем их.

            info[id] = {
                'title': title,
                'price': price,
                'address': address,
                'description': description,
                'link': link,
                'phone': phone
            }

    return info


def write_to_json():
    """Записываем результаты, отсирторировав по ключу."""
    current_time = time.strftime('%Y-%m-%d_%H:%M')
    with open(f'info_{current_time}.json', 'w') as file:
        sorted_info = sorted(info.items(), key=lambda x: x[0])
        json.dump(dict(sorted_info), file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    start = time.time()
    pprint(content_pars())
    write_to_json()
    print(time.time() - start)
