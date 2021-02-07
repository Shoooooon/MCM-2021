import numpy as np
import random
import matplotlib
import math
from PointSupporter import PointMaster

'''
We are re-working this file from the version in the other folder.
The new concept is grid-based, we overlay a grid onto the domain, and the drones can be put at the centers of the grid boxes.
Each box gets a fire count based on the fire in it.
Then the comparisons and checking of fitness are a lot easier bc given a drone position, I can easily check only the nearby boxes to see how many fires it touches.
Let's do 1kmx1km boxes.
Also, let's take advantage of this to clean up some.
'''

### Changes:
# Drone signal range - drone2drone = 20, drone2fire = 5 --- adjust globals and fitness accordingly


EOC_FROM_FIRE = 20                          # Minimum distance EOC needs to be from an active fire point - Note that there are 2 such variables in this folder, so when you change one you should change both
RECHARGE_TIME = 1.75                        # Time it takes dronesto recharge
DRONE_SPEED = 1.2 * 60                      # km/hr
BATTERY_LIFE = 2.5                          # Hours before recharge required
DRONE2DRONE_SIGNAL_RANGE = 20               # Drone signal range to other drones (km)
DRONE2MAN_SIGNAL_RANGE = 5                  # Drone signal range to people and SSA drones (km)
BOX_SIZE = 1                                # Each box is 1km x 1km
SQRT2 = 1.4143

'''
Helper Functions
'''

'''
Gets best survivor from batch
'''
def best_survivor(gen, pointSupp):
    # Choose best survivor
    fit = 0
    best = None
    for survivor in gen:
        score = fitness(survivor, pointSupp)
        if score > fit:
            fit = score
            best = survivor
    return(best, fit)


'''
Returns true if eoc is not within range of any fire - false otherwise
'''
def check_eoc_safety(eoc, pointSupp):
    fireCoords = pointSupp.get_contained_points()
    for fireFree in pointSupp.get_range(eoc, EOC_FROM_FIRE):
        if fireFree in fireCoords:
            return False
    return True




'''
Major functions
'''

'''
LIMITING FUNCTION - EXTREMELY SLOW - SEND HELP
Direct fitness function for drone placement
Reevaluate later based on literature for smoother measures and better counting
It turns out we can't do better, so we'll stick with this.
Over enough time, we get convergence to good values anyway.

Note that the "fires" in fire coords are grid blocks on fire. The numFires is just the number of fires in such a block
Inputs:
    Proposal - ((eoc.x, eoc.y), {(drone1.x,drone1.y)...(dronen.x,dronen.y)})
    pointSupp - PointMaster object containing fire'''
def fitness(proposal, pointSupp):
    eoc = proposal[0]
    fireCoordsWeighted = pointSupp.get_contained_weighted_points()
    
    # Reward by fire coverage
    fitScore = 0
    # Get drones in range of EOC
    inrange = {eoc}
    changed = True
    while changed:
        changed = False
        adders = set()
        for drone in (proposal[1] - inrange):
            for node in pointSupp.get_range(drone, DRONE2DRONE_SIGNAL_RANGE):
                if node in inrange:
                    adders.add(drone)
                    changed = True
                    break
        inrange = inrange | adders                      # Union
    # Count fires in range of EOC

    # Get full range network can hit drone2man
    fireRange = set()                                           
    for drone in inrange:
        fireRange |= pointSupp.get_range(drone, DRONE2MAN_SIGNAL_RANGE)    
    # Count fires covered
    fitScore = sum([fire[2] for fire in list(filter(lambda fire: fire[:2] in fireRange, fireCoordsWeighted))])         # Could weight this by brightness or other fire-importance metric
    return fitScore

