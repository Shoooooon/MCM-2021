#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 20:43:55 2021

@author: kevinzheng
"""

import numpy as np
import find_boundary
from collections import namedtuple  
import matplotlib.pyplot as plt  
import random
import math

N = 100 #number of SSA drones available
Topography = np.#a 2d array of altitude
#Vegetation = #a 2d array reflecting burnabilty, described as either true or false, meaning there is or is not sufficient feul for fire to spread
Array_step = 0.1
#suppose in our array, the step is 0.1km, i.e., what distance in reality one step represents
Fuel_check = 10
#the length of the side of a square center at the point in check in km. If less than 1/5 of the area has fuel,
#no drone will be deployed there


def grad(topo):
    """
    calculate the gradient field

    """
    gravec = np.gradient(topo)
    return gravec




def dot_product(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]


def find_pt(edge, stepbd=1):
    """
    egde: a list of two tuples specifying a segment
    step: the upperbound of a step between the two breaking points
    
    returns a list of tuples specifying the step points on the segment
    """
    p1x = edge[0][0]
    p1y = edge[0][1]
    p2x = edge[1][0]
    p2y = edge[1][1]
    lst = []
    if p1x == p2x:
        length = p2y - p1y
        numstep = int(np.ceil(length/stepbd)) #obtain the number of steps
        step = length/numstep
        for i in range(numstep):
            lst.append((p1x, p1y+i*step))
    else:
        slope = (p2y-p1y)/(p2x-p1x)
        b = p1y - slope*p1x
        length = np.sqrt(slope**2 + 1)*np.abs(p2x-p1x)
        numstep = int(np.ceil(length/stepbd)) #obtain the number of steps
        step = length/numstep
        stepx = (p2x-p1x)/numstep
        for i in range(numstep):
            xi = p1x+i*stepx
            lst.append((xi, slope*xi+b))
    return lst


def find_grad(p, grad):
    """
    find the gradient of an arbitrary point by approximating it with arrays of gradient
    p: a point
    grad: the gradient field array
    """
    px = p[0]/Array_step
    py = p[1]/Array_step
    ceilx = np.ceil(px)
    florx = np.floor(px)
    ceily = np.ceil(py)
    flory = np.floor(py)
    grad1 = (grad[0][ceilx],grad[1][ceily])
    grad2 = (grad[0][ceilx],grad[1][flory])
    grad3 = (grad[0][florx],grad[1][flory])
    grad4 = (grad[0][florx],grad[1][ceily])
    gradient = ((grad1[0]+grad2[0]+grad3[0]+grad4[0])/4, (grad1[1]+grad2[1]+grad3[1]+grad4[1])/4)
    return gradient

# use N*tanh(A del altitude * vec) to model the alert level if spreading in that direction

def find_rho(p, vec):
    """
    find the drone density needed at a point
    #grad: a tuple representing the gradient at the point
    vec: the unit vector pointing outward the cluster
    #vege: the vegetation array (true/false). we want to check the vegetation in the square with 
    side length centered at
    the point 
    """
    rho = None
    grad = find_grad(p, grad(Topography))
    crit = N*np.tanh(dot_product(grad,vec))
    #first check by altitude gradient(the topography)
    if -1 <= crit <=0:
        rho = 0.5
    elif 0 <= crit <= 0.5:
        rho = 1
    else:
        rho = 2
    px = p[0]/Array_step
    py = p[1]/Array_step
    ceilx = np.ceil(px)
    ceily = np.ceil(py)
    idx = Fuel_check/2/Array_step
    idx2 = 4*idx**2
    temp = np.sum(Vegetation[ceilx-idx:ceilx+idx][ceily-idx:ceily+idx])
    #second check by fuel(vegetation)
    if temp < 0.2*idx2:
        rho = 0
    elif 0.2 <= temp <= 0,5:
        rho *= 0.5
    else:
        continue
    
    
    return rho



def assign_SSA(lst):
    """
    the input will be a list of drone densities at equispaced points along the fire edge. 
    returns the total number of SSA drones needed
    """




def main():
    










"""

ch = Cluster()
for _ in range(500):
    ch.add(Point(100000*random.uniform(0,1), 100000*random.uniform(0,1)))

print("Points on hull:", ch.get_hull_points())
print(ch.get_edges())
print(ch.get_area())
ch.display()


"""




    



