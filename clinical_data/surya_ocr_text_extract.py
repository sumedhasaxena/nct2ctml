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
    s = sort_lines(text_lines)
    print(s)

#IMAGE_PATH = "mtb/case1.png"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from an image file.")
    parser.add_argument("image_path", type=str, help="Relative path to the image file")
    args = parser.parse_args()

    main(args.image_path)