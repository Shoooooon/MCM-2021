import GeneralDroneGa as gg
import concurrent.futures
import numpy as np
import cProfile

'''
The goal of this file is to:
    a) Be able to produce meaningful data/datapoints on inputs and collections of inputs
    b) To validate good/stable convergence under the chosen parameters 

b) In general, I want to be able to run a problem n times with a set of parameters and measure the spread in fire coverage.
Then, I'd like to be able to graph each parameter against the coverage it gets me, or against a problem variable and see how quickly things get out of hand. 

The most important parameter is probably # generations. We want to convince judges we ran for long enough to converge to a good solution.
'''

'''
Takes a list of values and expresses them as dict
'''
def list_to_dict(values):
    d = {}
    for v in values:
        d[v] = 0
    for v in values:
        d[v] += 1
    return d



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
    if None in output:
        return None
    return output

def fire_coverage_distribution(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    dist = [i[0] for i in runTest(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)]
    return list_to_dict(dist)





# def lambda_for_parallel():
#     [[x[1:] for x in gg.runGA_output_all_gens(droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)] for p in range(nList(k),nList(k+1))]

'''
Returns list of runs
Each run is a list of (best values, droneCount) tuples
'''
def runTest_all_gen_output(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    tasks = [None] * 10
    output = []
    # # nList = [0, int(n/10), 2*int(n/10), 3*int(n/10), 4*int(n/10), 5*int(n/10), 6*int(n/10), 7*int(n/10), 8*int(n/10), 9*int(n/10), n]
    # executor = concurrent.futures.ThreadPoolExecutor()
    # # Parallelize, but only make like 10 threads bc the 100 thread overhead killed it
    # for k in range(10):
    #     tasks[k] = executor.submit(lambda : [[x[1:] for x in gg.runGA_output_all_gens(droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)] for p in range(nList[k],nList[k+1])])
    # for i in range(10):
    #     for out in tasks[i].result():
    #         output.append(out)
    output = [[x[1:] for x in gg.runGA_output_all_gens(droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)] for p in range(n)]
    if None in output:
        return None
    return output


def distribution_by_runs(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    distributions = [0] * (generations + 1)
    data = runTest_all_gen_output(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)
    if data == None:
        return None
    for j in range(generations + 1):
        jthRuns = [datum[j] for datum in data]
        dist = [run[0] for run in jthRuns]
        distributions[j] = list_to_dict(dist)
    return distributions






# print(fire_coverage_distribution(50, 1, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 3, -10, 10, 0, 40))
# print(fire_coverage_distribution(50, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 4, -10, 10, 0, 40))
# print(fire_coverage_distribution(50, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 5, -10, 10, 0, 40))
# print(fire_coverage_distribution(50, 3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 15, 30, 6, -10, 10, 0, 40))


# testCase2 = [(-30,32),(-30,30),(-30,28),(0,0),(30,32),(30,30),(30,28)]
# print(distribution_by_runs(25, 14, testCase2, 10, 30, 8, -55, 55, -55, 55))


testCase3 = [(-27,0),(-25,3),(0,27),(25,3),(27,0)]
# print(distribution_by_runs(5, 6, testCase3, 10, 30, 1, -60, 60, -60, 60))
# print(fire_coverage_distribution(50, 4, testCase3, 10, 30, 6, -60, 60, -60, 60))

# [print(i) for i in distribution_by_runs(50, 10, testCase3, 10, 30, 8, -60, 60, -60, 60)]

testCase4 = [(np.random.uniform(-50.0,50.0),np.random.uniform(-50.0,50.0)) for i in range(20)]
# a = distribution_by_runs(50, 20, testCase4, 10, 30, 5, -70, 70, -70, 70)
# [print(i) for i in a]

# b = distribution_by_runs(50, 20, testCase4, 30, 60, 5, -70, 70, -70, 70)
# [print(i) for i in b]

# [print(sum([cover*frequency/float(50) for (cover,frequency) in i.items()])) for i in a]

# cProfile.run('distribution_by_runs(1, 10, testCase4, 10, 30, 20, -100, 100, -100, 100)')
cProfile.run('distribution_by_runs(1, 6, testCase3, 10, 30, 40, -60, 60, -60, 60)')
# cProfile.run('[gg.get_range((10.5,10.5,),20,60,60) for i in range(1000)]')
