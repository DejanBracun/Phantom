import numpy as np
import math

"""
Source: https://github.com/lachibal2/triangle_centers
"""

def getLine(p1, p2):
    """
    p1 is a tuple of the first point
    p2 is a tuple of the second point
    returns a tuple of the slope and y-intercept of the line going throug both points
    """
    try:
        slope = float((p1[1] - p2[1]) / (p1[0] - p2[0]))
        yint = float((-1 * (p1[0])) * slope + p1[1])
        return (slope, yint)
    except ZeroDivisionError:
        print('Divided by Zero Error.')
def getIntersection(line1, line2):
    """
    line1 is a tuple of m and b of the line in the form y=mx+b
    line2 is a tuple of m and b of the line in the form y=mx+b
    returns a tuple of the points of the intersection of the two lines
    """
    slope1, slope2 = line1[0], line2[0]
    yint1, yint2 = line1[1], line2[1]
    matA = np.matrix(str(-1 * slope1) + ' 1;' + str(-1 * slope2) + ' 1')
    matB = np.matrix(str(yint1) + '; ' + str(yint2))
    invA = matA.getI()
    resultant = invA * matB
    return (resultant[0,0], resultant[1,0])
def getMidpoint(p1, p2):
    """
    p1 is a tuple of the first point
    p2 is a tuple of the second point
    returns the midpoint, in tuple form, of p1 and p2
    """
    return(((p1[0] + p2[0]) / 2), ((p1[1] + p2[1]) / 2))
def perpSlope(slope):
    #takes slope(float) and returns the slope of a line perpendicular to it
    return (slope * -1) ** -1
def distance(p1, p2):
    """
    p1 is a tuple of ...
    p2 is a tuple of ...
    returns float of distance between p1 and p2
    """
    return(float(math.sqrt((p1[0] + p2[0]) ** 2 + (p1[1] + p2[1]) ** 2)))
def lineFromSlope(slope, point):
    """
    slope is a float of slope
    point is a tuple of ...
    returns tuple of slope and y intercept
    """
    return (slope, ((slope * (-1 * point[0])) +  point[1]))


def vrniCenter(tocke):
	point1 = tuple(tocke[0])
	point2 = tuple(tocke[1])
	point3 = tuple(tocke[2])
	mid1 = getMidpoint(point1, point2)
	mid2 = getMidpoint(point2, point3)
	line1 = getLine(point1, point2)
	line2 = getLine(point2, point3)
	perp1 = perpSlope(line1[0])
	perp2 = perpSlope(line2[0])
	perpbi1 = lineFromSlope(perp1, mid1)
	perpbi2 = lineFromSlope(perp2, mid2)
	circumcent = getIntersection(perpbi1, perpbi2)
	return circumcent

