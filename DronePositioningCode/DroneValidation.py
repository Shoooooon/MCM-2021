import GeneralDroneGa as gg

'''
The goal of this file is to:
    a) Be able to produce meaningful data/datapoints on inputs and collections of inputs
    b) To validate good/stable convergence under the chosen parameters 

b) In general, I want to be able to run a problem n times with a set of parameters and measure the spread in fire coverage.
Then, I'd like to be able to graph each parameter against the coverage it gets me, or against a problem variable and see how quickly things get out of hand. 
'''



'''
Runs problem with specified parameters specified number of times, outputing the following data
Inputs:
    n - number of times to run trial
Outputs:
    list of tuples of (fitness, drone hrs/hr)
'''
def runTest(n, droneCount, fireCoords, batchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    output = []
    for i in range(n):
        survivor, fitness, dc = gg.runGA(droneCount, fireCoords, batchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)
        output.append((fitness, dc))
    return output

def fire_coverage_distribution(n, droneCount, fireCoords, batchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    dist = [i[0] - 1100 for i in runTest(100, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 10, 20, 3, -10, 10, 0, 40)]
    distribution = {}
    for d in dist:
        distribution[d] = 0
    for d in dist:
        distribution[d] += 1
    return distribution


print(fire_coverage_distribution(100, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 20, 40, 5, -10, 10, 0, 40))