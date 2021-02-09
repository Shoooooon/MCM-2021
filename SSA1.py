#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 15:55:14 2021

@author: kevinzheng
"""

from collections import namedtuple  
import matplotlib.pyplot as plt  
import random
import math
import numpy as np


Point = namedtuple('Point', 'x y')


class Cluster(object):  
    """
    use gift wrapping algorithm to find the fire edge of a cluster of fires
    """
    _points = []
    _hull_points = []
    _edges = []
    _area = None

    def __init__(self):
        pass

    def add(self, point):
        self._points.append(point)
        
    def get_points(self):
        return self._points

    def _get_orientation(self, origin, p1, p2):
        """
        Returns the orientation of the Point p1 with regards to Point p2 using origin.
        """
        difference = (
            ((p2.x - origin.x) * (p1.y - origin.y))
            - ((p1.x - origin.x) * (p2.y - origin.y))
        )

        return difference

    def compute_hull(self):
        """
        Computes the points that make up the convex hull.
        """
        points = self._points

        # get leftmost point
        start = points[0]
        min_x = start.x
        for p in points[1:]:
            if p.x < min_x:
                min_x = p.x
                start = p

        point = start
        self._hull_points.append(start)

        far_point = None
        while far_point is not start:

            # get the first point (initial max) to use to compare with others
            p1 = None
            for p in points:
                if p is point:
                    continue
                else:
                    p1 = p
                    break

            far_point = p1

            for p2 in points:
                # ensure we aren't comparing to self or pivot point
                if p2 is point or p2 is p1:
                    continue
                else:
                    direction = self._get_orientation(point, far_point, p2)
                    if direction > 0:
                        far_point = p2

            self._hull_points.append(far_point)
            point = far_point

    def get_hull_points(self):
        if self._points and not self._hull_points:
            self.compute_hull()

        return self._hull_points
    
    def get_edges(self):
        """
        return a list of list. Each sublist is made up with two tuples. The second tuple contains the 
        coords of the two endpoints of that edge, and the first corresponds to the perpendicular unit vector
        that is pointing outward the cluster

        """
        num_edges = len(self._hull_points)
        for i in range(-1, num_edges-1):
            edge = (self._hull_points[i], self._hull_points[i+1])
            deltay = edge[1][1] - edge[0][1]
            deltax = edge[1][0] - edge[0][1]
            dist = np.sqrt(deltay ** 2 + deltax ** 2)
            unit_out = (deltay/dist, -deltax/dist)
            edge_obj = [unit_out, edge]
            self._edges.append(edge_obj)
        return self._edges
    
    def get_area(self):
        a = 0
        x0, y0 = self._hull_points[0]
        for x, y in self._hull_points[1:]:
            a += (x*y0 - y*x0)
            x0, y0 = x, y
        self._area = -a/2
        return self._area
    
    
    def display(self):
        """
        plot the cluster and the boundary founded

        """
        # all points
        x = [p.x for p in self._points]
        y = [p.y for p in self._points]
        plt.plot(x, y, marker='D', linestyle='None')

        # hull points
        hx = [p.x for p in self._hull_points]
        hy = [p.y for p in self._hull_points]
        plt.plot(hx, hy)
        plt.xlabel("x/km")
        plt.ylabel("y/km")

        plt.title('The boundary of a cluster of fires from gift wrapping algorithm (orange line)')
        plt.show()
        
        
        
        
        
        
        
#Topography = np.#a 2d array of altitude
#Vegetation = #a 2d array reflecting burnabilty, described as either true or false, meaning there is or is not sufficient feul for fire to spread
Array_step = 0.1
#suppose in our array, the step is 0.1km, i.e., what distance in reality one step represents
Fuel_check = 10
#the length of the side of a square center at the point in check in km. If less than 1/5 of the area has fuel,
#no drone will be deployed there
R = 30 #diameter of range of SSA drones

def grad(topo):
    """
    calculate the gradient field

    """
    gravec = np.gradient(topo)
    return gravec




def dot_product(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]


def find_pt(edge, vec, stepbd=0.1):
    """
    egde: a list of two tuples specifying a segment
    step: the upperbound of a step between the two breaking points
    
    returns a list of tuples specifying the step points on the segment and unit vector in the thrid field
    """
    p1x = edge[0][0]
    p1y = edge[0][1]
    p2x = edge[1][0]
    p2y = edge[1][1]
    lst = []
    if p1x == p2x:
        length = p2y - p1y
        numstep = int(np.ceil(length/stepbd))#obtain the number of steps
        if numstep == 0:
            return []
        step = length/numstep
        for i in range(numstep):
            lst.append((p1x, p1y+i*step, vec))
    else:
        slope = (p2y-p1y)/(p2x-p1x)
        b = p1y - slope*p1x
        length = np.sqrt(slope**2 + 1)*np.abs(p2x-p1x)
        numstep = int(np.ceil(length/stepbd)) #obtain the number of steps
        step = length/numstep
        stepx = (p2x-p1x)/numstep
        for i in range(numstep):
            xi = p1x+i*stepx
            lst.append((xi, slope*xi+b, vec))
    return lst


def find_grad(p, grad):
    """
    find the gradient of an arbitrary point by approximating it with arrays of gradient
    p: a point
    grad: the gradient field array
    """
    px = p[0]/Array_step
    py = p[1]/Array_step
    ceilx = int(np.ceil(px))
    florx = int(np.floor(px))
    ceily = int(np.ceil(py))
    flory = int(np.floor(py))
    grad1 = (grad[0][ceilx][ceily],grad[1][ceilx][ceily])
    grad2 = (grad[0][ceilx][flory],grad[1][ceilx][flory])
    grad3 = (grad[0][florx][flory],grad[1][florx][flory])
    grad4 = (grad[0][florx][ceily],grad[1][florx][ceily])
    gradient = ((grad1[0]+grad2[0]+grad3[0]+grad4[0])/4, (grad1[1]+grad2[1]+grad3[1]+grad4[1])/4)
    return gradient

# use N*tanh(A del altitude * vec) to model the alert level if spreading in that direction

def find_rho(p):
    """
    find the drone density needed at a point
    #grad: a tuple representing the gradient at the point
    vec: the unit vector pointing outward the cluster
    #vege: the vegetation array (true/false). we want to check the vegetation in the square with 
    side length centered at
    the point 
    """
    vec = p[2]
    rho = None
    #grad_field = grad(Topography)
    gradp = find_grad(p, grad_field)
    #print(gradp)
    crit = N*np.tanh(dot_product(gradp,vec))
    #print("This is crit", crit)
    #first check by altitude gradient(the topography)
    if -1 <= crit <= 0:
        rho = 0.5
    elif 0 < crit <= 0.5:
        rho = 1
    else:
        rho = 2
    px = p[0]/Array_step
    py = p[1]/Array_step
    ceilx = int(np.ceil(px))
    ceily = int(np.ceil(py))
    idx = int(Fuel_check/2/Array_step)
    idx2 = 4*idx**2
    temp_array = Vegetation[ceilx-idx:ceilx+idx, ceily-idx:ceily+idx]
    temp = np.sum(temp_array)
    #print(temp)
    #second check by fuel(vegetation)
    if temp < 0.2*idx2:
        rho = 0
    elif 0.2 <= temp <= 0.5:
        rho = 0.5*rho
    else:
        rho = 1*rho
    return rho

def find_rho2(p):
    """
    find the drone density needed at a point
    #grad: a tuple representing the gradient at the point
    vec: the unit vector pointing outward the cluster
    #vege: the vegetation array (true/false). we want to check the vegetation in the square with 
    side length centered at
    the point 
    """
    vec = p[2]
    rho = None
    #grad_field = grad(Topography)
    gradp = find_grad(p, grad_field)
    #print(gradp)
    rho = np.tanh(5*dot_product(gradp,vec))+1
    #print("This is crit", crit)
    #first check by altitude gradient(the topography)
    px = p[0]/Array_step
    py = p[1]/Array_step
    ceilx = int(np.ceil(px))
    ceily = int(np.ceil(py))
    idx = int(Fuel_check/2/Array_step)
    idx2 = 4*idx**2
    temp_array = Vegetation[ceilx-idx:ceilx+idx, ceily-idx:ceily+idx]
    temp = np.sum(temp_array)
    #print(temp)
    #second check by fuel(vegetation)
    rho = temp/idx2 * rho
    return rho


def assign_SSA(lst):
    """
    the input will be a list of drone densities at equispaced points along the fire edge. 
    returns the total number of SSA drones needed
    """
    check = R/Array_step
    num = 0 #number of SSA drones needed
    keep = 0
    check_keep = 0
    for i in lst:
        if check_keep == check:
            if keep > 0.625 * 2 * check:
                num += 2
            elif 0.125 * 2 * check < keep <= 0.625 * 2 * check:
                num += 1
            else:
                num += 0
            keep = 0
            check_keep = 0
        else:
            keep += i
            check_keep += 1
    return num


def assign_SSA2(lst):
    """
    the input will be a list of drone densities at equispaced points along the fire edge. 
    returns the total number of SSA drones needed
    """
    check = R/Array_step
    num = 0 #number of SSA drones needed
    keep = 0
    check_keep = 0
    for i in lst:
        if check_keep == check:
            if keep > 0.8 * 2 * check:
                num += 2
            elif 0.2 * 2 * check < keep <= 0.8 * 2 * check:
                num += 1
            else:
                num += 0
            keep = 0
            check_keep = 0
        else:
            keep += i
            check_keep += 1
    return num
        
    







#BOHAN_CSV_FILENAME = './Data/fire_data_for_drones.csv'
#df = pd.read_csv(BOHAN_CSV_FILENAME,  converters={'fires_cart': eval})
#number_of_clusters = df.shape[0]

def read_cluster(row):
    '''
    Reads a cluster off the csv and returns (cluster row number, fireCoords, date)
    '''
    return (row, df.at[row,'fires_cart'], df.at[row, 'acq_date'])


# The following is the test
Topography = np.zeros((5000,5000)) #set a grid with 500 km side
Vegetation = np.ones((5000,5000), dtype=int) #
# forest and savanna ------ 1
# mountain vegetaion ------ 0
# major river -------- -1
#Temparature =
#Humidity = 
N = 1
if_temparature = False
if_humidity = False

#print(grad(Topography))

#mycluster = read_cluster(1)
#print(mycluster, 'this is cluster')
ch = Cluster()
#for (i,j) in mycluster:
    #ch.add(Point(i,j))

for _ in range(20000):
    ch.add(Point(500*random.uniform(0.25,0.5), 500*random.uniform(0.25,0.4))) # set cluster
"""
for _ in range(10000):
    ch.add(Point(500*random.uniform(0.4,0.75), 500*random.uniform(0.5,0.75)))

