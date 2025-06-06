from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

from os import listdir
from os.path import isfile, join
import os
from PyPDF2 import PdfReader
from typing import Union
from pathlib import Path


def is_multi_page_pdf(pdf_path: Union[str, Path]) -> bool:
    """
    Check if a PDF file contains more than one page.

    Args:
        pdf_path (Union[str, Path]): Path to the PDF file

    Returns:
        bool: True if PDF has more than one page, False otherwise

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the file is not a valid PDF
    """
    try:
        # Convert string path to Path object if necessary
        pdf_path = Path(pdf_path) if isinstance(pdf_path, str) else pdf_path

        # Check if file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"No file found at {pdf_path}")

        # Check if file has .pdf extension
        if pdf_path.suffix.lower() != '.pdf':
            raise ValueError(f"File {pdf_path} is not a PDF")

        # Open and read the PDF
        with open(pdf_path, 'rb') as file:
            pdf = PdfReader(file)
            return len(pdf.pages) > 1

    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    mypath = "springer"

    LLAMA_PARSE_API = os.getenv("LLAMA_PARSE_API")

    parser = LlamaParse(
        api_key=LLAMA_PARSE_API,
        result_type="markdown",
    )
    file_extractor = {".pdf": parser}

    scientific_papers = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and (".pdf" in f))]
    for scientific_paper in scientific_papers:
        if is_multi_page_pdf(join(mypath, scientific_paper)):
            print(f"{scientific_paper} is 1+ pages")
            documents = SimpleDirectoryReader(
                input_files=[join(mypath, scientific_paper)],
                file_extractor=file_extractor,
            ).load_data()
            # print(documents)
            with open(f'springer-mds/parsed_output-{scientific_paper.split("article")[-1]}.md', 'w') as f:
                for doc in documents:
                    f.write(doc.text + '\n')
        else:
            print(f"{scientific_paper} is 1 ")