import sys
from os import path
from math import sqrt

sys.path.insert(0, path.dirname(path.dirname(path.abspath(__file__))))
from pymorton.pymorton.pymorton import interleave_latlng

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class MBR:
    def __init__(self, id, xlow, xhigh, ylow, yhigh):
        self.xlow = xlow
        self.xhigh = xhigh
        self.ylow = ylow
        self.yhigh = yhigh
        self.id = id
        self.obj = False
        self.zcurve = self.findZcurve()

    def findZcurve(self):
        x_median = (self.xlow + self.xhigh) / 2
        y_median = (self.ylow + self.yhigh) / 2
        return interleave_latlng(y_median, x_median)

    def setDistance(self, p):
        self.distance = self.findDistance(p)

    def findDistance(self, p):
        dx = dy = 0
        if p.x < self.xlow:
            dx = self.xlow - p.x
        elif p.x > self.xhigh:
            dx = p.x - self.xhigh
        else:
            dx = 0

        if p.y < self.ylow:
            dy = self.ylow - p.y
        elif p.y > self.yhigh:
            dy = p.y - self.yhigh
        else:
            dy = 0
        return sqrt(dx**2 + dy**2)

    def makeObject(self):
        self.obj = True

    def intersects(self, other):
        if self.xlow > other.xhigh or self.xhigh < other.xlow:
            return False
        if self.ylow > other.yhigh or self.yhigh < other.ylow:
            return False
        return True

    def __lt__(self, other):
        if self.distance < other.distance:
            return True
        return False

class Node:
    def __init__(self, leaf, id, list_of_mbrs):
        self.leaf = leaf
        self.id = id
        self.list_of_mbrs = list_of_mbrs
