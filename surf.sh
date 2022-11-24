#!/bin/bash

DIR='data'
FOLDER='figures'

NAME='surf'
RES=8
SURF="$NAME$RES"

THRESH1=80
THRESH2=250


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

# SAMPLE 1 DELAUNAY
RUN "load.py --write --save --gauss --downsample $RES --barcode --contours --thresh $THRESH1 --greedy"
SAMPLE1=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH1}.csv" )
RUN "main.py $SAMPLE1 --save --delaunay --contours --barcode"
RUN "main.py $SAMPLE1 --save --delaunay --contours --color"

# SAMPLE 2 DELAUNAY
RUN "load.py $DIR/$NAME/$SURF.csv --write --save --thresh $THRESH2 --greedy"
SAMPLE2=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH2}.csv" )
RUN "main.py $SAMPLE2 --save --delaunay --contours --barcode"
RUN "main.py $SAMPLE2 --save --delaunay --contours --color"

# LIPS DELAUNAY SUBSAMPLE
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --barcode"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --color"

# LIPS COVER
RUN "main.py $SAMPLE1 --save --lips --cover --contours"
RUN "main.py $SAMPLE1 --save --lips --cover --color --contours"
RUN "main.py $SAMPLE1 --save --lips --union --contours"
RUN "main.py $SAMPLE1 --save --lips --union --color --contours"

# RIPS
RUN "main.py $SAMPLE1 --save --rips --contours --barcode"
RUN "main.py $SAMPLE2 --save --rips --contours --barcode"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --barcode"
