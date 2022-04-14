import sys
import ast
from mbr import MBR, Node

# Read R-Tree from data
def parse_tree(filename):
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

# Read and execute all the range queries
def parse_query(rtree, filename):
    with open(filename, 'r') as f:
        i = 0
        for line in f:
            [xlow, ylow, xhigh, yhigh] = line.split()
            results = []
            range_query(rtree, MBR(int(i), float(xlow), float(xhigh),
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
def range_query(rtree, window, results, node=None):
    # At the root node
    if node == None:
        node = rtree[-1]
        for n in node.list_of_mbrs:
            if window.intersects(n) or n.intersects(window):
                range_query(rtree, window, results, rtree[n.id])
    # At an intermediate node
    elif node.leaf == 1:
        for n in node.list_of_mbrs:
            if window.intersects(n) or n.intersects(window):
                range_query(rtree, window, results, rtree[n.id])
    # At a leaf node
    else:
        for mbr in node.list_of_mbrs:
            if window.intersects(mbr) or mbr.intersects(window):
                results.append(mbr)

if __name__ == '__main__':
    rtree = parse_tree(sys.argv[1])
    parse_query(rtree, sys.argv[2])
