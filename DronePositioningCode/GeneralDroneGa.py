import numpy as np
import random

'''
Restrictions/Requirements:
. If fire > 90km, that's trash. Drones can't make it more than 90km past EOC without having to turn around and refuel.
. There needs to be a place to put the eoc so that it is farther than EOC_FROM_FIRE from every fire.
. 
'''



EOC_FROM_FIRE = 0                          # Minimum distance EOC needs to be from an active fire point
RECHARGE_TIME = 1.75                        # Time it takes dronesto recharge
DRONE_SPEED = 1.2 * 60                           # km/hr
BATTERY_LIFE = 2.5                          # Hours before recharge required
DRONE_SIGNAL_RANGE = 20                     # Drone signal range (km)

def euclidean_dist(a,b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

'''
Computes "drone hours per hour" of potential drone position
'''
def dc_val(drone, eoc):
    flightTime = euclidean_dist(eoc,drone)/DRONE_SPEED
    return (BATTERY_LIFE + RECHARGE_TIME)/(BATTERY_LIFE - 2*flightTime)

'''
Shitty fitness function for drone placement
Reevaluate later based on literature for smoother measures and better counting
'''
def fitness(proposal, droneCount, fireCoords):
    eoc = proposal[0]
    # Punish if EOC in fire                 -  Not necessary based on how kids are being made
    layer0 = 1000
    for fire in fireCoords:
        if euclidean_dist(fire, eoc) < EOC_FROM_FIRE:
            layer0 = 0
            break

    # Punish if exceed drone count
    layer1 = 100
    dc = 0
    for drone in proposal[1]:
        dc += dc_val(drone, eoc)
    if dc > droneCount:                     # May want to make this a continuous/smooth function later haha analysis is useful
        layer1 = 0

    # Reward by fire coverage
    layer2 = 0
    # Get drones in range of EOC
    inrange = {eoc}
    changed = True
    while changed:
        changed = False
        for drone in (proposal[1] - inrange):
            adders = set()
            for node in inrange:
                if euclidean_dist(node, drone) <= DRONE_SIGNAL_RANGE:
                    adders.add(drone)
                    changed = True
            inrange = inrange | adders                  # Union
    # Count fires in range of EOC
    for fire in fireCoords:
        for drone in inrange:
            if euclidean_dist(fire, drone) < DRONE_SIGNAL_RANGE:
                layer2 += 1                 # Could weight this by brightness or other fire-importance metric
                break

    return layer0 + layer1 + layer2

'''
Make one gen0 proposal
'''
def intialize_parent(droneCount, fireCoords, lowXbound, highXbound, lowYbound, highYbound):
    # Assume there is a safe place to put EOC - fix later if necessary
    EOCSafe = False
    while not EOCSafe:
        EOCSafe = True
        eoc = (np.random.uniform(lowXbound,highXbound),np.random.uniform(lowXbound,highXbound))
        for fire in fireCoords:
            if euclidean_dist(fire, eoc) < EOC_FROM_FIRE:
                EOCSafe = False
                break
    
    # Pick points in range of current setup until cannot add drones
    network = {eoc}
    drones = set()
    dc = 0
    while dc < droneCount:                                      # Unnecessary condition here, but feels nice
        node = random.choice(tuple(network))                    # Choose node to be in range of, and set point in range of choice
        xNew = np.random.uniform(-DRONE_SIGNAL_RANGE,DRONE_SIGNAL_RANGE)
        xNew = min(max(xNew, lowXbound), highXbound) 
        ySpread = np.sqrt(DRONE_SIGNAL_RANGE**2 - xNew**2)
        yNew = np.random.uniform(-ySpread, ySpread)
        yNew = min(max(yNew, lowYbound), highYbound) 
        
        drone = (xNew, yNew)                                    # If we can afford the drone, add it. Else, don't.
        if dc_val(drone, eoc) > 0:
            dc += dc_val(drone, eoc)
            # print(dc, droneCount)
            if dc < droneCount:
                network.add(drone)
                drones.add(drone)

    return (eoc, drones)
    

'''
Make all gen0 proposals that will later be evolved over time
'''
def intialize_parents(droneCount, fireCoords, batchSize, lowXbound, highXbound, lowYbound, highYbound):
    # Assume there is a safe place to put EOC - fix later if necessary
    return [intialize_parent(droneCount, fireCoords, lowXbound, highXbound, lowYbound, highYbound) for i in range(batchSize)]

'''
Make kid off of 1 proposal
'''    
def spawn_kid(parent, fireCoords, lowXbound, highXbound, lowYbound, highYbound):
    kid = [parent[0],set()]
    
    # Try to move EOC randomly, only allow if safe distance from fire
    displacement = (np.random.uniform(-1.0,1.0), np.random.uniform(-1.0,1.0))
    newEOC = np.add(parent[0],displacement)
    newEOC = (min(max(newEOC[0], lowXbound), highXbound), min(max(newEOC[1], lowYbound), highYbound))
    safeEOC = True
    for fire in fireCoords:
        if euclidean_dist(fire, newEOC) < EOC_FROM_FIRE:
            safeEOC = False
    if safeEOC:
        kid[0] = newEOC

    # Move the drones randomly
    for drone in parent[1]:
        # Small chance of killing drone (1%)
        if np.random.uniform(0,100) < 99:
            displacement = (np.random.uniform(-1.0,1.0), np.random.uniform(-1.0,1.0))
            newDrone = np.add(drone,displacement)
            newDrone = (min(max(newDrone[0], lowXbound), highXbound), min(max(newDrone[1], lowYbound), highYbound))
            kid[1].add(newDrone)

    # Small chance of spawning drone (1%)
    if np.random.uniform(0,100) > 99:
        node = random.choice(tuple([parent[0]] + list(parent[1])))                    # Choose node to be in range of, and set point in range of choice
        xNew = np.random.uniform(-DRONE_SIGNAL_RANGE,DRONE_SIGNAL_RANGE)
        xNew = min(max(xNew, lowXbound), highXbound) 
        ySpread = np.sqrt(DRONE_SIGNAL_RANGE**2 - xNew**2)
        yNew = np.random.uniform(-ySpread, ySpread)
        yNew = min(max(yNew, lowYbound), highYbound) 
        kid[1].add((xNew, yNew))
        
    return kid
   

'''
Given a set of kids, kill them off until only the fittest survive
(call with lambda as fitnessFunc specifying arguments)
'''
def cull(kids, batchSize, fitnessFunc):
    kids.sort(reverse = True, key = fitnessFunc)
    return kids[:batchSize]     # If the literature says to, make this a probabilistic approach

'''
Given gen n, generate gen n+1
'''
def kids_and_cull(gen, droneCount, fireCoords, culledBatchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound):
    kids = []
    babiesPer = int(unculledBatchSize/1 + len(gen[1]))
    for parent in gen:
        for i in range(babiesPer):
            kids.append(spawn_kid(parent, fireCoords, lowXbound, highXbound, lowYbound, highYbound))
    return cull(kids, culledBatchSize, lambda kid: fitness(kid, droneCount, fireCoords))



'''
Inputs:
    droneCount - number of drones available
    fireCoords - list of coords of fires as tuples
    batchSize - number of individual in ea generation
    generations - number of generations to generate
    lowXbound - lower bound on drone x coordinate
    highXbound - upper bound on drone x coordinate
    lowYbound - lower bound on drone y coordinate
    highYbound - upper bound on drone y coordinate
'''
def main(droneCount, fireCoords, batchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    # Set initial generation
    gen = intialize_parents(droneCount, fireCoords, batchSize, lowXbound, highXbound, lowYbound, highYbound)

    # Mutate, cull, and repeat
    for i in range(generations):
        gen = kids_and_cull(gen, droneCount, fireCoords, batchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound)

    # Choose best survivor
    fit = 0
    best = None
    for survivor in gen:
        if fitness(survivor, droneCount, fireCoords) > fit:
            fit = fitness(survivor, droneCount, fireCoords)
            best = survivor
    print(survivor, fitness(survivor, droneCount, fireCoords), sum([dc_val(drone, survivor[0]) for drone in survivor[1]]))




main(3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 10, 20, 3, -10, 10, 0, 40)