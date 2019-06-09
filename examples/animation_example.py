import matplotlib
matplotlib.use('TkAgg')
from matplotlib.pylab import *
import matplotlib.animation as animation

# Sent for figure
font = {'size': 9}
matplotlib.rc('font', **font)

# Setup figure and subplots
f0 = figure(num=0, figsize=(12, 8))  # , dpi = 100)
f0.suptitle("Oscillation decay", fontsize=12)
ax01 = f0.add_subplot(111)
ax02 = ax01.twinx()

# Set titles of subplots
ax01.set_title('Position vs Time')

# set y-limits
ax01.set_ylim(0, 2)
ax02.set_ylim(-6, 6)

# sex x-limits
ax01.set_xlim(0, 5.0)
ax02.set_xlim(0, 5.0)

# Turn on grids
ax01.grid(True)
ax02.grid(True)

# set label names
ax01.set_xlabel("x")
ax01.set_ylabel("py")
ax02.set_xlabel("t")
ax02.set_ylabel("vy")

# Data Placeholders
yp1 = zeros(0)
yv1 = zeros(0)
yp2 = zeros(0)
yv2 = zeros(0)
t = zeros(0)

# set plots
p11, = ax01.plot(t, yp1, 'b-', label="yp1")
p12, = ax01.plot(t, yp2, 'g-', label="yp2")

p21, = ax02.plot(t, yv1, 'b-', label="yv1")
p22, = ax02.plot(t, yv2, 'g-', label="yv2")

# set lagends
ax01.legend([p11, p12], [p11.get_label(), p12.get_label()])
ax02.legend([p21, p22], [p21.get_label(), p22.get_label()])

# Data Update
xmin = 0.0
xmax = 5.0
x = 0.0


def update_data(self):
    global x
    global yp1
    global yv1
    global yp2
    global yv2
    global t

    tmpp1 = 1 + exp(-x) * sin(2 * pi * x)
    tmpv1 = - exp(-x) * sin(2 * pi * x) + exp(-x) * cos(2 * pi * x) * 2 * pi
    yp1 = append(yp1, tmpp1)
    yv1 = append(yv1, tmpv1)
    yp2 = append(yp2, 0.5 * tmpp1)
    yv2 = append(yv2, 0.5 * tmpv1)
    t = append(t, x)

    x += 0.05

    p11.set_data(t, yp1)
    p12.set_data(t, yp2)

    p21.set_data(t, yv1)
    p22.set_data(t, yv2)

    if x >= xmax - 1.00:
        p11.axes.set_xlim(x - xmax + 1.0, x + 1.0)
        p21.axes.set_xlim(x - xmax + 1.0, x + 1.0)

    return p11, p12, p21, p22


# interval: draw new frame every 'interval' ms
# frames: number of frames to draw
simulation = animation.FuncAnimation(f0, update_data, blit=False, frames=200, interval=20, repeat=False)

# Uncomment the next line if you want to save the animation
# simulation.save(filename='sim.mp4',fps=30,dpi=300)

plt.show()
