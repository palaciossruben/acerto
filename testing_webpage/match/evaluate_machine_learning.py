"""Runs a good amount of simulations to estimate avg model accuracy"""
import time
import numpy as np
from match import learn

start_time = time.time()

NUM_RUNS = 10
np.random.seed(1)  # Predictable randomness


results = []
for _ in range(NUM_RUNS):
    _, result = learn.get_model(regression=False)
    results.append(result)

while len(results) > 1:
    results[-2].average(results[-1])
    results.pop()

print('\n\nSUMMARY:')
results[0].print()

print("TOTAL TIME: " + str(time.time() - start_time))
