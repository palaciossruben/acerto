"""Runs a good amount of simulations to estimate avg model accuracy"""
from match import learn

NUM_RUNS = 100

results = []
for _ in range(NUM_RUNS):
    _, result = learn.get_model()
    results.append(result)

while len(results) > 1:
    results[-2].average(results[-1])
    results.pop()

print('TRAIN ACCURACY: ' + str(results[0].train_accuracy_mean))
print('TEST ACCURACY: ' + str(results[0].test_accuracy_mean))
print('MY test accuracy: ' + str(results[0].my_test_accuracy))
print('RANDOM test accuracy: ' + str(results[0].random_test_accuracy))
