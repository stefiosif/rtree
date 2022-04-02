import sys
import ast
import heapq as hq
from math import sqrt

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

    def setDistance(self, qp):
        self.distance = self.findDistance(qp)

    def findDistance(self, qp):
        dx = dy = 0
        if qp.x < self.xlow:
            dx = self.xlow - qp.x
        elif qp.x > self.xhigh:
            dx = qp.x - self.xhigh
        else:
            dx = 0

        if qp.y < self.ylow:
            dy = self.ylow - qp.y
        elif qp.y > self.yhigh:
            dy = qp.y - self.yhigh
        else:
            dy = 0
        return sqrt(dx**2 + dy**2)

    def makeObject(self):
        self.obj = True

    def __lt__(self, other):
        if self.distance < other.distance:
            return True
        return False

class Node:
    def __init__(self, leaf, id, list_of_mbrs):
        self.leaf = leaf
        self.id = id
        self.list_of_mbrs = list_of_mbrs

def parseRtree(filename):
    with open(filename, 'r') as f:
        nodes = []
        for line in f:
            node = ast.literal_eval(line)
            mbrs = []
            for mbr in node[2]:
                mbrs.append(MBR(int(mbr[0]), float(mbr[1][0]), float(mbr[1][1]),
                    float(mbr[1][2]), float(mbr[1][3])))
            nodes.append(Node(node[0], node[1], mbrs))

    return nodes

# Read and execute all the NN queries assigned to the r tree
def parseQuery(rtree, filename, k):
    with open(filename, 'r') as f:
        num = 0
        for line in f:
            [x, y] = line.split()
            findKNN(rtree, Point(float(x), float(y)), k, num)
            num += 1

# Search for the neareset k neighboors
def findKNN(rtree, qp, k, num):
    # List to put our k nn objects
    results = []
    # Initialize a priority queue
    pq = []
    # Put the root nodes into the priority queue
    for mbr in rtree[-1].list_of_mbrs:
        mbr.setDistance(qp)
        hq.heappush(pq, mbr)

    while len(pq) > 0 and len(results) < k:
        # Retrieve the next node and remove it from the queue
        e = hq.heappop(pq)

        if e.obj == True:
            hq.heappush(results, e)
            continue

        # At a leaf node
        if rtree[e.id].leaf == 0:
            for mbr in rtree[e.id].list_of_mbrs:
                mbr.setDistance(qp)
                mbr.makeObject()
                hq.heappush(pq, mbr)
        # At an intermediate node
        else:
            for node in rtree[e.id].list_of_mbrs:
                node.setDistance(qp)
                hq.heappush(pq, node)

    print("{}:".format(num), end=' ')
    for r in range(k-1):
        nn = hq.heappop(results)
        print("{},".format(nn.id), end='')
    nn = hq.heappop(results)
    print(nn.id)

if __name__ == '__main__':
    rtree = parseRtree(sys.argv[1])
    parseQuery(rtree, sys.argv[2], int(sys.argv[3]))
