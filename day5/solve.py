# DAY 5

file = open("day5/input.txt")
input = list(map(int, file.readline().split(",")))
ac = 5
i = 0

def index(param, off):
    if param == '0':
        return input[i+off]
    else:
        return i+off

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
        input[int(index(param[2], 1))] = ac
        i+=2
    elif op == '04':
        print(input[int(index(param[2], 1))])
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
    elif op == '99':
        break
    else:
        print(op)