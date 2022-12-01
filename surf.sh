#!/bin/bash

DIR='data'
FOLDER='figures'

NAME='surf'
RES=4
SURF="$NAME$RES"

STEP=0
RUN () {
  printf '%s%s%s\n' "$(tput setaf 2)" "($STEP) python $1" "$(tput sgr0)"
  STEP=$( expr $STEP + 1 )
  python $1
}


RUN "load.py data/$NAME/$SURF.csv --contours --barcode --save"

# # SAMPLE1="data/surf/samples/surf8-sample1654-45.csv"
# # SAMPLE2="data/surf/samples/surf8-sample217-153.csv"
#
# SAMPLE1="data/surf/samples/surf8-sample1662-45.csv"
# SAMPLE2="data/surf/samples/surf8-sample228-153.csv"

SAMPLE1="data/surf/samples/surf4-sample1618-45.csv"
SAMPLE2="data/surf/samples/surf4-sample454-100.csv"

RUN "load.py data/$NAME/$SURF.csv --sample-file $SAMPLE1 --save --cover"
RUN "load.py data/$NAME/$SURF.csv --sample-file $SAMPLE2 --save --color"


# if [ -d "$DIR/$NAME" ]; then
#   rm -r "$DIR/$NAME"
# fi
#
# if [ -d "$FOLDER/$SURF" ]; then
#   rm -r "$FOLDER/$SURF"
# fi
#
# THRESH1=70
# THRESH2=210
#
# # SAMPLE 1 DELAUNAY
# RUN "load.py --write --save --gauss --downsample $RES --barcode --contours --thresh $THRESH1 --greedy"
# SAMPLE1=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH1}.csv" )
#
# # SAMPLE 2 DELAUNAY
# RUN "load.py $DIR/$NAME/$SURF.csv --write --save --thresh $THRESH2 --greedy --alpha 2e4"
# SAMPLE2=$( echo "$DIR/$NAME/samples/$SURF-sample"*"-${THRESH2}.csv" )

RUN "main.py $SAMPLE1 --save --delaunay --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE1 --save --delaunay --barcode --contours --color --alpha 2e4"
RUN "main.py $SAMPLE1 --save --delaunay --alpha 2e4"

RUN "main.py $SAMPLE2 --save --delaunay --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE2 --save --delaunay --barcode --contours --color --alpha 2e4"
RUN "main.py $SAMPLE2 --save --delaunay --alpha 2e4"

# LIPS DELAUNAY SUBSAMPLE
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --barcode --contours --color --nomin --alpha 2e4"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --delaunay --contours --color --nomax --alpha 2e4"

# LIPS DELAUNAY SUBSAMPLE
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --barcode --nosmooth --alpha 2e4"
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --barcode --contours --color --nomin --alpha 2e4"
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --delaunay --contours --color --nomax --alpha 2e4"

# LIPS COVER
RUN "main.py $SAMPLE1 --save --lips --cover --contours"
RUN "main.py $SAMPLE1 --save --lips --cover --color --contours"
RUN "main.py $SAMPLE1 --save --lips --union --contours"
RUN "main.py $SAMPLE1 --save --lips --union --color --contours"

# RIPS
RUN "main.py $SAMPLE1 --save --rips --barcode --nosmooth"
RUN "main.py $SAMPLE1 --save --rips --barcode --contours --color"

RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --barcode --nosmooth"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --color --nomax --barcode"
RUN "main.py $SAMPLE1 --sub-file $SAMPLE2 --save --lips --rips --contours --color --nomin --noim"


RUN "main.py $SAMPLE2 --save --rips --barcode --nosmooth"
RUN "main.py $SAMPLE2 --save --rips --barcode --contours --color"

RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --rips --barcode --nosmooth"
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --rips --contours --color --nomax --barcode"
RUN "main.py $SAMPLE2 --sub-file $SAMPLE1 --save --lips --rips --contours --color --nomin --noim"
