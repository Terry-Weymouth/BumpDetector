import numpy as np

file_in = "../May29_2019_Cleaned.txt"
file_out_a = "../May29_2019_Segment_A.txt"
file_out_b = "../May29_2019_Segment_B.txt"

seg1_end = 318
seg2_start = 319

with open(file_in) as f:
    content = f.readlines()
content = [x.strip() for x in content]

with open(file_out_a, "w") as fa:
    for i in range(0,318):
        fa.write("{}\n".format(content[i]))

with open(file_out_b, "w") as fb:
    for i in range(319, len(content)):
        fb.write("{}\n".format(content[i]))

