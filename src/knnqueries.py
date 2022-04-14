import sys
import ast
from mbr import MBR, Node, Point
import heapq as hq

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

# Read and execute all the NN queries
def parse_query(rtree, filename, k):
    with open(filename, 'r') as f:
        num = 0
        for line in f:
            [x, y] = line.split()
            find_knn(rtree, Point(float(x), float(y)), k, num)
            num += 1

# Search and print the neareset k neighboors
def find_knn(rtree, qp, k, num):
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
    rtree = parse_tree(sys.argv[1])
    parse_query(rtree, sys.argv[2], int(sys.argv[3]))
