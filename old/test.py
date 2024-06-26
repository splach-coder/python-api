import re
import json

def swap_number_string(text):
    # Use a regular expression to match a leading number
    text = re.sub(r'\s+', ' ', text).strip()
    match = re.match(r"(\d+)\s*(.*)", text)
    if match:
        number = match.group(1)
        remaining_string = match.group(2)
        return f"{remaining_string} {number}"
    else:
        return text
  
def switch_number_and_string(text):
    # Remove all kinds of whitespace characters including \n, \r, \t, etc.
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    
    # Use a regular expression to find a number and the remaining string
    match = re.match(r"(\D+)\s*(\d+)", cleaned_text)
    if match:
        string_part = match.group(1).strip()
        number_part = match.group(2).strip()
        return f"{number_part} {string_part}"
    else:
        # If no match, return the cleaned text as is
        return cleaned_text

def remove_control_chars(text):
    return ''.join(char for char in text if ord(char) >= 32 and ord(char) != 127)


def update_object(json_object, object_key):
    for key in json_object:
        if key == object_key and key == "Gross Weight":
            json_object[key] = remove_control_chars(json_object[key])
            json_object[key] = switch_number_and_string(json_object[key])
        if key == object_key and key == "Packages":
            json_object[key] = remove_control_chars(json_object[key])
        if key == object_key and key == "Item":
            json_object[key] = remove_control_chars(json_object[key])
            json_object[key] = swap_number_string(json_object[key])
    return json_object

extracted_text = {"Vissel": "MSC GEMMA", "Port Of Loading": "SHANGHAI", "ETA": "08/06/2024", "LoydsNumber": "9936616", "BL number": "MEDUGW933725", "Article": "60", "Agent Code": "MSCBEL", "Stay": "281257", "Quay": "1742", "Date": "15/04/2024", "Container": "MSDU7307112", "Item": "1 \nItem:", "Packages": "328 \nCarton(s)", "Description": "ALU FOLDABLE LOUNGER", "Gross Weight": "kgs.\n 3706"}

extracted_text = update_object(extracted_text, "Gross Weight")
extracted_text = update_object(extracted_text, "Item")
extracted_text = update_object(extracted_text, "Packages")

print(extracted_text)