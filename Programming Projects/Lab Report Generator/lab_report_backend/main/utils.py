import PyPDF2

def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text