import matplotlib
matplotlib.use('TkAgg')
from matplotlib.pylab import *
import matplotlib.animation as animation
import numpy as np

filename = "../data/June04_2019_Cleaned_dist.txt"

# Sent for figure
font = {'size': 9}
matplotlib.rc('font', **font)

# Setup figure and subplots
f0 = figure(num=0, figsize=(12, 8))  # , dpi = 100)
f0.suptitle("Bump Graph", fontsize=12)
ax01 = f0.add_subplot(111)

with open(filename) as f:
    content = f.readlines()
content = [x.strip() for x in content]
table = np.array([x.split(",") for x in content])
g1 = table[:,0].astype(np.float)
g2 = table[:,1].astype(np.float)
g3 = table[:,2].astype(np.float)
g4 = table[:,3].astype(np.float)
g5 = table[:,4].astype(np.float)
g6 = table[:,5].astype(np.float)

time = table[:,6].astype(np.datetime64)

lat = table[:,7].astype(np.float)
long = table[:,8].astype(np.float)
atl = table[:,9].astype(np.float)
speed = table[:,10].astype(np.float)
distance = table[:,11].astype(np.float)

base_time = time[0]
delta_time = [(probe - base_time).item().total_seconds() for probe in time]

# Set titles of subplots
ax01.set_title('speed, delta distance vs Time')

# set y-limits
ax01.set_ylim(0, 20)

# sex x-limits
ax01.set_xlim(0, 200.0)

# Turn on grids
ax01.grid(True)

# set label names
ax01.set_xlabel("Delta Time (secs)")
ax01.set_ylabel("Speed, Distance")

# Data Placeholders
yp1 = zeros(0)
yp2 = zeros(0)
t = zeros(0)

# set plots
p11, = ax01.plot(t, yp1, 'b-', label="speed")
p12, = ax01.plot(t, yp2, 'g-', label="distance")

# set lagends
ax01.legend([p11, p12],
            [p11.get_label(), p12.get_label()]
            )

# Scrolling Update
x_start = 0.0
x_width = 200.0


def update_data(index):
    global x_start
    global x_width
    global yp1
    global yp2
    global t
    global speed
    global distance
    global delta_time

    yp1 = append(yp1, speed[index])
    yp2 = append(yp2, distance[index])
    t = append(t, delta_time[index])

    p11.set_data(t, yp1)
    p12.set_data(t, yp2)

    x = delta_time[index] - x_start
    if x >= x_width:
        x_start = x - x_width
        xmin = x_start
        xmax = x_start + x_width
        p11.axes.set_xlim(xmin, xmax)
        p12.axes.set_xlim(xmin, xmax)

    return p11, p12


# interval: draw new frame every 'interval' ms
# frames: number of frames to draw
simulation = animation.FuncAnimation(f0, update_data,
                                     blit=False, frames=len(delta_time), interval=20, repeat=False)

# Uncomment the next line if you want to save the animation
# simulation.save(filename='sim.mp4',fps=30,dpi=300)

plt.show()
