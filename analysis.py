import pickle
import numpy as np
from collections import defaultdict
import pprint 

# keys only
data = loaded_log['key_history']

keys = [key_stroke for _, key_stroke in data]

# unique keys pressed
key_set = []
for stroke in keys:
    if stroke not in key_set:
        key_set.append(stroke)

key_histogram = defaultdict(int)

for stroke in keys:
    key_histogram[tuple(stroke)] += 1

timestamps = [timestamp for timestamp, _ in data]

