import fitz  # PyMuPDF

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


# Example usage
pdf_path = "CH_repr.pdf"
page_num = 6
start_x = 41  # Adjust based on actual starting x-coordinate
start_y = 180  # Adjust based on actual starting y-coordinate
rect_width = 290  # Adjust based on the width of the table
rect_height = 9  # Adjust based on the height of one row
height_increment = 10  # Adjust based on the height of one row
empty_threshold = 1  # Number of empty rows to detect the end of the table

extracted_lines, error = extract_table_from_page(pdf_path, page_num, start_x, start_y, rect_width, rect_height, height_increment, empty_threshold)

total = 0

if error:
    print("Error:", error)
else:
    for line in extracted_lines: 
        total += line['Value']

print("Total:", total)        
