#!/bin/bash

# Synopsis: bash preprocess_qtq.sh <qtq-dataset-name>.json
# <qtq-dataset-name>.json has to be located in ./data/input/

FILE_NAME=$1

if [[ ! -f "./data/input/$FILE_NAME" ]]; then
    echo "./data/input/$FILE_NAME" "file does not exist!"
    echo "Please put the input QTQ file into ./data/input"
    exit
fi

FILE_NAME="${FILE_NAME/.json/}"

mkdir -p "./data/sep/"
mkdir -p "./data/output/"

echo "Starting data seperation..."
python3 seperate_qtq.py --data="./data/input" --subset="$FILE_NAME" --output="./data/sep"
echo "Data seperation finished."
echo "Starting data preprocessing..."
python3 preprocessing_qtq.py --data="./data/sep" --subset="$FILE_NAME" --output="./data/output"
echo "Data preprocessing finished."