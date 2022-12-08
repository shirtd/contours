#! /bin/bash

SAMPLE="data/surf/samples/surf8-sample1002-61.csv"
SUBSAMPLE="data/surf/samples/surf8-sample322-111.csv"

python load.py --gauss --downsample 8 --write --contours --barcode --save
python load.py data/surf/surf8.csv --write --greedy --thresh 100 --seed 2525 --save
python load.py data/surf/surf8.csv --write --greedy --thresh 50 --seed 12121 --save --cover

python main.py $SUBSAMPLE --delaunay --contours --barcode --color --save
python main.py $SAMPLE --delaunay --lips --contours --barcode --color --save
python main.py $SAMPLE --sub-file $SUBSAMPLE --delaunay --lips --contours --barcode --color --save

python main.py $SUBSAMPLE --voronoi --contours --barcode --color --save
python main.py $SAMPLE --voronoi --lips --contours --save
python main.py $SAMPLE --save --voronoi --lips --contours --color --nomin --barcode
python main.py $SAMPLE --save --voronoi --lips --contours --color --nomax --barcode --nosmooth
python main.py $SAMPLE  --save --sub-file $SUBSAMPLE --voronoi --lips --contours --color --barcode

# NON-SUB LIPS IS BROKEN
