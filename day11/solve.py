# DAY 11
from collections import defaultdict
import math
import numpy as np

file = open("day11/input.txt")
input = list(map(int, file.readline().split(","))) + list(map(int,list('0'*1000000)))

i = 0
rel_base = 0
paint = defaultdict(lambda: 0)
curr_i, curr_j = 0, 0

# 0 for part 1, 1 for part 2
paint[(0,0)] = 1
angle = 90
instruct = []

def index(param, off):
    if param == '0':
        return input[i+off]
    elif param == '1':
        return i+off
    else:
        return input[i+off]+rel_base

while True:
    op = str(input[i])[-2:].zfill(2)
    param = str(input[i])[:-2].zfill(3)
    if op == '01':
        input[int(index(param[0], 3))] = input[int(index(param[2], 1))] + input[int(index(param[1], 2))]
        i+=4
    elif op == '02':
        input[int(index(param[0], 3))] = input[int(index(param[2], 1))] * input[int(index(param[1], 2))]
        i+=4
    elif op == '03':
        input[int(index(param[2], 1))] = paint[(curr_i, curr_j)]
        i+=2
    elif op == '04':
        instruct.append(int(input[int(index(param[2], 1))]))
        if len(instruct) == 2:
            paint[(curr_i, curr_j)] = instruct[0]
            angle += 90 if instruct[1] else -90
            curr_i += round(math.cos(math.radians(angle)))
            curr_j += round(math.sin(math.radians(angle)))
            instruct = []
        i+=2
    elif op == '05':
        if input[int(index(param[2], 1))] != 0:
            i = input[int(index(param[1], 2))]
        else:
            i+=3
    elif op == '06':
        if input[int(index(param[2], 1))] == 0:
            i = input[int(index(param[1], 2))]
        else:
            i+=3
    elif op == '07':
        input[int(index(param[0], 3))] = int(input[int(index(param[2], 1))] < input[int(index(param[1], 2))])
        i+=4
    elif op == '08':
        input[int(index(param[0], 3))] = int(input[int(index(param[2], 1))] == input[int(index(param[1], 2))])
        i+=4
    elif op == '09':
        rel_base += input[int(index(param[2], 1))]
        i+=2
    elif op == '99':
        break
    else:
        print(op)

min_x = min(paint.keys(), key=lambda x: x[0])[0]
min_y = min(paint.keys(), key=lambda x: x[1])[1]

board = np.zeros((-min_x+1, -min_y+1))

for k,v in paint.items():
    board[k[0]][-k[1]] = v
print(len(paint.keys()))
res = np.where(board==0, ' ', board)
res = np.where(board==1, '■', res)
print(res)