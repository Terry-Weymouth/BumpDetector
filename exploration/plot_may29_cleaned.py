import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

filename = "data/May29_2019_Cleaned_Data_Records.txt"

with open(filename) as f:
    content = f.readlines()
content = [x.strip() for x in content]
table = np.array([x.split(",") for x in content])
g1 = table[:,0].astype(float)
g2 = table[:,1].astype(float)
g3 = table[:,2].astype(float)
g4 = table[:,3].astype(float)
g5 = table[:,4].astype(float)
g6 = table[:,5].astype(float)

time = table[:,6].astype(np.datetime64)

lat = table[:,7].astype(float)
long = table[:,8].astype(float)
atl = table[:,9].astype(float)
speed = table[:,10].astype(float)

plt.figure(1)
plt.plot(time, g3)

plt.xlabel('time (s)')
plt.ylabel('accel-g3)')
plt.title('Bumps?')

plt.show()

print("Done")
