#!/usr/bin/env bash

device=0
if [ $# -ge 1 ]; then
    device=$1
fi

exp=''
if [ $# -ge 2 ]; then
    exp=$2
fi

DATA='data' # input dir
OUT='/media/nas_mount/Rohan/out_latest/out' # output dir

DATA_BIN=$OUT/data_bin
# DATA_RAW=$OUT/custom_data_raw
DATA_RAW=$OUT/data_raw

mkdir -p $DATA_BIN
mkdir -p $DATA_RAW

MODELS=$OUT/models$exp
RESULT=$OUT/tejas_result$exp
mkdir -p $MODELS
mkdir -p $RESULT
