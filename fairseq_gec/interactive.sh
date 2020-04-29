#!/usr/bin/env bash
source ./config.sh

copy_params='--copy-ext-dict --replace-unk'
if $WO_COPY; then
    copy_params='--replace-unk'
fi

beam=12

CUDA_VISIBLE_DEVICES=0 python interactive.py $DATA_RAW \
--path /media/nas_mount/Rohan/out_latest/out/modelsexp_t2/checkpointema9.pt \
--beam $beam \
--nbest 1 \
--no-progress-bar \
--print-alignment \
--input /media/nas_mount/Rohan/out_latest/out/data_raw/spell_raw_ben_30.txt \

$copy_params

#--replace-unk ./data/bin/alignment.src-tgt.txt \
#--path $MODELS/checkpointema1.pt \
