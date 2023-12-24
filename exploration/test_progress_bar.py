from src.lib.progress_bar import print_progress, clear_progress
from time import sleep


print('testing progress bar')

for n in range(10, 211):
    print_progress(n, 10, 210)
    sleep(0.2)
clear_progress(' -- done')
