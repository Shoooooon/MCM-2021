import numpy
import random

EOC_FROM_FIRE = 10                          # Minimum distance EOC needs to be from an active fire point
RECHARGE_TIME = 1.75                        # Time it takes dronesto recharge
DRONE_SPEED = 1.2                           # km/hr
BATTERY_LIFE = 2.5                          # Hours before recharge required
DRONE_SIGNAL_RANGE = 20                     # Drone signal range (km)

'''
Computes "drone hours per hour" of potential drone position
'''
def dc_val(drone, eoc):
    flightTime = np.distance(eoc,drone)/DRONE_SPEED
    return (BATTERY_LIFE + RECHARGE_TIME)/(BATTERY_LIFE - 2*flightTime)

'''
Shitty fitness function for drone placement
Reevaluate later based on literature for smoother measures and better counting
'''
def fitness(gen, droneCount, fireCoords):
    # Punish if EOC in fire
    layer0 = 1000
    for fire in fireCoords:
        if np.distance(fire, gen[0]) < EOC_FROM_FIRE:
            layer0 = 0
            break

    # Punish if exceed drone count
    layer1 = 100
    dc = 0
    for drone in gen[1]:
        dc += dcVal(drone, eoc)
    if dc > droneCount:                     # May want to make this a continuous/smooth function later haha analysis is useful
        layer1 = 0

    # Reward by fire coverage
    layer2 = 0
    # Get drones in range of EOC
    inrange = {gen[0]}
    changed = True
    while changed:
        changed = False
        for drone in gen[1]:
            for node in inrange:
                if np.distance(node, drone) <= DRONE_SIGNAL_RANGE:
                    inrange.add(drone)
                    changed = True
    # Count fires in range of EOC
    for fire in fireCoords:
        for drone in inrange:
            if np.distance(fire, drone) < DRONE_SIGNAL_RANGE:
                layer2 += 1                 # Could weight this by brightness or other fire-importance metric
                break

    return layer0 + layer1 + layer2


def intialize_parents(droneCount, fireCoords, batchSize, lowXbound, highXbound, lowYbound, highYbound):
    # Assume there is a safe place to put EOC - fix later if necessary
    EOCSafe = False
    while not EOCSafe:
        EOCSafe = True
        eoc = (random.randrange(lowXbound,highXbound),random.randrange(lowXbound,highXbound))
        for fire in fireCoords:
            if np.distance(fire, eoc) < EOC_FROM_FIRE:
                EOCSafe = False
                break
    
    # Pick points in range of current setup until cannot add drones
    network = {eoc}
    drones = {}
    dc = 0
    while dc < droneCount:                                      # Unnecessary condition here, but feels nice
        node = random.choice(tuple(network))                    # Choose node to be in range of, and set point in range of choice
        xNew = random.randrange(-DRONE_SIGNAL_RANGE,DRONE_SIGNAL_RANGE)
        xNew = min(max(xNew, lowXbound), highXbound) 
        ySpread = np.sqrt(DRONE_SIGNAL_RANGE^2 - xNew^2)
        yNew = random.randrange(-ySpread, ySpread)
        yNew = min(max(yNew, lowYbound), highYbound) 
        
        drone = (xNew, yNew)                                    # If we can afford the drone, add it. Else, don't.
        dc += dc_val(drone, eoc)
        if dc < droneCount:
            network.add(drone)
            drones.add(drone)

    return (eoc, drones)
        





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
def main(droneCount, fireCoords, batchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    # Set initial generation
    gen = intialize_parents(droneCount, fireCoords, batchSize, lowXbound, highXbound, lowYbound, highYbound)

    for i in range(generations):
        gen = kids_and_cull(gen, droneCount, fireCoords, batchSize, lowXbound, highXbound, lowYbound, highYbound)

    print(gen, fitness(gen, droneCount, fireCoords), droneCount(gen))