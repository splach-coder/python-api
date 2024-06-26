import json

def is_number(input_value):
    input_str = str(input_value)
    input_str = input_str.replace(",", "")
    input_str = input_str.replace(".", "")
    return input_str.isdigit()

def handle_number(input_value):
    input_str = str(input_value)
    input_str = input_str.replace(".", "")
    input_str = input_str.replace(",", ".")
    return float(input_str)

def data_to_json(data_list, key_map):
    if len(data_list) != len(key_map):
        raise ValueError("Length of data list and key map must be equal.")

    data_dict = dict(zip(key_map, data_list))
    return json.dumps(data_dict)