'''
Make one gen0 proposal
'''
def intialize_parent(droneCount, pointSupp):
    # Get all possible EOC placements and try them. If none work then there is a major problem.
    options = pointSupp.get_all_points()
    random.shuffle(options)
    eoc = None
    for option in options:
        if check_eoc_safety(option, pointSupp):
            eoc = option
            break
    if eoc == None:
        print('Could not get safe EOC.')
        return None
    
    # Pick points in range of current setup until cannot add drones
    network = {eoc}
    for i in range(droneCount):  
        fullRange = set()                                           # Get full range network can hit drone2drone
        for drone in network:
            fullRange |= pointSupp.get_range(drone, DRONE2DRONE_SIGNAL_RANGE)    

        
        halfRange = set()                                           # Get halved range to force new drones to be on outer parts of structure
        for drone in network:
            halfRange |= pointSupp.get_range(drone, DRONE2DRONE_SIGNAL_RANGE/2)                                       
        
        if len(fullRange - halfRange) != 0:                         # If we can add far-ish drone, do so
            network.add(random.choice(list(fullRange - halfRange)))

        elif len(fullRange - network) != 0:                         # Else, add whatever you can
            network.add(random.choice(list(fullRange - network)))

        else:                                                       # Otherwise we have all possible drones in the range, so we are sitting pretty and need not add more
            print("TOO MANY DRONES ALLOCATED FOR SIZE - not really an error, but inefficient")
                      
    if len(network) - 1 != droneCount:
        print("oof drone count is off in parent creation")
    return (eoc, network - {eoc})



'''
Make all gen0 proposals that will later be evolved over time - done
'''
def intialize_parents(droneCount, culledBatchSize, unculledBatchSize, pointSupp):
    # Assume there is a safe place to put EOC - fix later if necessary
    a = [intialize_parent(droneCount, pointSupp) for i in range(unculledBatchSize)]
    a = list(filter(lambda x: x != None, a))
    if len(a) < unculledBatchSize/2.0:
        return None
    return cull([intialize_parent(droneCount, pointSupp) for i in range(unculledBatchSize)], culledBatchSize, lambda kid: fitness(kid, pointSupp), 0, 1)



'''
Make kid off of 1 proposal - done
'''    
def spawn_kid(parent, pointSupp):
    kid = [parent[0], set()]
    
    # Try to move EOC randomly 1 step, only allow if safe distance from fire
    newEOC = random.choice(list(pointSupp.get_range(kid[0], SQRT2 * BOX_SIZE)))
    if check_eoc_safety(newEOC, pointSupp):
        kid[0] = newEOC

    # Move the drones randomly, by random degrees of extremeness.
    droneLog = set(parent[1])
    for drone in parent[1]:
        # Small chance of killing and replacing drone (5%) - In case high number of drones and we get a poorly seeded drone in an otherwise good candidate
        # On larger fire areas, I'm hoping this will be a useful Mulligan
        droneLog.remove(drone)
        if np.random.uniform(0,100) < 95:
            loc = random.choice(list(pointSupp.get_range(drone, SQRT2 * BOX_SIZE) - droneLog))                     # Adjacent unoccupied points - can alwasy stay still
        else:
            fullRange = set()                                                       # Get full range network that can hit drone2drone
            for drone in droneLog:
                fullRange |= pointSupp.get_range(drone, DRONE2DRONE_SIGNAL_RANGE)                                         
            loc = random.choice(list(fullRange - droneLog))
        droneLog.add(loc)
        kid[1].add(loc)

            


    # # Small chance of spawning drone (1%)
    # if np.random.uniform(0,100) > 99:
    #     node = random.choice(tuple([parent[0]] + list(parent[1])))                    # Choose node to be in range of, and set point in range of choice
    #     xNew = np.random.uniform(-DRONE2DRONE_SIGNAL_RANGE,DRONE2DRONE_SIGNAL_RANGE)
    #     xNew = min(max(xNew, lowXbound), highXbound) 
    #     ySpread = np.sqrt(DRONE2DRONE_SIGNAL_RANGE**2 - xNew**2)
    #     yNew = np.random.uniform(-ySpread, ySpread)
    #     yNew = min(max(yNew, lowYbound), highYbound) 
    #     kid[1].add((xNew, yNew))
        
    return kid
   

