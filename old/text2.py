import fitz

def search_text_with_coords(pdf_path, search_text):
  """
  This function searches for text in a PDF document and returns a list of dictionaries
  containing the text and its coordinates (x0, y0, x1, y1).

  Args:
      pdf_path (str): Path to the PDF document.
      search_text (str): The text to search for.

  Returns:
      list: A list of dictionaries containing text and its bounding box information.
  """
  results = []
  pdf_document = fitz.open(pdf_path)

  for page in pdf_document:
    blocks = page.get_text("blocks")
    for block in blocks:
      text = block[4]  # Accessing the text content of the block (index 4)
      if search_text in text:

        # Access coordinates by index (avoiding unpacking issue)
        x0 = block[0]
        y0 = block[1]
        x1 = block[2]
        y1 = block[3]

        result = {
          "text": text,
          "x0": x0,
          "y0": y0,
          "x1": x1,
          "y1": y1,
        }
        results.append(result)

  return results

if __name__ == "__main__":
  pdf_path = "CH_repr.pdf"  # Replace with your actual PDF path
  search_text = "DAP NIEDERBIPP"

  results = search_text_with_coords(pdf_path, search_text)

  if results:
    for result in results:
      print(f"Text: {result['text']}")
      print(f"Coordinates: ({result['x0']}, {result['y0']}), ({result['x1']}, {result['y1']})")
      print("-" * 20)
  else:
    print(f"Search text '{search_text}' not found in the PDF.")
