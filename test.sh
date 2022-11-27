#!/bin/bash

DIR='data'
FOLDER='figures'

# (4) python main.py data/rainier_sub/samples/rainier_sub32-sample4179-2000.csv --sub-file data/rainier_sub/samples/rainier_sub32-sample852-5000.csv --save --lips --delaunay --contours --barcode
# loading data/rainier_sub/samples/rainier_sub32-sample4179-2000.csv
# loading data/rainier_sub/samples/rainier_sub32-sample852-5000.csv
# delaunay: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 24688/24688 [00:00<00:00, 123881.08it/s]
# Traceback (most recent call last):
#   File "/Users/kirk/workspace/contours/main.py", line 66, in <module>
#     complex.lips_sub(subsample, args.local)
#   File "/Users/kirk/workspace/contours/contours/complex/complex.py", line 112, in lips_sub
#     s.data['max'] = max(self(0)[v].data['max'] for v in s)
#   File "/Users/kirk/workspace/contours/contours/complex/complex.py", line 112, in <genexpr>
#     s.data['max'] = max(self(0)[v].data['max'] for v in s)
# IndexError: list index out of range

NAME='rainier_sub'
RES=32
SURF="$NAME$RES"
CUTS="200 1000 1400 1800 2500 4500"

THRESH1=1000
THRESH2=2000


if [ -d "$DIR/$NAME" ]; then
  rm -r "$DIR/$NAME"
fi

if [ -d "$FOLDER/$SURF" ]; then
  rm -r "$FOLDER/$SURF"
fi

STEP=0
RUN () {
  printf '%s%s%s\n' "$(tput setaf 2)" "($STEP) python $1" "$(tput sgr0)"
  STEP=$( expr $STEP + 1 )
  python $1
}

# RUN "load.py --write --save --gauss --downsample $RES --barcode --contours --thresh $THRESH1 --greedy"
# RUN "load.py $DIR/$NAME.asc --write --save --downsample $RES --barcode --contours --thresh $THRESH1 --greedy"

# FOR RAINIER_SUB : DIFFERENT CUTS FOR DIFFERENT FUCKS
RUN "load.py $DIR/$NAME.asc --write --save --downsample $RES --barcode --contours --thresh $THRESH1 --greedy --cuts $CUTS"

# SAMPLE 1 DELAUNAY
SAMPLE1=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH1}.csv" )
RUN "main.py $SAMPLE1 --save --delaunay --contours --barcode --nosmooth"

# SAMPLE 2 DELAUNAY
RUN "load.py $DIR/$NAME/$SURF.csv --write --save --thresh $THRESH2 --greedy"
SAMPLE2=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH2}.csv" )
RUN "main.py $SAMPLE2 --save --delaunay --contours --barcode --nosmooth"

# LIPS DELAUNAY SUBSAMPLE
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --barcode --nosmooth"

# # LIPS COVER
# RUN "main.py $SAMPLE1 --save --lips --cover --contours"
# RUN "main.py $SAMPLE1 --save --lips --union --contours"
#
# # RIPS
# RUN "main.py $SAMPLE1 --save --rips --contours --barcode"
# RUN "main.py $SAMPLE2 --save --rips --contours --barcode"
# RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --barcode"
#
#
# RUN "main.py $SAMPLE1 --save --delaunay --contours --color"
# RUN "main.py $SAMPLE2 --save --delaunay --contours --color"
# RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --color"
# RUN "main.py $SAMPLE1 --save --lips --cover --color --contours"
# RUN "main.py $SAMPLE1 --save --lips --union --color --contours"
