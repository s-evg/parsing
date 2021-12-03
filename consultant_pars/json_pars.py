import json, openpyxl, time
from pprint import pprint
from tqdm import tqdm


start = time.time()

with open('consultant.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


book = openpyxl.Workbook()
sheet = book.active


sheet['A1'] = 'Категория 1'
sheet['B1'] = 'Категория 2'

row = 2
for key, val in tqdm(data.items()):
    sheet[row][0].value = key
    for v in val:
        sheet[row][1].value = v
        row += 1


book.save('consultant.xlsx')
book.close()
print(time.time() - start)
