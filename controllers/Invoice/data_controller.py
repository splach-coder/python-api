from flask import Blueprint, jsonify, request
import os
import json
from services.INVOICE.pdf_service import extract_single_data_from_page_cords, find_page_with_all_strings, extract_multidata_with_cords_and_pagenum, extract_table_from_page
from utils.INVOICE.text_utils import data_to_json
from config.Invoice.coords import first_data_coordinates, Customs_authorisation_coordinates, Totals_cords, start_x, start_y, rect_width, rect_height, height_increment, empty_threshold
from config.Invoice.data_structure import totals_strings, Customs_authorisation_strings, key_map
from utils.INVOICE.controllers import check_cnee

data_blueprint = Blueprint('data', __name__)

@data_blueprint.route('/api/invoice/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist('file')

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

            final_version = []
            errors = []

            extracted_text = extract_multidata_with_cords_and_pagenum(uploaded_file_path, 1, first_data_coordinates)
            #first check to check if the cnee is the same
            extracted_text_cnee_checked, errors = check_cnee(extracted_text)    
            final_version = extracted_text_cnee_checked

            #this is for the Customs_authorisation
            page_num = find_page_with_all_strings(uploaded_file_path, Customs_authorisation_strings)
            Customs_authorisation = extract_single_data_from_page_cords(uploaded_file_path, page_num, Customs_authorisation_coordinates)
            final_version.append(Customs_authorisation)

            #this is for totals
            page_num2 = find_page_with_all_strings(uploaded_file_path, totals_strings)
            Totals = extract_single_data_from_page_cords(uploaded_file_path, page_num2, Totals_cords).split('\n')
            final_version.extend(Totals)

            #this is for table
            extracted_lines, error = extract_table_from_page(uploaded_file_path, 6, start_x, start_y, rect_width, rect_height, height_increment, empty_threshold)
            final_version.append(extracted_lines)

            final_version = data_to_json(final_version, key_map)

            # Delete the temporary uploaded file
            os.remove(uploaded_file_path)

            # Append the extracted text to the results list
            extracted_data.append({
                "message": "Text extracted successfully",
                "data": final_version,
                "filename": "invoice"
            })

        else:
            extracted_data.append({
                "error": "Invalid file type, only PDF files are allowed",
                "filename": file.filename
            })

    if not extracted_data:
        return jsonify({"error": "No valid files processed"}), 400

    return jsonify(extracted_data), 200

