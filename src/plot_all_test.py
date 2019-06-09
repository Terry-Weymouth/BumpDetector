import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

filename = "../May21_2019_Bump-FirstRun.txt"

with open(filename) as f:
    content = f.readlines()
content = [x.strip() for x in content]

x = []
value1 = []
value2 = []
for line in content:
    parts = line.split(":")
    n = int(parts[0])
    values = parts[1].split(",")
    v1 = int(values[0])
    v2 = int(values[1])
    x.append(n)
    value1.append(v1)
    value2.append(v2)

print("Got data", len(x), len(value1), len(value2))
limit = len(content)
length = 1000

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)

x = range(0,length)
y1 = value1[0:length]
y2 = value2[0:length]
line1, line2 = ax.plot(x, y1, 'r-', x, y2, 'b-')

print("Start scroll", limit)

time.sleep(3)

for base in range(0, limit-length):
    print(base)
    new_y1 = value1[base : base + length]
    new_y2 = value2[base : base + length]
    line1.set_ydata(new_y1)
    line2.set_ydata(new_y2)
    fig.canvas.draw()
    time.sleep(0.1)

print("Done")
exit(0)