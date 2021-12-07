import json, csv
from pprint import pprint

from bs4 import BeautifulSoup as bs
import requests, time, lxml, random
from openpyxl import Workbook
from tqdm import tqdm

from worker_proxy import get_proxy, my_ip
from user_agent_mobile import mobile
from user_agent_desktop import desktop


URL = input('Введите адрес раздела AVITO для парсинга:\n>>> ')
desktop_agent = random.choice(desktop)
HEADERS = {"user-agent": f"{desktop_agent}"}


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

        page_count = soup.find_all('span', class_="pagination-item-JJq_j")
        amount_page = int(page_count[-2].text)
        print(f'Всего {amount_page} страниц.')
        time.sleep(3)

        p = 1
        for i in tqdm(range(amount_page)):  # скрап со второй страницы
            url = URL + '?p=' + str(p)
            response = requests.get(url=url, headers=HEADERS, timeout=9)
            soup = bs(response.content, 'lxml')

            page_content = soup.find_all('div', class_='iva-item-content-UnQQ4')

            if page_content != []:
                for advert in page_content:
                    content_list.append(advert)
                value = random.random()
                scaled_value = 1 + value * 3 - value / 9
                time.sleep(scaled_value)
                p += 1

            else:
                print('Пусто')
                break

        return content_list


# ip_my = my_ip() # опционально получаем свой IP
ban = []  # создаём список забаненых IP
bad = []  # плохие IP


def phone_pars(id):
    """Получаем телефон, если он доступен"""

    url = f'https://m.avito.ru/api/1/items/{id}/phone'
    params = {
        'key': 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir',
        'accept': 'application/json, text/plain, */*'
    }

    mobile_agent = random.choice(mobile)
    headers = {"user-agent": f"{mobile_agent}"}



    run = True
    while run:
        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            run = False

        else:
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

        try:
            response = requests.get(url=url, headers=headers, params=params)

        except requests.exceptions.ProxyError:
            print('Переподключение к сереверам AVITO...')
            time.sleep(random.randint(7, 15))

        except requests.exceptions.SSLError:
            print('Превышено число подключений...\nПереподключение через 10 сек')
            time.sleep(random.randint(5, 11))

        except requests.exceptions.ConnectTimeout:
            print('Сервер долго не отвечает...\nЖдёмс =)')
            time.sleep(random.randint(3, 13))

        except AttributeError:
            print('Был достигнут конец списка,\nи что-то пошло не так\nПробуем ещё раз...')
            time.sleep(1.618)

        except requests.exceptions.ReadTimeout:
            print('Error ReadTimeout...')
            time.sleep(1.618)

        except requests.exceptions.ConnectionError:
            print('Кажется слишком долго нет ответа...\nЖдём одну минуту...')
            time.sleep(60)

    try:
        phone = response.json()['result']['action']['uri'].split('=')[-1]
        phone = phone.replace('%2B', '+')
        if 'authenticate' in phone:
            phone = 'Телефон скрыт'

    except KeyError:
        phone = 'Телефон не указан'

    # print(phone)

    value = random.random()
    scaled_value = (5.5 + value) * 1.618  # от 8.899 до 10.517 сек
    # print(f'Спим {scaled_value} секунд')
    time.sleep(scaled_value)

    return phone


info = []  # карточки объявлений


def content_pars():
    """Распарсиваем полученные блоки по содержимому."""

    content_list = page_pars()
    print('#' * 25 + ' Собираю данные ' + '#' * 25)

    for cell in tqdm(content_list):
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
        """
        Если собирать то по api это очень долго (пока),
        возможно распознание изображение с телефоном будет быстрее...
        """
        phone = phone_pars(id)  # TODO сделать возможность выбора: собирать телефон или нет
        # phone = 'test'   # затычка для ускорения процесса

        if '?' in id:
            id = id.split('?')[0]  # бывает посли id идут параметры, отсеиваем их.

        info.append({
            'id': id,
            'title': title,
            'price': price,
            'address': address,
            'description': description,
            'link': link,
            'phone': phone
        })

    return info


current_time = time.strftime('%Y-%m-%d_%H:%M')


def write_to_json():
    """Записываем результаты, отсирторировав по ключу в JSON"""
    with open(f'info_{current_time}.json', 'w') as file:
        json.dump(info, file, ensure_ascii=False, indent=2)


def write_to_csv():
    """Записываем результаты, отсортировав по ключу в CSV"""
    csv_columns = ["id", "title", "price", "address", "description", "link", "phone"]
    with open(f'info_{current_time}.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns, delimiter=';')
        writer.writeheader()
        for data in info:
            writer.writerow(data)


def write_to_xlsx():
    """Записываем полученнные данные в xlsx"""

    book = Workbook()
    sheet = book.active

    sheet['A1'] = 'ID'
    sheet['B1'] = 'ЗАГОЛОВОК'
    sheet['C1'] = 'ЦЕНА'
    sheet['D1'] = 'АДРЕС'
    sheet['E1'] = 'ОПИСАНИЕ'
    sheet['F1'] = 'ССЫЛКА'
    sheet['G1'] = 'ТЕЛЕФОН'

    row = 2
    for r in info:
        sheet[row][0].value = r['id']
        sheet[row][1].value = r['title']
        sheet[row][2].value = r['price']
        sheet[row][3].value = r['address']
        sheet[row][4].value = r['description']
        sheet[row][5].value = r['link']
        sheet[row][6].value = r['phone']
        row += 1

    book.save(f'info_{current_time}.xlsx')
    book.close()


if __name__ == '__main__':
    start = time.time()
    content_pars()
    write_to_xlsx()
    print(time.time() - start)
