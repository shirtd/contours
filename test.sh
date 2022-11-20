#!/bin/bash

DIR='data'
FOLDER='figures'

NAME='surf'
RES=16
SURF="$NAME$RES"

THRESH1=200
THRESH2=400


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

# RUN "load.py $DIR/test.asc --save --downsample $RES"
RUN "load.py --save --gauss --downsample $RES"

RUN "sample.py $DIR/$NAME/$SURF.csv --save --barcode --contours"
RUN "sample.py $DIR/$NAME/$SURF.csv --save --thresh $THRESH1 --greedy --force"
RUN "sample.py $DIR/$NAME/$SURF.csv --save --thresh $THRESH2 --greedy --force"

SAMPLE1=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH1}.csv" )
SAMPLE2=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH2}.csv" )

RUN "main.py $SAMPLE1 --save --rips --contours --barcode"
RUN "main.py $SAMPLE2 --save --rips --contours --barcode"

RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --barcode"
# RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --barcode --local"
