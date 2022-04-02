from os import write
from os import path, makedirs
import sys
import csv

if not path.exists('output'):
    makedirs('output')

_DIVISORS = [180.0 / 2 ** n for n in range(32)]

class MBR:
    def __init__(self, id, xlow, xhigh, ylow, yhigh):
        self.xlow = xlow
        self.xhigh = xhigh
        self.ylow = ylow
        self.yhigh = yhigh
        self.id = id
        self.zcurve = self.findZcurve()

    def findZcurve(self):
        x_median = (self.xlow + self.xhigh) / 2
        y_median = (self.ylow + self.yhigh) / 2
        return interleave_latlng(y_median, x_median)

def interleave_latlng(lat, lng):
    if lng > 180:
        x = (lng % 180) + 180.0
    elif lng < -180:
        x = (-((-lng) % 180)) + 180.0
    else:
        x = lng + 180.0
    if lat > 90:
        y = (lat % 90) + 90.0
    elif lat < -90:
        y = (-((-lat) % 90)) + 90.0
    else:
        y = lat + 90.0

    morton_code = ""
    for dx in _DIVISORS:
        digit = 0
        if y >= dx:
            digit |= 2
            y -= dx
        if x >= dx:
            digit |= 1
            x -= dx
        morton_code += str(digit)

    return morton_code

# Given a set of coordinates find the MBR
def findMBR(objId, points):
    x_min = min(points, key=lambda p: p[0])[0]
    x_max = max(points, key=lambda p: p[0])[0]
    y_min = min(points, key=lambda p: p[1])[1]
    y_max = max(points, key=lambda p: p[1])[1]

    return MBR(objId, x_min, x_max, y_min, y_max)

# Given a set of MBRs find the MBR
def createMBR(nodeId, mbrs):
    x_min = min(mbr.xlow for mbr in mbrs)
    x_max = max(mbr.xhigh for mbr in mbrs)
    y_min = min(mbr.ylow for mbr in mbrs)
    y_max = max(mbr.yhigh for mbr in mbrs)

    return MBR(nodeId, x_min, x_max, y_min, y_max)

# Read data from input files
def inputReader(filename1, filename2):
    set_of_points = []
    with open(filename1, 'r') as offsets, open(filename2, 'r') as coords:
        reader = csv.reader(offsets, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in reader:
            points = []
            for i in range(int(row[2]) - int(row[1]) + 1):
                points.append([float(x) for x in coords.readline().split(',')])
            set_of_points.append([row[0], points])

    return set_of_points

# Write data into output file
def outputWriter(filename, rTree):
    with open(filename, 'w+') as rtree:
        numNode = 0
        leaves = 0
        for level in rTree:
            for node in level:
                rtree.write("[{}, {}, [[".format(leaves, numNode))
                for i in range(len(node) - 1):
                    rtree.write("{}, [{}, {}, {}, {}]],[".format(
                        node[i].id, node[i].xlow, node[i].xhigh, node[i].ylow, node[i].yhigh))
                rtree.write("{}, [{}, {}, {}, {}]]]]".format(
                        node[-1].id, node[-1].xlow, node[-1].xhigh, node[-1].ylow, node[-1].yhigh))
                rtree.write("\n")
                numNode += 1
            leaves = 1

#
def makeRtree(collection):
    level = [] # list of levels(of nodes) of nodes(of mbrs) of mbrs(of points)
    nodeId = 0
    rank = 0
    # Until we reach the root node
    while len(collection) > 1:
        # Split the mbr collection into nodes of 20
        nodes = [collection[x:x+20] for x in range(0, len(collection), 20)]

        # If the last node has less than 8 mbrs, fill with mbrs of the previous
        balance = 8 - len(nodes[-1])
        if balance > 0 and len(nodes) > 1:
            migrate = len(nodes[-2])
            nodes[-1] = nodes[-2][migrate-balance:] + nodes[-1]
            nodes[-2] = nodes[-2][:migrate-balance]

        # Make the new MBRs based on the corners of each 20-piece
        collection = []
        for node in nodes: #for every 20 MBRs in 500 MBRs
            collection.append(createMBR(nodeId, node))
            nodeId += 1

        level.append(nodes)
        print("{} nodes at level {}".format(len(nodes), rank))
        rank += 1

    return level

if __name__ == '__main__':
    # Read the coordinates of the polygons points
    set_of_points = inputReader(filename1=sys.argv[1], filename2=sys.argv[2])

    # Create the mbrs of the polygons
    mbrs = []
    for sp in set_of_points:
        mbrs.append(findMBR(sp[0], sp[1]))

    # Sort the mbrs based on the Z curve
    mbrs.sort(key=lambda ld: ld.zcurve)

    # Make the Rtree
    rTree = makeRtree(mbrs)
    outputWriter("output/rtree.txt", rTree)
