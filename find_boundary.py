#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 22:15:01 2021

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
        return a list of list. Each sublist is made up with a double and a tuple. The tuple contains the 
        coords of the two endpoints of that edge, and the double corresponds to the perpendicular unit vector
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
        self._area = a/2
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

        plt.title('The boundary of a cluster of fires')
        plt.show()


#some testing

ch = Cluster()
for _ in range(500):
    ch.add(Point(100000*random.uniform(0,1), 100000*random.uniform(0,1)))

print("Points on hull:", ch.get_hull_points())
print(ch.get_edges())
print(ch.get_area())
ch.display()
    


