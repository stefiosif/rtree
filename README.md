
# R-Tree
This project demonstrates the construction of an R-Tree using the Morton
space filling curve. 

## Bulk-loading
For every object of the collection, we calculate the z-order value of its center and sort
the collection based on it. Using this technique we want nodes created in the upper levels
to contain objects that are as close to each other as possible. We set the maximum capacity
of a node to 20. To utilize disk space properly at least 40% of each node should be full.
With that in mind, every node except the root should have at least 8 nodes.

## Range query
Given a window size, recursively search the tree from top to bottom for the nodes that
intersect the window. When reaching the leaf nodes stop. Every object from the leaf nodes
that still intersects the window is a hit.

## Nearest Neighbor Query
A heap queue stores the child nodes of the root node, based on the distance from the
point query. Iteratively pop a node from the heap queue and then push its child nodes in it.
When reaching a leaf node, put the objects into the heap queue. Finally, if the heap queue
is about to pop an object, this is the first neighbor hit. Continue until reaching the number
of neighbors requested.

## Run Locally

Clone the project
```bash
  git clone --recursive https://github.com/stefiosif/rtree
```

Construct the R-Tree
```bash
  make build
```

Run all range queries given on `data/ranges.txt`
```bash
  make range
```

Run all knn queries given on `data/knn.txt` where k is specified (e.g. k=10)
```bash
  make knn k=10
```

