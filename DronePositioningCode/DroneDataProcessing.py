import pandas
import DroneValidation as dv
import os, sys
import multiprocessing as mp

'''
The goal of this file is to provide the necessary results on Bohan's data.
1) Read clusters and choose what to run
2) Run each cluster, and write to output file
'''
EOC_FROM_FIRE = 20                                                               # Note that there are 2 such variables in this folder, so when you change one you should change the other
BOHAN_CSV_FILENAME = '../Data/fire_data_for_drones.csv'
# Bohan file preprocessing
df = pandas.read_csv(BOHAN_CSV_FILENAME,  converters={'fires_cart': eval})

def find_bounding_box(fireCoords):
    (lowXbound, highXbound, lowYbound, highYbound) = (fireCoords[0][0],fireCoords[0][0],fireCoords[0][1],fireCoords[0][1])
    for fire in fireCoords:
        if fire[0] > highXbound:
            highXbound = fire[0]
        elif fire[0] < lowXbound:
            lowXbound = fire[0]
        if fire[1] > highYbound:
            highYbound = fire[1]
        elif fire[1] < lowYbound:
            lowYbound = fire[1]
    lowXbound -= 1.1 * EOC_FROM_FIRE
    lowYbound -= 1.1 * EOC_FROM_FIRE
    highXbound += 1.1 * EOC_FROM_FIRE
    highYbound += 1.1 * EOC_FROM_FIRE
    return (lowXbound, highXbound, lowYbound, highYbound)

'''
Given a cluster, a number of drones to try, and the other necessary data, writes out the distribution data to 'filename_prefix_drone_distrubitions.txt'
'''
def run_cluster_with_dc(filename_prefix, n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound):
    results = dv.distribution_by_runs(n, droneCount, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)
    writeFile = open(filename_prefix + '_drone_distribution.txt','a')
    for result in results:
        writeFile.write(str(result) + '\n')
    writeFile.close()

'''
Given fire coords and a folder path name, creates a folder to store the cluster run and runs the GA on at most 75 drone counts  
'''
def run_cluster(folder_name, n, fireCoords, culledBatchSize, unculledBatchSize, generations):
    os.mkdir(folder_name)
    # Worst case we should only need < 81 drone positions - 90km max radius, model drone positions as 10km tangent spheres, loose upper bound
    # Note that because of correction factor (2 drones per location) this should be 162 actual drones
    processes = []
    fireNum = len(fireCoords)
    cap = min(150, 2 * fireNum)         # We won't need more than twice as many positions than we have fires, probably
    (lowXbound, highXbound, lowYbound, highYbound) = find_bounding_box(fireCoords)
    # Spawn processes for each number of drones
    for dc in range(2, cap, 2):
        process = mp.Process(target= run_cluster_with_dc, args = (folder_name + '/' + str(dc) + '_drones', n, dc, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound))
        processes.append(process)
        processes[-1].start()
        # run_cluster_with_dc(folder_name + '/' + str(dc) + '_drones', n, dc, fireCoords, culledBatchSize, unculledBatchSize, generations, lowXbound, highXbound, lowYbound, highYbound)
    # Let all processes join. I'm not sure this is strictly necessary, but it doesn't hurt.
    for p in processes:
        p.join()
        
'''
Reads a cluster off the csv and returns (cluster row number, fireCoords, date)
'''
def read_cluster(row):
    return (row, df.at[row,'fires_cart'], df.at[row, 'acq_date'])


def main():
    if len(sys.argv) != 2:
        print('cli input error', len(sys.argv))
        return 1

    # Set parameters for runs 
    n = 3
    culledBatchSize = 10
    unculledBatchSize = 20
    generations = 25

    row = int(sys.argv[1])

    fireCoords = read_cluster(row)[1]
    run_cluster('./1st_attempt_drone_position_GA_cluster_' + str(row), n, fireCoords, culledBatchSize, unculledBatchSize, generations)


'''
A function that will put the number of the rows that need to get run into a file.
For now we are optimistic, so we only discard fires with a single point.
'''
def choose_rows():
    writeFile = open('use_these_rows.txt','a')
    for i in range(df.shape[0]):
        if len(df.at[i,'fires_cart']) > 1:
            writeFile.write(str(i) + '\n')
    
if __name__ == '__main__':
    main()