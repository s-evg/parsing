import requests
from bs4 import BeautifulSoup as bs


url = "https://free-proxy-list.net/"
headers = {
"user-agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko)"
              "Chrome/95.0.4638.69 Mobile Safari/537.36"
}


def pars():
    """Парсим список доступных IP адресов."""

    response = requests.get(url=url, headers=headers)
    soup = bs(response.content, 'html.parser')
    proxy_list = soup.find('textarea').get_text().split('\n')[3:-1]
    return proxy_list


if __name__ == '__main__':
    pars()
