#!/bin/bash

DIR='data'
FOLDER='figures'

NAME='surf'
RES=7
SURF="$NAME$RES"

THRESH1=100
THRESH2=150


if [ -d "$DIR/$NAME" ]; then
  rm -r "$DIR/$NAME"
fi

# if [ -d "$FOLDER/$SURF" ]; then
#   rm -r "$FOLDER/$SURF"
# fi

STEP=0
RUN () {
  printf '%s%s%s\n' "$(tput setaf 2)" "($STEP) python $1" "$(tput sgr0)"
  STEP=$( expr $STEP + 1 )
  python $1
}

# SAMPLE 1 DELAUNAY
RUN "load.py --write --save --gauss --downsample $RES --barcode --contours --thresh $THRESH1 --greedy"
SAMPLE1=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH1}.csv" )
RUN "main.py $SAMPLE1 --save --delaunay --contours --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE1 --save --delaunay --contours --color --barcode --alpha 2e4"

# SAMPLE 2 DELAUNAY
RUN "load.py $DIR/$NAME/$SURF.csv --write --save --thresh $THRESH2 --greedy --alpha 2e4"
SAMPLE2=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH2}.csv" )
RUN "main.py $SAMPLE2 --save --delaunay --contours --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE2 --save --delaunay --contours --color --barcode --alpha 2e4"

# LIPS DELAUNAY SUBSAMPLE
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --color --barcode --alpha 2e4"

# LIPS DELAUNAY SUBSAMPLE OP
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --contours --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --contours --color --barcode --alpha 2e4"

# # LIPS COVER
# RUN "main.py $SAMPLE1 --save --lips --cover --contours"
# RUN "main.py $SAMPLE1 --save --lips --cover --color --contours"
# RUN "main.py $SAMPLE1 --save --lips --union --contours"
# RUN "main.py $SAMPLE1 --save --lips --union --color --contours"
#
# # RIPS
# RUN "main.py $SAMPLE1 --save --rips --contours --barcode"
# RUN "main.py $SAMPLE2 --save --rips --contours --barcode"
# RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --barcode"
