from pprint import pprint
from random import randint as random

arr = ['white', 'red', 'blue', 'green', 'black', 'yellow', 'pink']

"""
Вероятность:
'white' => 30%
'pink' => 5%
"""

var = []
for n in range(30, 4, -1):
    var.append(n)

var = sum(var)

band = []

for k in range(len(arr) + 1):
    q = var * 1000 // (k + 1)
    band.append(q)
# print(band)

c = []
for b in range(len(band) - 1):
    c.append([band[b], band[b + 1]])
# print(c)

color = []
for q in range(1001):
    n = random(0, var * 1000)
    # print(n)
    for k in c:
        if k[0] >= n >= k[1]:
            index = c.index(k)
            color.append(arr[index])
# pprint(color)
colors = {}


for col in color:
    if col not in colors:
        colors[col] = 1
    if col in colors:
        colors[col] += 1


pprint(colors)

