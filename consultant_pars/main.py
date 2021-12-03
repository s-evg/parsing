import json

import requests, lxml, time, random
from bs4 import BeautifulSoup as bs
from tqdm import tqdm


URL = 'https://www.consultant.ru/cons/cgi/online.cgi?'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
           'accept': '*/*'}
PARAMS_1 = {
    'rnd': '1A2706C5F50E9F59F533F30C8CC392C8',
    'req': 'sit1',
    # 'pars': 0-500,
}

kat = {}


def pars(**kwargs):
    """Парсим страничку Правовой навигатор"""

    response = requests.get(**kwargs)

    if response.status_code != 200:
        print('Сайт не доступен!')

    else:
        soup = bs(response.content, 'lxml')
        print(soup)
        kat_1 = soup.find_all('s')
        name_kat_1 = []
        name_kat_2 = []
        # kat = {}
        for k in tqdm(kat_1):
            sit1 = int(k.get('id'))
            k = k.get('t')
            name_kat_1.append(k)
            # print(k)
            # print(name_kat_1)
            kat[k] = []
            PARAMS_2 = {
                'rnd': '1A2706C5F50E9F59F533F30C8CC392C8',
                'req': 'sit2',
                'sit1': sit1
                # 'pars': 0-500,
            }
            resp = requests.get(url=URL, headers=HEADERS, params=PARAMS_2)
            if response.status_code != 200:
                print('Страница не доступна!')
            else:
                soup = bs(resp.content, 'lxml')
                kat_2 = soup.find_all('s')
                for m in kat_2:
                    m = m.get('t')
                    name_kat_2.append(m)
                    # print(m)
                    # print(name_kat_2)
                    kat[k].append(m)

                delay = random.randint(3, 99)
                time.sleep(delay / 99)
                # print(soup)

        print(name_kat_1)
        print(name_kat_2)
        # print(kat)


if __name__ == '__main__':
    start = time.time()
    pars(url=URL, headers=HEADERS, params=PARAMS_1)
    # print(kat)
    with open('consultant.json', 'w') as file:
        json.dump(kat, file, indent=2)
    print(time.time() - start)
