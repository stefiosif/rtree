build:
	py src/bulkloading.py data/offsets.txt data/coords.txt output/rtree.txt

range:
	py src/rangequeries.py output/rtree.txt data/ranges.txt

knn:
	py src/knnqueries.py output/rtree.txt data/knn.txt 10

.PHONY: clean
clean:
	rm -rf output
