#!/bin/bash

DIR='data'
FOLDER='figures'
RES=16
THRESH=2000

if [ -d "$DIR/test" ]; then
  rm -r "$DIR/test"
fi

if [ -d "$FOLDER/test" ]; then
  rm -r "$FOLDER/test"
fi

STEP=0
RUN () {
  printf '%s%s%s\n' "$(tput setaf 2)" "($STEP) python $1" "$(tput sgr0)"
  STEP=$( expr $STEP + 1 )
  python $1
}

RUN "load.py $DIR/test.asc --save --downsample $RES"
RUN "sample.py $DIR/test/test$RES.csv --save --barcode --contours --thresh 2000 --greedy --force"

SAMPLE=$( echo "$DIR/test/samples/test$RES-sample"*"-${THRESH}.csv" )

RUN "main.py $SAMPLE --save --rips --contours --barcode"
