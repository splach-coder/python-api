from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import fitz
import re
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to my API!"

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        "name": "ChatGPT",
        "version": "4.0",
        "description": "An example API response"
    }
    return jsonify(data)

def extract_text_from_coordinates(pdf_path, coordinates):
    pdf_document = fitz.open(pdf_path)
    extracted_text = {}

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        page_text = []
        
        for (x0, y0, x1, y1) in coordinates:
            rect = fitz.Rect(x0, y0, x1, y1)
            text = page.get_text("text", clip=rect)
            page_text.append(text.strip())
        
        extracted_text[page_num + 1] = page_text

    return extracted_text

def data_to_json(data_list, key_map):
        if len(data_list) != len(key_map):
          raise ValueError("Length of data list and key map must be equal.")

        data_dict = dict(zip(key_map, data_list))
        return json.dumps(data_dict)

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

key_map = ["Vissel", "Port Of Loading", "ETA", "LoydsNumber", "BL number", "Article", "Agent Code", "Stay", "Quay", "Date", "Container", "Item", "Packages", "Description",  "Gross Weight"]


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        # Save the uploaded file temporarily
        uploaded_file_path = './temp/' + file.filename

        file.save(uploaded_file_path)

        # Define coordinates for text extraction (example)
        coordinates = [
            #line 1
            (50, 253, 110, 263),
            (180, 253, 217, 263),
            (429, 253, 467, 263),
            (490, 253, 570, 263),

            #line 2
            (20, 277, 90, 287),
            (200, 277, 225, 287),
            (250, 277, 280, 287),
            (310, 277, 333, 287),
            (468, 277, 492, 287),
            (495, 277, 560, 287),

            #line 3
            (60, 310, 130, 330),
            (90, 340, 130, 350),
            (150, 340, 210, 350),
            (210, 333, 306, 353),
            (450, 333, 550, 353),
        ]

        # Extract text from PDF based on coordinates
        extracted_text = extract_text_from_coordinates(uploaded_file_path, coordinates)

        extracted_text = data_to_json(extracted_text[1], key_map)
        extracted_text = json.loads(extracted_text)

        extracted_text = update_object(extracted_text, "Gross Weight")
        extracted_text = update_object(extracted_text, "Item")
        extracted_text = update_object(extracted_text, "Packages")
        
        # Delete the temporary uploaded file
        os.remove(uploaded_file_path)

        # Return the extracted text as JSON response
        return jsonify({
            "message": "Text extracted successfully",
            "data": extracted_text,
            "filename": extracted_text["Container"],
        }), 200
    
    else:
        return jsonify({"error": "Invalid file type, only PDF files are allowed"}), 400


if __name__ == '__main__':
    app.run(debug=True)
