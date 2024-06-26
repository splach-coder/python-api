from flask import Blueprint, jsonify, request
import os
import json
from services.MSC.pdf_service import extract_text_from_coordinates
from utils.MSC.text_utils import data_to_json, update_object
from config.MSC.coords import coordinates
from config.MSC.data_structure import key_map


data_blueprint = Blueprint('data', __name__)



@data_blueprint.route('/api/msc/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist('files')

    if not files:
        return jsonify({"error": "No selected files"}), 400

    extracted_data = []

    for file in files:
        if file.filename == '':
            continue

        if file and file.filename.endswith('.pdf'):
            # Save the uploaded file temporarily
            uploaded_file_path = './temp/' + file.filename
            file.save(uploaded_file_path)

            # Extract text from PDF based on coordinates
            extracted_text = extract_text_from_coordinates(uploaded_file_path, coordinates)
            extracted_text = data_to_json(extracted_text[1], key_map)
            extracted_text = json.loads(extracted_text)

            extracted_text = update_object(extracted_text, "Gross Weight")
            extracted_text = update_object(extracted_text, "Item")
            extracted_text = update_object(extracted_text, "Packages")

            # Delete the temporary uploaded file
            os.remove(uploaded_file_path)

            # Append the extracted text to the results list
            extracted_data.append({
                "message": "Text extracted successfully",
                "data": extracted_text,
                "filename": extracted_text.get("Container", file.filename)
            })
        else:
            extracted_data.append({
                "error": "Invalid file type, only PDF files are allowed",
                "filename": file.filename
            })

    if not extracted_data:
        return jsonify({"error": "No valid files processed"}), 400

    return jsonify(extracted_data), 200