for _ in range(15000):
    ch.add(Point(400*random.uniform(0.3,0.65), 400*random.uniform(0.2,0.7)))
for _ in range(10000):
    ch.add(Point(500*random.uniform(0.4,0.3), 500*random.uniform(0.3,0.7)))
"""
for _ in range(10000):
    ch.add(Point(400*random.uniform(0.2,0.4), 500*random.uniform(0.3,0.55)))


my_lst = [(-26.907016076747677, -33.898694783273385), (-22.508703595430795, -28.332413068723785), (-28.055234256851893, -35.353452077360345), (-27.80696980844345, -35.03885130613091), (-23.233814780790958, -29.249396417184602), (-25.98466835684022, -32.73059801280237), (-25.79090504835786, -32.4852640674714), (-25.680617355702683, 
-32.34563158736822), (-25.192758011394194, -31.72803979977314), (-22.590598949271172, -28.435965367299627), (-22.76273960153767, -28.653639178980082), (-13.321188604650128, -16.736941560881416), (-13.376674499776225, -16.80684138056677), (-13.07647492668314, -16.42867559967247), (-12.96513916978934, -16.28843588980152), (-13.02063107624823, -16.35833330632231), (-12.420845376485154, -15.602927665149924), (-20.006163599367646, -25.16973324104269), (-13.541538825155902, -17.014542736164774), (-20.133369760062106, -25.33041791661425), (-19.82375275092328, -24.939329301377764), (-12.596875028296207, -15.8246110146866), (-12.651402603119445, -15.893283614008483), (-2.9059668717364513, -3.6435239860869584), (-12.291574495200038, -15.440140037242475), (-10.375034633678752, -13.0276769943689), (-9.958090573227368, -12.503089644741292), (-10.013633179016704, -12.572966746373996), (-9.707386634215744, -12.18770307537135), (-8.408525459401643, -10.554236464007527), (-8.46312236101287, -10.622881248085864), (3.085902676781361, 3.8645277895156553), (-8.102836822126696, -10.169921239758818), (0.6857373586711298, 0.8591694476983129), (0.9874799624619864, 1.2371526599726625), (-2.4745402717647242, -3.102331749969159), (-1.451725096389027, -1.8196580746215465), (6.704998914267904, 8.390765439667566), (7.005331619409322, 8.766086613292234), (6.949771596011853, 8.696657463684316), (-2.927912821070861, -3.6710560131841503), (-3.0389677222004177, -3.8103822928015827), (-3.0953344079449256, -3.8811006690600864), (-3.982651871578633, -4.994549830849922), (-2.6780921033008167, -3.3576606433939786), (-3.676554565983515, -4.610399579466219), (5.319591602869544, 6.658865973255981), (-3.4251090302274982, -4.294871993751356), (-3.4797881093340344, -4.363483599647079), (-2.643666168868026, -3.314476401617965), (-2.7003935467047016, -3.385636116233206), (7.597200477252118, 9.505605638735947), (7.542340825383889, 9.437067733559767), (7.898589440905842, 9.882113943585138), (8.254875775565548, 10.327144636410337), (-5.431011649414054, -6.812867888504825), (-5.0296274403666, -6.308851945906236), (16.171407998633924, 20.199429765777253), (16.114718108887672, 20.12884410504486), (8.490615472724379, 10.621568322696636), (8.433343858924518, 10.55004228929958), (15.279341707626424, 19.08851874286873), (9.216584284607483, 11.52808444993854), (9.579760586842609, 11.981484663010253), (9.520516391508366, 11.907526864047254), (9.82376526974092, 12.286070953490041), (9.883014793564964, 12.360026555038152), (9.652951255186329, 12.072850226720067), (18.492589418662362, 23.08822822324007), (11.795103131302659, 14.745778943431539), (11.743908077120084, 14.681925233803607), (18.90271988531297, 23.59837771681344), (19.15033612487589, 23.906340720627945), (19.09635781358843, 23.83920985747048), (26.932217342096894, 33.56955940299305), (24.413398492419795, 30.445010891644458), (26.538262267549808, 33.08106795875339), (27.254788849449277, 33.969481671662976), (27.197200518137805, 33.898087683753154), (26.97685593429909, 33.62490506764266), (27.556585333108817, 34.34360164682272), (27.499349112743435, 34.272652534654746), (28.217772894146847, 35.163084534661195), (28.518939318519443, 35.53628341748954), (28.582355535494404, 35.614861833550364)]


"""
for (i,j) in my_lst:
    ch.add(Point(i+100,j+100))
