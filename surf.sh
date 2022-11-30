#!/bin/bash

DIR='data'
FOLDER='figures'

NAME='surf'
RES=6
SURF="$NAME$RES"

THRESH1=50
THRESH2=200


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

# SAMPLE1="data/surf/samples/surf4-sample5122-40.csv"
# RUN "load.py data/$NAME/$SURF.csv --sample-file $SAMPLE1 --save"

RUN "main.py $SAMPLE1 --save --delaunay --contours --color --barcode --alpha 2e4"
RUN "main.py $SAMPLE1 --save --delaunay --contours --barcode --nosmooth --alpha 2e4"

# SAMPLE 2 DELAUNAY
RUN "load.py $DIR/$NAME/$SURF.csv --write --save --thresh $THRESH2 --greedy --alpha 2e4"
SAMPLE2=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH2}.csv" )

# SAMPLE2="data/surf/samples/surf4-sample714-120.csv"
# RUN "load.py data/$NAME/$SURF.csv --sample-file $SAMPLE2 --save"

RUN "main.py $SAMPLE2 --save --delaunay --contours --color --barcode --alpha 2e4"
RUN "main.py $SAMPLE2 --save --delaunay --contours --barcode --nosmooth --alpha 2e4"

# LIPS DELAUNAY SUBSAMPLE
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --barcode --alpha 2e4"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --color --nomin --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --color --nomax --alpha 2e4"

# LIPS DELAUNAY SUBSAMPLE OP
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --contours --barcode --alpha 2e4"
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --contours --color --nomin --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --contours --color --nomax --alpha 2e4"

# LIPS COVER
RUN "main.py $SAMPLE1 --save --lips --cover --contours"
RUN "main.py $SAMPLE1 --save --lips --cover --color --contours"
RUN "main.py $SAMPLE1 --save --lips --union --contours"
RUN "main.py $SAMPLE1 --save --lips --union --color --contours"

# RIPS
RUN "main.py $SAMPLE1 --save --rips --contours --color --barcode"
RUN "main.py $SAMPLE1 --save --rips --contours --color --barcode --nosmooth"
RUN "main.py $SAMPLE2 --save --rips --contours --color --barcode"
RUN "main.py $SAMPLE2 --save --rips --contours --color --barcode --nosmooth"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --barcode"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --color --nomin --barcode --nosmooth"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --color --nomax"
