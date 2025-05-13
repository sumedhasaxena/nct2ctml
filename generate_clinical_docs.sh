#!/bin/bash

function show_help() {
    echo "Usage: $0 <image_file>"
    echo
    echo "Automates the execution of three Python scripts in sequence:"
    echo "1. surya_ocr_text_extract.py - Extracts genomic data from image"
    echo "2. get_patient_genomic_data.py - Converts genomic text to JSON"
    echo "3. get_patient_clinical_data.py - Converts clinical text to JSON. Make sure the clinical data for patient is stored under patient_data/clinical_data folder with same file name as image"
    echo "Options:"
    echo "  -h, --help        Display this help message."
}

# Check for help parameter
if [[ "$#" -eq 1 && ("$1" == "-h" || "$1" == "--help") ]]; then
echo "here"
    show_help
    exit 0
fi

# Check if the image file argument is provided
if [ "$#" -ne 1 ]; then
    echo "Error: An image file must be provided."
    show_help
    exit 1
fi

# Get the image file from the first argument
image_file="$1"
base_name="${image_file%.*}"  # Remove the file extension
text_file="${base_name}.txt"   # Construct the text file name

# Activate the first Conda environment for text extraction via suryaocr
conda activate suryaocr
python ./patient_data/surya_ocr_text_extract.py "$image_file"
if [ $? -ne 0 ]; then
    echo "Error running surya_ocr_text_extract.py"
    exit 1
fi
echo "Successfully extracted text via surya ocr"

python ./patient_data/get_patient_genomic_data.py "$text_file"
if [ $? -ne 0 ]; then
    echo "Error running get_patient_genomic_data.py"
    exit 1
fi
echo "Successfully converted extracted text to genomic json"

python ./patient_data/get_patient_clinical_data.py "$text_file"
if [ $? -ne 0 ]; then
    echo "Error running get_patient_clinical_data.py"
    exit 1
fi
echo "Successfully converted clinical data to clinical json"