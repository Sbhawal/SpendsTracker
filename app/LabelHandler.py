from app.Constants import *
from app.google_apis import *
import re

def parse_Label_Structure(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    labels = []
    hist = []
    stack = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        level = (len(line) - len(stripped)) // 4  # Assuming 4 spaces per level
        if len(stack) > level:
            labels.append("/".join(hist))
            while len(stack) > level:
                stack.pop()
                hist.pop()
        else:
            if hist:
                labels.append("/".join(hist))
        stack.append(stripped)
        hist.append(stripped)
    return labels

def delete_all_user_labels():
    labels = list_labels(service)
    for label in labels:
        if label['type'] == 'user':
            delete_label(service, label['id'])

def parse_colors_from_Label(label_string):
    hex_code_pattern = r'#[0-9A-Fa-f]{6}'
    hex_codes = re.findall(hex_code_pattern, label_string)
    if not hex_codes:
        return None, None, label_string
    bg_color = hex_codes[0] if len(hex_codes) > 0 else None
    txt_color = hex_codes[1] if len(hex_codes) > 1 else "#000000"
    label = re.sub(hex_code_pattern, '', label_string).strip()
    return bg_color.lower(), txt_color, label

def Add_labels_to_Gmail():
    global LABELS
    global CURRENT_LABELS
    for label in LABELS:
        background_color, text_color, label_name = parse_colors_from_Label(label)
        if label_name not in CURRENT_LABELS:
            create_label(label_name, background_color, text_color)
    print("Label Structure Updated Successfully!")

def get_current_labels_from_Gmail():
    global labelsJson
    current_labels = []
    for label in labelsJson:
        if label["type"] == 'user':
            current_labels.append(label['name'])
    return current_labels

def create_Label_Map():
    labelsJson = list_labels() 
    labelMapping = {}
    for label in labelsJson:
        if label['type'] != 'system':
            labelMapping[label['name']] = label['id']
    return labelMapping


labelMapping = create_Label_Map()
labelsJson = list_labels()           
PARSED_LABELS = parse_Label_Structure(LABEL_STRUCTURE_PATH)
CURRENT_LABELS = get_current_labels_from_Gmail()


LABELS = [x for x in PARSED_LABELS if parse_colors_from_Label(x)[2] not in CURRENT_LABELS]
if len(LABELS):
    print(f"Found {len(LABELS)} New label(s) in the config file. Updating Gmail.")
    Add_labels_to_Gmail()



    



