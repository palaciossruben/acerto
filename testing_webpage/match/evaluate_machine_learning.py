"""Runs a good amount of simulations to estimate avg model accuracy"""
import numpy as np
from match import learn


NUM_RUNS = 2
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
