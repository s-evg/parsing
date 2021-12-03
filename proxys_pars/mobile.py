from bs4 import BeautifulSoup as bs
import requests


url = 'https://useragents.ru/mobile.html'


resp = requests.get(url=url)

soup = bs(resp.content, 'html.parser')

user_agent = soup.find('div', id="wb_Text3")

user = user_agent.get_text(separator='|').split('|')[1:-1]

with open('user_agent_mobile.py', 'w') as file:
    file.write(f'user_agent = {user}')


print(user)