'''
Given a set of kids, kill them off until only the fittest survive
(call with lambda as fitnessFunc specifying arguments)
'''
def cull(kids, batchSize, fitnessFunc, runNum, totalRuns):
    # Direct Selection? -                                       best
    kids.sort(reverse = True, key = fitnessFunc)                
    return kids[:batchSize]     # If the literature says to, make this a probabilistic approach
    
    # Roulette Wheel Selection -                                worst
    # children = list(kids)
    # return random.choices(children, weights = [(fitnessFunc(child) - 1500)**2 for child in children], k=batchSize)

    # Rank Selection                                            second best, but still bad
    # kids.sort(reverse = True, key = fitnessFunc)
    # return random.choices(kids, weights = [len(kids) - i for i in range(len(kids))], k=batchSize)

    # Direct Selection + random -                               bad, somehow
    # kids.sort(reverse = True, key = fitnessFunc)
    # a = kids[:batchSize - batchSize//10]
    # b = [] + kids
    # for k in a:
    #     b.remove(k)
    # b = random.choices(b, k = batchSize//10)
    # return a + b

    # Boltzmann Selection -                                     pretty bad, but not terrible - maybe robust on large run sizes?                               
    # temp = 1 - 0.8 * runNum/float(totalRuns)   
    # scale = 3
    # adjustfit = lambda fit: scale * float(fitnessFunc(fit) - 1500)/fireCount
    # return random.choices(kids, weights=[e**(adjustfit(kid)/temp) for kid in kids], k = batchSize)

'''
Given gen n, generate gen n+1
Note that the parents can survive into the next generation if they are good. - massive improvement to performance 
'''
def kids_and_cull(gen, culledBatchSize, unculledBatchSize, pointSupp, runNum, totalRuns):
    kids = [] + gen
    babiesPer = int(unculledBatchSize/1 + len(gen[1]))
    for parent in gen:
        for i in range(babiesPer):
            kids.append(spawn_kid(parent, pointSupp))
    return cull(kids, culledBatchSize, lambda kid: fitness(kid, pointSupp), runNum, totalRuns)



'''
Inputs:
    droneCount - number of drones available
    fireCoords - list of coords of fires as tuples
    culledbatchSize - number of individual in ea generation after culling
    generations - number of generations to generate
    lowXbound - lower bound on drone x coordinate
    highXbound - upper bound on drone x coordinate
    lowYbound - lower bound on drone y coordinate
    highYbound - upper bound on drone y coordinate
'''
def runGA(droneCount, fireCoordsRaw, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    pointSupp = PointMaster(BOX_SIZE, lowXbound, highXbound, lowYbound, highYbound, fireCoordsRaw)
    
    # Set initial generation
    gen = intialize_parents(droneCount, culledBatchSize, unculledBatchSize, pointSupp)

    if gen == None:
        return None
    # Mutate, cull, and repeat
    for i in range(generations):
        gen = kids_and_cull(gen, culledBatchSize, unculledBatchSize, pointSupp, i + 1, generations)

    return(best_survivor(gen, pointSupp))

'''
Runs the GA but gives data on the best of every generation
'''
def runGA_output_all_gens(droneCount, fireCoordsRaw, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    pointSupp = PointMaster(BOX_SIZE, lowXbound, highXbound, lowYbound, highYbound, fireCoordsRaw)
    
    bests = []
    # Set initial generation
    gen = intialize_parents(droneCount, culledBatchSize, unculledBatchSize, pointSupp)
    if gen == None:
        return None
    bests.append(best_survivor(gen, pointSupp))

    # Mutate, cull, and repeat
    for i in range(generations):
        gen = kids_and_cull(gen, culledBatchSize, unculledBatchSize, pointSupp, i + 1, generations)
        bests.append(best_survivor(gen, pointSupp))

    return(bests)


'''
Takes in consumer for generation output.
The intention is that the consumer writes to a file.
This way, if not everything runs, we at least have some generation data.
'''
def runGA_iter_on_gen(droneCount, fireCoordsRaw, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound, iterationFunc):
    pointSupp = PointMaster(BOX_SIZE, lowXbound, highXbound, lowYbound, highYbound, fireCoordsRaw)
    
    bests = []
    # Set initial generation
    gen = intialize_parents(droneCount, culledBatchSize, unculledBatchSize, pointSupp)
    if gen == None:
        return None
    bests.append(best_survivor(gen, pointSupp))
    iterationFunc(bests[-1])

    # Mutate, cull, and repeat
    for i in range(generations):
        gen = kids_and_cull(gen, culledBatchSize, unculledBatchSize, pointSupp, i + 1, generations)
        bests.append(best_survivor(gen, pointSupp))    
        iterationFunc(bests[-1])

    return(bests)


# print(runGA_output_all_gens(3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 10, 20, 3, -10, 10, 0, 40))