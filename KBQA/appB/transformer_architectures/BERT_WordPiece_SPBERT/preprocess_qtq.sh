#!/bin/bash

FILE_NAME=$1

if [[ ! -f "./data/input/$FILE_NAME" ]]; then
    echo "./data/input/$FILE_NAME" "file does not exist!"
    exit
fi

FILE_NAME="${FILE_NAME/.json/}"

mkdir -p "./data/sep/"
mkdir -p "./data/output/"

python3 seperate_qtq.py --data="./data/input" --subset="$FILE_NAME" --output="./data/sep"
python3 preprocessing_qtq.py --data="./data/sep" --subset="$FILE_NAME" --output="./data/output"