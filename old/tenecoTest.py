import fitz
import json

key_map = ["VAT", "Inv date", "Inv Reference", "Cnee", "VAT Cnee", "Reference1", "Reference2", "Customs authorisation", "Collis", "test", "Weight", "INCO", "Invoiceamount", "Items" ]
errors = []
totals_strings = ['Summe/Total amount', 'Summe ohne MwSt/Total w/o VAT', 'Lieferbedingungen/Terms of delivery', 'Gewicht/Weight (KG)', 'Anzahl der Einheiten', 'Verpackung']
Customs_authorisation_strings = ['(customs authorisation No ']

first_data_coordinates = [
    #Vat
    (60, 57, 200, 67),
    #Inv Date 
    (100, 158, 150, 168),
    #Inv Reference
    (160, 158, 230, 168),

    #bill to cnee
    (36, 190, 177, 200),
    #ship to cnee
    (305, 190, 446, 200),
    #Vat cnee
    (305, 254, 446, 264),

    #ref1
    (36, 254, 150, 264),
    #ref2
    (170, 254, 200, 264),
]
Customs_authorisation_coordinates = (330, 338, 350, 349)
Totals_cords = (97, 740, 549, 752)

start_x = 41  # Adjust based on actual starting x-coordinate
start_y = 180  # Adjust based on actual starting y-coordinate
rect_width = 290  # Adjust based on the width of the table
rect_height = 9  # Adjust based on the height of one row
height_increment = 10  # Adjust based on the height of one row
empty_threshold = 1  # Number of empty rows to detect the end of the table


def data_to_json(data_list, key_map):
    if len(data_list) != len(key_map):
        raise ValueError("Length of data list and key map must be equal.")

    data_dict = dict(zip(key_map, data_list))
    return json.dumps(data_dict)

def check_strings_equal(str1, str2):
    return str1 == str2

def check_cnee(arr):
    errors = []
    
    # Check if the array has at least 5 items
    if len(arr) < 5:
        errors.append("Array does not have enough items.")
        return arr, errors
    
    cnee1 = arr[3]
    cnee2 = arr[4]
    
    if check_strings_equal(cnee1, cnee2):
        arr.pop(4)
    else:
        errors.append(f"cnee1 ({cnee1}) and cnee2 ({cnee2}) are different. Please check this.")
    
    return arr, errors

def extract_multidata_with_cords_and_pagenum(pdf_path, page_num, coordinates):
    pdf_document = fitz.open(pdf_path)
    extracted_text = {}

    # Convert to 0-based index for page access
    page_index = page_num - 1

    # Check if the page number is valid
    if page_index < 0 or page_index >= len(pdf_document):
        return None, f"Invalid page number: {page_num}"

    page = pdf_document[page_index]
    page_text = []
    
    for (x0, y0, x1, y1) in coordinates:
            rect = fitz.Rect(x0, y0, x1, y1)
            text = page.get_text("text", clip=rect)
            page_text.append(text.strip())
    
    page_text

    return page_text

def extract_single_data_from_page_cords(pdf_path, page_num, coordinates):
    pdf_document = fitz.open(pdf_path)
    extracted_text = {}

    # Convert to 0-based index for page access
    page_index = page_num - 1

    # Check if the page number is valid
    if page_index < 0 or page_index >= len(pdf_document):
        return None, f"Invalid page number: {page_num}"

    page = pdf_document[page_index]
    
    # Extract text from the specified coordinates
    x0, y0, x1, y1 = coordinates
    rect = fitz.Rect(x0, y0, x1, y1)
    text = page.get_text("text", clip=rect)

    return text.strip()

def find_page_with_all_strings(pdf_path, search_strings):
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        all_found = True
        
        for search_text in search_strings:
            text_instances = page.search_for(search_text)
            if not text_instances:
                all_found = False
                break
        
        if all_found:
            # Returning the 1-based page number
            return page_num + 1

    return "No page contains all the strings together."

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

def extract_table_from_page(pdf_path, page_num, start_x, start_y, rect_width, rect_height, height_increment, empty_threshold):
    pdf_document = fitz.open(pdf_path)
    page_index = page_num - 1

    if page_index < 0 or page_index >= len(pdf_document):
        return None, f"Invalid page number: {page_num}"

    page = pdf_document[page_index]
    extracted_objects = []
    empty_count = 0
    y0 = start_y

    while True:
        y1 = y0 + rect_height
        rect = fitz.Rect(start_x, y0, start_x + rect_width, y1)
        text = page.get_text("text", clip=rect).strip()
        
        if text:
            #print(text)
            # Assuming the text fields are separated by a consistent delimiter, e.g., whitespace
            fields = text.split('\n')  # Adjust splitting logic as needed

            data_object = {
                'Commodity': fields[0] if len(fields) > 0 else "",
                'Origin': fields[1] if len(fields) > 1 else "",
                'Netweight': fields[2] if len(fields) > 2 else "",
                'Quantity': fields[3] if len(fields) > 3 else "",
                'Value': fields[4] if len(fields) > 4 else ""
            }
            
            # Check field types
            if is_number(data_object['Commodity']) and isinstance(data_object['Origin'], str) and is_number(data_object['Netweight']) and is_number(data_object['Quantity'])and is_number(data_object['Value']) :

                data_object['Value'] = handle_number(data_object['Value'])
                data_object['Origin'] = data_object['Origin'].encode('latin1').decode('unicode_escape')
                extracted_objects.append(data_object)
                empty_count = 0  # Reset empty count if text is found and valid
            else:
                empty_count += 1
        else:
            empty_count += 1

        if empty_count >= empty_threshold:
            break

        y0 += height_increment

    return extracted_objects, None


if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "CH_repr.pdf"
    final_version = []
    errors = []

    extracted_text = extract_multidata_with_cords_and_pagenum(pdf_path, 1, first_data_coordinates)
    #first check to check if the cnee is the same
    extracted_text_cnee_checked, errors = check_cnee(extracted_text)    
    final_version = extracted_text_cnee_checked

    #this is for the Customs_authorisation
    page_num = find_page_with_all_strings(pdf_path, Customs_authorisation_strings)
    Customs_authorisation = extract_single_data_from_page_cords(pdf_path, page_num, Customs_authorisation_coordinates)
    final_version.append(Customs_authorisation)

    #this is for totals
    page_num2 = find_page_with_all_strings(pdf_path, totals_strings)
    Totals = extract_single_data_from_page_cords(pdf_path, page_num2, Totals_cords).split('\n')
    final_version.extend(Totals)

    #this is for table
    extracted_lines, error = extract_table_from_page(pdf_path, 6, start_x, start_y, rect_width, rect_height, height_increment, empty_threshold)
    final_version.append(extracted_lines)

    print(data_to_json(final_version, key_map))