"""

"""
for _ in range(60):
    ch.add(Point(500*random.uniform(0.25,0.4), 500*random.uniform(0.25,0.35))) # set cluster
"""


    
print("Points on hull:", ch.get_hull_points())
print(ch.get_edges())
print(ch.get_area())
ch.display()


fire_spot = ch.get_points()
vec_lst = [] #list of unit vectors pointing outward
edge_lst = [] #list of edges specified by endpoints
edges = ch.get_edges()
num_edge = len(edges)
for i in range(num_edge):
    vec_lst.append(edges[i][0])
    edge_lst.append(edges[i][1])
    

point_lst = []
for idx in range(num_edge):
    temp = find_pt(edge_lst[idx], vec_lst[idx])
    point_lst.extend(temp) # note this elements in temp have the format (x,y, unit_vector)
    

grad_field = grad(Topography)



rho_lst = []
for i in point_lst:
    rho_lst.append(find_rho2(i))
    
    
length_rho_lst = len(rho_lst)
result_lst = []
for idx in range(length_rho_lst):
    new_lst = rho_lst[idx:]+rho_lst[0:idx]
    result_lst.append(assign_SSA2(new_lst))
result = min(result_lst)
print(result)
"""
result = assign_SSA(rho_lst)
print("Need SSA drones ", result)
#print(Vegetation)
print(rho_lst)
#print(len(rho_lst))
    
"""



    



