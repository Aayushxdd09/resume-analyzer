from PyPDF2 import PdfReader
import docx

def extract_text(file_path):
    text = ""

    # If file is PDF
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)

        for page in reader.pages:
            text += page.extract_text() or ""

    # If file is Word
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)

        for para in doc.paragraphs:
            text += para.text + "\n"

    return text