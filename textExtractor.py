import io
import pdfplumber
import docx
from bs4 import BeautifulSoup

# Extracting text of the file
def extract_document_text(upload_file) -> str:
  if upload_file is None:
    return ""

  upload_file.seek(0) # reset file pointer

  filename= upload_file.name.lower()

  if filename.endswith(".txt"):
    return read_txt(upload_file)
  elif filename.endswith(".pdf"):
    return read_pdf(upload_file)
  elif filename.endswith(".docx"):
    return read_docx(upload_file)
  elif filename.endswith(".html") or filename.endswith(".htm"):
    return read_html(upload_file)
  else:
    raise ValueError("Unsupported file type.Please upload .txt, .pdf, .docx, or .html")


def read_txt(file_bytes) -> str:
  bytes_data=file_bytes.read()
  return bytes_data.decode("utf-8",errors="ignore")


def read_pdf(file_bytes) -> str:
  pdf_bytes = io.BytesIO(file_bytes.getbuffer()) # Wrap the uploaded file in a BytesIO stream so pdfplumber can use it.

  text_chunks=[]
  with pdfplumber.open(pdf_bytes) as pdf: # Open the PDF
    for i,page in enumerate(pdf.pages):
      page_text = page.extract_text() or "" #Loop through all pages
      text_chunks.append(f"--- {i+1} ---\n {page_text}")

      full_text = "\n\n".join(text_chunks) #Join all pages into a single string
    return full_text


def read_docx(file_bytes) ->str:
  file_bytes = file_bytes.read() # read all bytes from the upload file
  doc = docx.Document(io.BytesIO(file_bytes)) # Wrap in BytesIO so docx.Document can open it
  paragraphs = [p.text for p in doc.paragraphs] #list paragraphs objects
  return "\n".join(paragraphs) #for each paragraph,take .text and join the newlines

def read_html(file_bytes) -> str:
  bytes_data = file_bytes.read() # Read raw bytes from file
  html_text = bytes_data.decode("utf-8",errors= "ignore") # Decode to HTML string (html_text)
  soup = BeautifulSoup(html_text, "html.parser") # Parse with BeautifulSoup
  return soup.get_text(seperator="\n") # pulls all visible text, removing tags.