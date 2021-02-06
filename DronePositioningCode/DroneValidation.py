import GeneralDroneGa as gg
import concurrent.futures

'''
The goal of this file is to:
    a) Be able to produce meaningful data/datapoints on inputs and collections of inputs
    b) To validate good/stable convergence under the chosen parameters 

b) In general, I want to be able to run a problem n times with a set of parameters and measure the spread in fire coverage.
Then, I'd like to be able to graph each parameter against the coverage it gets me, or against a problem variable and see how quickly things get out of hand. 

The most important parameter is probably # generations. We want to convince judges we ran for long enough to converge to a good solution.
'''



'''
Runs problem with specified parameters specified number of times, outputing the following data
Inputs:
    n - number of times to run trial
Outputs:
    list of tuples of (fitness, drone hrs/hr)
'''
def runTest(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    output = [0] * n
    tasks = [None] * n
    executor = concurrent.futures.ThreadPoolExecutor()
    for i in range(n):
        tasks[i] = executor.submit(lambda: gg.runGA(droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound) [1:])
    for i in range(n):
        output[i] = tasks[i].result()
    return output

def fire_coverage_distribution(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    dist = [i[0] - 1100 for i in runTest(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)]
    distribution = {}
    for d in dist:
        distribution[d] = 0
    for d in dist:
        distribution[d] += 1
    return distribution


print(fire_coverage_distribution(50, 1, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 3, -10, 10, 0, 40))
# print(fire_coverage_distribution(50, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 4, -10, 10, 0, 40))
# print(fire_coverage_distribution(50, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 5, -10, 10, 0, 40))
# print(fire_coverage_distribution(50, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 6, -10, 10, 0, 40))


testCase2 = [(-15,-15),(-15,15),(0,0),(15,-15),(15,15),]
print(fire_coverage_distribution(50, 3, testCase2, 10, 20, 3, -15, 15, -15, 15))

'''
Some ideas:
. Allow larger km jumps in parents?
'''