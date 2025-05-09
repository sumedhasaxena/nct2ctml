# pre-requisites
# this script needs an environment with following packages installed:
# #python 3.10
# #PyTorch
# #surya-ocr

from PIL import Image
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from typing import List
from surya.recognition.schema import TextLine
import argparse
import os

extracted_text_dir = 'extracted_text'

def sort_lines(lines:List[TextLine] | List[dict], tolerance=10.0):
    vertical_groups = []
    for line in lines:
        min_y = line.bbox[1] if isinstance(line, TextLine) else line["bbox"][1]
        found_group = False

        #check for existing groups within y tolerance
        for group in vertical_groups:
            if abs(min_y - group[0]) <= tolerance:
                group.append(line)
                found_group = True
                break

        #if group not found,create a new one
        if not found_group:
            vertical_groups.append([min_y,line])   

    sorted_text = []
    for group in sorted(vertical_groups):
        print(group)
        group_lines = sorted(group[1:], key=lambda x:x.bbox[0])
        for line in group_lines:
            sorted_text.append(line.text)
        sorted_text.append("\n")

    return ' '.join(sorted_text).strip()

def main(image_path: str):
    image = Image.open(image_path)
    langs = ["en"]
    recognition_predictor = RecognitionPredictor()
    detection_predictor = DetectionPredictor()

    predictions = recognition_predictor([image], [langs], detection_predictor)
    text_lines = predictions[0].text_lines
    sorted_text = sort_lines(text_lines)
        
    save_extracted_text(sorted_text, image_path)

def save_extracted_text(extracted_text:str, image_path:str):
    current_dir =  os.path.dirname(__file__)
    op_file = f'{os.path.splitext(os.path.basename(image_path))[0]}.txt'
    op_file_path = os.path.join(current_dir, extracted_text_dir,op_file)
    with open(op_file_path, 'w') as op_text_file:
        op_text_file.write(extracted_text)
    print(f"Extracted text saved at {op_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from an image file.")
    parser.add_argument("image_path", type=str, help="Relative path to the image file")
    args = parser.parse_args()

    main(args.image_path)