#! /bin/bash

SAMPLE="data/surf/samples/surf8-sample1002-61.csv"
SUBSAMPLE="data/surf/samples/surf8-sample322-111.csv"

python load.py --gauss --downsample 8 --write --contours --barcode --save
python load.py data/surf/surf8.csv --write --greedy --thresh 100 --seed 2525 --save
python load.py data/surf/surf8.csv --write --greedy --thresh 50 --seed 12121 --save --cover
python main.py $SUBSAMPLE --delaunay --contours --barcode --color --save
python main.py $SAMPLE --sub-file $SUBSAMPLE --delaunay --lips --contours --barcode --color --save

# NON-SUB LIPS IS BROKEN
