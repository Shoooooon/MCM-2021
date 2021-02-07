import numpy as np
import random
import matplotlib

'''
Restrictions/Requirements:
. If fire > 90km, that's trash. Drones can't make it more than 90km past EOC without having to turn around and refuel.
. There needs to be a place to put the eoc so that it is farther than EOC_FROM_FIRE from every fire.
. 
'''

### Changes:
# Drone signal range - drone2drone = 20, drone2fire = 5 --- adjust globals and fitness accordingly


EOC_FROM_FIRE = 20                          # Minimum distance EOC needs to be from an active fire point - Note that there are 2 such variables in this folder, so when you change one you should change both
RECHARGE_TIME = 1.75                        # Time it takes dronesto recharge
DRONE_SPEED = 1.2 * 60                      # km/hr
BATTERY_LIFE = 2.5                          # Hours before recharge required
DRONE2DRONE_SIGNAL_RANGE = 20               # Drone signal range to other drones (km)
DRONE2MAN_SIGNAL_RANGE = 5                  # Drone signal range to people and SSA drones (km)
e = 2.718281


'''
Helper Functions
'''

'''
Compute euclidean distance bet two 2-tuples
'''
def euclidean_dist(a,b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

'''
Computes "drone hours per hour" of potential drone position
We decided that the drones should be stationed permanently, at least in the extreme short-term, so we have 2 drones per position
'''
def dc_val(drone, eoc):
    # flightTime = euclidean_dist(eoc,drone)/DRONE_SPEED
    # flightTime = 0                                                          # Assuming firefighters set manually and are there to replace/recharge
    # return (BATTERY_LIFE + RECHARGE_TIME)/(BATTERY_LIFE - 2*flightTime)
    return 2

'''
Returns overall drone hours per hour of a proposal.
'''
def overall_dc_val(drones,eoc):
    # return sum([dc_val(drone,eoc) for drone in drones])
    return(2*len(drones))


'''
Gets best survivor from batch
'''
def best_survivor(gen, droneCount, fireCoords):
    # Choose best survivor
    fit = 0
    best = None
    for survivor in gen:
        if fitness(survivor, droneCount, fireCoords) > fit:
            fit = fitness(survivor, droneCount, fireCoords)
            best = survivor
    return(survivor, fitness(survivor, droneCount, fireCoords) - 1500, overall_dc_val(survivor[1], survivor[0]))





'''
Major functions
'''

'''
Direct fitness function for drone placement
Reevaluate later based on literature for smoother measures and better counting
It turns out we can't do better, so we'll stick with this.
Over enough time, we get convergence to good values anyway.
'''
def fitness(proposal, droneCount, fireCoords):
    eoc = proposal[0]
    # Punish if EOC in fire                             -  No longer necessary based on how kids are being made
    layer0 = 1000
    # for fire in fireCoords:
    #     if euclidean_dist(fire, eoc) < EOC_FROM_FIRE:
    #         layer0 = 0
    #         break

    # Punish if exceed drone count                      - No longer necessary since dc now fixed
    layer1 = 500
    # dc = 0
    # for drone in proposal[1]:
    #     dc += dc_val(drone, eoc)
    # if dc > droneCount:                     # May want to make this a continuous/smooth function later haha analysis is useful
    #     layer1 = 0

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
                if euclidean_dist(node, drone) <= DRONE2DRONE_SIGNAL_RANGE:
                    adders.add(drone)
                    changed = True
                    break
            inrange = inrange | adders                  # Union
    # Count fires in range of EOC
    for fire in fireCoords:
        for drone in inrange:
            if euclidean_dist(fire, drone) < DRONE2MAN_SIGNAL_RANGE:
                layer2 += 1                 # Could weight this by brightness or other fire-importance metric
                break

    return layer0 + layer1 + layer2

'''
Make one gen0 proposal
'''
def intialize_parent(droneCount, fireCoords, lowXbound, highXbound, lowYbound, highYbound):
    # Assume there is a safe place to put EOC - fix later if necessary
    EOCSafe = False
    trials = 10000
    while not EOCSafe and trials >=0:
        EOCSafe = True
        trials -= 1
        eoc = (np.random.uniform(lowXbound,highXbound),np.random.uniform(lowYbound,highYbound))
        for fire in fireCoords:
            if euclidean_dist(fire, eoc) < EOC_FROM_FIRE:
                EOCSafe = False
                break
    if trials <= 0:
        print('Could not get safe EOC.')
        return None
    
    # Pick points in range of current setup until cannot add drones
    network = {eoc}
    drones = set()
    dc = 0
    while dc < droneCount:                                      # Unnecessary condition here, but feels nice
        base = random.choice(tuple(network))                    # Choose node to be in range of, and set point in range of choice
        theta = np.random.uniform(0.0, 2*np.pi)
        r = np.random.uniform(0.5, 1)                           # Forces drones sort of kind of apart in first approximation since tightly clustered drones are useless
        xNew = r*DRONE2DRONE_SIGNAL_RANGE*np.cos(theta) + base[0]
        xNew = min(max(xNew, lowXbound), highXbound) 
        yNew = r*DRONE2DRONE_SIGNAL_RANGE*np.sin(theta) + base[1]
        yNew = min(max(yNew, lowYbound), highYbound) 
        drone = (xNew, yNew)                                    # If we can afford the drone, add it. Else, don't. Now, this is basically just counting drones.
        if dc_val(drone, eoc) > 0:
            dc += dc_val(drone, eoc)
            # print(dc, droneCount)
            if dc <= droneCount:
                network.add(drone)
                drones.add(drone)

    return (eoc, drones)
    

'''
Make all gen0 proposals that will later be evolved over time - done
'''
def intialize_parents(droneCount, fireCoords, culledBatchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound):
    # Assume there is a safe place to put EOC - fix later if necessary
    a = [intialize_parent(droneCount, fireCoords, lowXbound, highXbound, lowYbound, highYbound) for i in range(unculledBatchSize)]
    a = list(filter(lambda x: x != None, a))
    if len(a) < unculledBatchSize/2.0:
        return None
    return cull([intialize_parent(droneCount, fireCoords, lowXbound, highXbound, lowYbound, highYbound) for i in range(unculledBatchSize)], len(fireCoords), culledBatchSize, lambda kid: fitness(kid, droneCount, fireCoords), 0, 1)

'''
Make kid off of 1 proposal - done
'''    
def spawn_kid(parent, droneCount, fireCoords, lowXbound, highXbound, lowYbound, highYbound):
    kid = [parent[0],set()]
    
    # Try to move EOC randomly, only allow if safe distance from fire
    displacement = (np.random.uniform(-7.5, 7.5), np.random.uniform(-7.5, 7.5))
    newEOC = np.add(parent[0],displacement)
    newEOC = (min(max(newEOC[0], lowXbound), highXbound), min(max(newEOC[1], lowYbound), highYbound))
    safeEOC = True
    for fire in fireCoords:
        if euclidean_dist(fire, newEOC) < EOC_FROM_FIRE:
            safeEOC = False
    if safeEOC:
        kid[0] = newEOC

    # Move the drones randomly, by random degrees of extremeness.
    for drone in parent[1]:
        # Small chance of killing and replacing drone (2%) - In case high number of drones and we get a poorly seeded drone in an otherwise good candidate
        # On larger fire areas, I'm hoping this will be a useful Mulligan
        if np.random.uniform(0,100) < 98:
            displacement = (np.random.uniform(-10.0, 10.0), np.random.uniform(-10.0, 10.0))               # This makes a very big deal - it is good to be large
            newDrone = np.add(drone,displacement)
            newDrone = (min(max(newDrone[0], lowXbound), highXbound), min(max(newDrone[1], lowYbound), highYbound))
            kid[1].add(newDrone)
        else:
            bestScore = fitness(parent, droneCount, fireCoords)
            best = drone
            for i in range(15):
                copy = parent[1] - {drone}
                base = random.choice(tuple(parent[1]))                    # Choose node to be in range of, and set point in range of choice
                theta = np.random.uniform(0.0, 2*np.pi)
                r = np.random.uniform(0.9, 1)                           # Forces drones sort of kind of apart in first approximation since tightly clustered drones are useless
                xNew = r*DRONE2DRONE_SIGNAL_RANGE*np.cos(theta) + base[0]
                xNew = min(max(xNew, lowXbound), highXbound) 
                yNew = r*DRONE2DRONE_SIGNAL_RANGE*np.sin(theta) + base[1]
                yNew = min(max(yNew, lowYbound), highYbound) 
                newDrone = (xNew, yNew)                                    # If we can afford the drone, add it. Else, don't. Now, this is basically just counting drones.
                if fitness([parent[0],copy.union({newDrone})], droneCount, fireCoords) > bestScore:
                    bestScore = fitness([parent[0], copy.union({newDrone})], droneCount, fireCoords)
                    best = newDrone
            kid[1].add(best)


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
def cull(kids, fireCount, batchSize, fitnessFunc, runNum, totalRuns):
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
def kids_and_cull(gen, droneCount, fireCoords, culledBatchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound, runNum, totalRuns):
    kids = [] + gen
    babiesPer = int(unculledBatchSize/1 + len(gen[1]))
    for parent in gen:
        for i in range(babiesPer):
            kids.append(spawn_kid(parent, droneCount, fireCoords, lowXbound, highXbound, lowYbound, highYbound))
    return cull(kids, len(fireCoords), culledBatchSize, lambda kid: fitness(kid, droneCount, fireCoords), runNum, totalRuns)



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
def runGA(droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    # Set initial generation
    gen = intialize_parents(droneCount, fireCoords, culledBatchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound)

    if gen == None:
        return None
    # Mutate, cull, and repeat
    for i in range(generations):
        gen = kids_and_cull(gen, droneCount, fireCoords, culledBatchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound,i+1,generations)

    return(best_survivor(gen, droneCount, fireCoords))

'''
Runs the GA but gives data on the best of every generation
'''
def runGA_output_all_gens(droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    bests = []
    # Set initial generation
    gen = intialize_parents(droneCount, fireCoords, culledBatchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound)
    if gen == None:
        return None
    bests.append(best_survivor(gen, droneCount, fireCoords))

    # Mutate, cull, and repeat
    for i in range(generations):
        gen = kids_and_cull(gen, droneCount, fireCoords, culledBatchSize, unculledBatchSize, lowXbound, highXbound, lowYbound, highYbound,i+1,generations)
        bests.append(best_survivor(gen, droneCount, fireCoords))

    return(bests)



# runGA(3, [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)], 10, 20, 3, -10, 10, 0, 40)