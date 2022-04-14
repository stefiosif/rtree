import sys
import csv
from mbr import MBR
from os import path, makedirs

if not path.exists('output'):
    makedirs('output')

# Given a set of coordinates find the MBR
def find_mbr(obj_id, points):
    xlow = min(points, key=lambda p: p[0])[0]
    xhigh = max(points, key=lambda p: p[0])[0]
    ylow = min(points, key=lambda p: p[1])[1]
    yhigh = max(points, key=lambda p: p[1])[1]

    return MBR(obj_id, xlow, xhigh, ylow, yhigh)

# Given a set of MBRs find their MBR
def create_mbr(node_id, mbrs):
    xlow = min(mbr.xlow for mbr in mbrs)
    xhigh = max(mbr.xhigh for mbr in mbrs)
    ylow = min(mbr.ylow for mbr in mbrs)
    yhigh = max(mbr.yhigh for mbr in mbrs)

    return MBR(node_id, xlow, xhigh, ylow, yhigh)

# Read data from input files
def input_reader(filename1, filename2):
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
def output_writer(filename, RTREE):
    with open(filename, 'w+') as rtree:
        node_num = 0
        leaves = 0
        for level in RTREE:
            for node in level:
                rtree.write("[{}, {}, [[".format(leaves, node_num))
                for i in range(len(node) - 1):
                    rtree.write("{}, [{}, {}, {}, {}]],[".format(
                        node[i].id, node[i].xlow, node[i].xhigh, node[i].ylow, node[i].yhigh))
                rtree.write("{}, [{}, {}, {}, {}]]]]".format(
                        node[-1].id, node[-1].xlow, node[-1].xhigh, node[-1].ylow, node[-1].yhigh))
                rtree.write("\n")
                node_num += 1
            leaves = 1

# Bulk load R-Tree
def construct(collection):
    level = [] # list of levels(of nodes) of nodes(of mbrs) of mbrs(of points)
    node_id = 0
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
            collection.append(create_mbr(node_id, node))
            node_id += 1

        level.append(nodes)
        print("{} nodes at level {}".format(len(nodes), rank))
        rank += 1

    return level

if __name__ == '__main__':
    # Read the coordinates of the polygons points
    set_of_points = input_reader(filename1=sys.argv[1], filename2=sys.argv[2])

    # Create the mbrs of the polygons
    mbrs = []
    for sp in set_of_points:
        mbrs.append(find_mbr(sp[0], sp[1]))

    # Sort the mbrs based on the Z curve
    mbrs.sort(key=lambda ld: ld.zcurve)

    # Make the Rtree
    rTree = construct(mbrs)
    output_writer("output/rtree.txt", rTree)
