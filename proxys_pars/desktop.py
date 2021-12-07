from bs4 import BeautifulSoup as bs
import requests


url = 'https://useragents.ru/stable.html'


resp = requests.get(url=url)

soup = bs(resp.content, 'html.parser')

user_agent = soup.find('div', id="wb_Text3")

user = user_agent.get_text(separator='|').split('|')[1:-1]

with open('../AVITO/user_agent_desktop.py', 'w') as file:
    file.write(f'desktop = {user}')


print(user)