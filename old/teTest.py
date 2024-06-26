import fitz

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

def find_first_page_with_text_and_coords(pdf_path, search_text):
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text_instances = page.search_for(search_text)
        
        if text_instances:
            # Returning the 1-based page number and the coordinates of the first instance of the text
            return page_num + 1, text_instances[0]  

    return None, None

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

# Example usage
pdf_path = "CH_repr.pdf"
coordinates = [(97, 740, 549, 752)]  # Example coordinates

#extracted_text = extract_text_from_page_coordinates(pdf_path, page_num, coordinates)

arr = ['Summe/Total amount', 'Summe ohne MwSt/Total w/o VAT', 'Lieferbedingungen/Terms of delivery', 'Gewicht/Weight (KG)', 'Anzahl der Einheiten', 'Verpackung']

page_num = find_page_with_all_strings(pdf_path, arr)

extracted_text = extract_multidata_with_cords_and_pagenum(pdf_path, page_num, coordinates)

print(extracted_text[0].split('\n'))