import numpy as np
import math, decimal

'''
The general GA is stil too slow, so here is a potential solution.
The GA struggles to draw fixed radius ranges around points in the grid.
Since the points themselves do not change, I have decided to just memoize the ranges on each point.
This file contains support code for that.
'''


'''Helper Functions'''

'''
From stackexchange bc faster - range but for floats
'''
def float_range(start, stop, step):
  start = decimal.Decimal(start)
  while start < stop:
    yield float(start)
    start += decimal.Decimal(step)

'''
Given box and point coordinates -
    Translates system so lower left is (0,0).
    Makes box height and width multiples of boxSize
'''
def correct_coordinate_system(pointCoords, lowXbound, highXbound, lowYbound, highYbound, boxSize):
    newPointCoords = [(point[0] - lowXbound, point[1] - lowYbound) for point in pointCoords]
    return (newPointCoords, (highXbound - lowXbound)//boxSize + 1, (highYbound - lowYbound)//boxSize + 1)




'''
Point management/memoization class
'''
class PointMaster:
    def __init__(self, boxSize, lowXbound, highXbound, lowYbound, highYbound, containedPoints):
        self.boxSize = float(boxSize)
        self.containedPoints, self.xBound, self.yBound = correct_coordinate_system(containedPoints, lowXbound, highXbound, lowYbound, highYbound, boxSize)
        self.xSpan = list(float_range(boxSize/2.0, self.xBound, boxSize))
        self.ySpan = list(float_range(boxSize/2.0, self.yBound, boxSize))
        self.allPoints = None
        self.allPoints = self.get_all_points()
        self.rangeMap = {}                                  # Maps points to maps from radii to sets of points in range
        for point in self.allPoints:
            self.rangeMap[point] = {}
        self.containedPoints, self.containedWeightedPoints = self.box_contained_points(containedPoints)


    '''
    Self-explanatory getters.
    '''

    def get_all_points(self):
        if self.allPoints == None:
            self.allPoints = [(a,b) for a in self.xSpan for b in self.ySpan]
        return list(self.allPoints)

    def get_range(self, point, radius):
        if point[0] not in self.xSpan or point[1] not in self.ySpan:
            print("Asked for point that does not exist!  " + str(point))
            return None
        if radius in self.rangeMap[point].keys():
            return self.rangeMap[point][radius]
        return self.get_range_unmemoized(point, radius)

    def get_range_unmemoized(self, point, radius):
        pointRange = []
        for i in range(math.ceil(-radius/self.boxSize), math.floor(radius/self.boxSize) + 1):
            remainingDist = int(np.sqrt(radius**2 - (i * self.boxSize)**2))
            for j in range(math.ceil(-remainingDist/self.boxSize), math.floor(remainingDist/self.boxSize) + 1):
                x = point[0] + i * self.boxSize
                y = point[1] + j * self.boxSize
                if x > 0 and y > 0 and x < self.xBound and y < self.yBound:
                    pointRange.append((x,y))
        self.rangeMap[point][radius] = set(pointRange)
        return self.rangeMap[point][radius]

    def get_xSpan(self):
        return list(self.xSpan)

    def get_ySpan(self):
        return list(self.xSpan)

    def get_contained_points(self):
        return list(self.containedPoints)

    def get_contained_weighted_points(self):
        return list(self.containedWeightedPoints)




    def box_contained_points(self, rawPointCoords):
        xVals = self.get_xSpan()
        yVals = self.get_ySpan()

        # Initialize point dict structure
        pointDict = {}
        for a,b in self.get_all_points():
            pointDict[(a,b)] = 0

        # Count points
        for point in rawPointCoords:
            if point[0] <= xVals[0] + self.boxSize/2.0:
                point_x = xVals[0]
            else:
                for x in xVals:
                    if point[0] <= x + self.boxSize/2.0:
                        point_x = x
            
            if point[1] <= yVals[0] + self.boxSize/2.0:
                point_y = yVals[0]
            else:
                for y in yVals:
                    if point[1] <= y + self.boxSize/2.0:
                        point_y = y

            pointDict[(point_x,point_y)] += 1

        # Convert dict into likable data structures
        pointCoords = []
        pointCoordsWeighted = []
        for point in self.get_all_points():
            if pointDict[point] > 0:
                pointCoords.append(point)
                pointCoordsWeighted.append((point[0], point[1], pointDict[point]))

        return pointCoords, pointCoordsWeighted

