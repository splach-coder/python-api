import fitz
from utils.INVOICE.text_utils import is_number, handle_number 

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
