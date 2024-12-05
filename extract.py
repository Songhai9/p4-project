import PyPDF2

def extract_text(pdf_path, output_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    with open(output_path, 'w', encoding='utf-8') as out_file:
        out_file.write(text)

if __name__ == "__main__":
    pdf_path = 'main.pdf'
    output_path = 'sujet.txt'
    extract_text(pdf_path, output_path)
    print(f"Text extracted to {output_path}")