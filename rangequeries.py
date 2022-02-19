import sys
import ast

class MBR:
    def __init__(self, id, xlow, xhigh, ylow, yhigh):
        self.xlow = xlow
        self.xhigh = xhigh
        self.ylow = ylow
        self.yhigh = yhigh
        self.id = id

    def intersects(self, other):
        if self.xlow > other.xhigh or self.xhigh < other.xlow:
            return False
        if self.ylow > other.yhigh or self.yhigh < other.ylow:
            return False
        return True

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

# Read and execute all the range queries assigned to the r tree
def parseQuery(rtree, filename):
    with open(filename, 'r') as f:
        i = 0
        for line in f:
            [xlow, ylow, xhigh, yhigh] = line.split()
            results = []
            rangeQuery(rtree, MBR(int(i), float(xlow), float(xhigh),
                    float(ylow), float(yhigh)), results)

            print("{} ({}):".format(i, len(results)), end=' ')
            for r in range(len(results) - 1):
                print("{},".format(results[r].id), end='')
            if len(results) != 0:
                print(results[-1].id)
            else:
                print(' ')
            i += 1

# Find the intersecting rectangles
def rangeQuery(rtree, window, results, node=None):
    # At the root node
    if node == None:
        node = rtree[-1]
        for n in node.list_of_mbrs:
            if window.intersects(n) or n.intersects(window):
                rangeQuery(rtree, window, results, rtree[n.id])
    # At an intermediate node
    elif node.leaf == 1:
        for n in node.list_of_mbrs:
            if window.intersects(n) or n.intersects(window):
                rangeQuery(rtree, window, results, rtree[n.id])
    # At a leaf node
    else:
        for mbr in node.list_of_mbrs:
            if window.intersects(mbr) or mbr.intersects(window):
                results.append(mbr)

if __name__ == '__main__':
    rtree = parseRtree(sys.argv[1])
    parseQuery(rtree, sys.argv[2])
