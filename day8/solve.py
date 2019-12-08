# DAY 6
from collections import Counter

file = open("day8/input.txt")
data = file.readline()
width=25
height=6
layers=[]
for i in range(0,len(data),width*height):
    layers.append(data[i:i+width*height])

count = [Counter(i) for i in layers]
correct = min(count,key=lambda x: x['0'])
print(correct['2']*correct['1'])

ans = []
for i in range(width*height):
    pixels = [x[i] for x in layers if x[i] == '0' or x[i] == '1']
    ans.append(pixels[0])

for h in range(height):
    print(''.join(ans[h*width:(h+1)*width]).replace("0"," "))