import json
import fitz  # PyMuPDF

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

if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "an.pdf"

    # Define the coordinates
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

    extracted_text = extract_text_from_coordinates(pdf_path, coordinates)

    def remove_control_chars(text):
        return ''.join(char for char in text if ord(char))

    
    


    



