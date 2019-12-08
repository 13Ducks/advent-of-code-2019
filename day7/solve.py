# DAY 5

import itertools

file = open("day7/input.txt")
input_data = list(map(int, file.readline().split(",")))

def solve(phase, val, data, first_input, i):
    def index(param, off):
        if param == '0':
            return data[i+off]
        else:
            return i+off

    while True:
        op = str(data[i])[-2:].zfill(2)
        param = str(data[i])[:-2].zfill(3)
        if op == '01':
            data[int(index(param[0], 3))] = data[int(index(param[2], 1))] + data[int(index(param[1], 2))]
            i+=4
        elif op == '02':
            data[int(index(param[0], 3))] = data[int(index(param[2], 1))] * data[int(index(param[1], 2))]
            i+=4
        elif op == '03':
            if not first_input:
                data[int(index(param[2], 1))] = phase
                first_input = True
            else:
                data[int(index(param[2], 1))] = val
            i+=2
        elif op == '04':
            return [data[int(index(param[2], 1))], data, i]
        elif op == '05':
            if data[int(index(param[2], 1))] != 0:
                i = data[int(index(param[1], 2))]
            else:
                i+=3
        elif op == '06':
            if data[int(index(param[2], 1))] == 0:
                i = data[int(index(param[1], 2))]
            else:
                i+=3
        elif op == '07':
            data[int(index(param[0], 3))] = int(data[int(index(param[2], 1))] < data[int(index(param[1], 2))])
            i+=4
        elif op == '08':
            data[int(index(param[0], 3))] = int(data[int(index(param[2], 1))] == data[int(index(param[1], 2))])
            i+=4
        elif op == '99':
            return False
        else:
            print(op)

all = list(itertools.permutations([0,1,2,3,4]))
out = []
for a in all:
    o = 0
    for l in a:
        o = solve(l,o,input_data.copy(),False,0)[0]
    out.append(o)
print(max(out))

all = [[9,8,7,6,5]] #should produce 139629729
out = []
for a in all:
    curr_data = input_data.copy()
    o = 0
    amps = []
    for l in a:
        res = solve(l,o,curr_data,False,0)
        print(res)
        amps.append(res.copy())
        o = res[0]
    for b in amps:
        print(b)
    # for i in range(1):
    #     for i in range(5):
    #         res = solve("",o,amps[i][0],True,amps[i][1]+2)
    #         if not res:
    #             print(i,"DONE")
    #             break
    #         o = res[0]
    #         amps[0] = (res[1],res[2])
    #         print(o)

    # for a in amps:
    #     print(a)
