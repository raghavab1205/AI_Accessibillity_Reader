"""
Text extraction module for the AI Accessibility Reader.
Handles various file formats and extracts plain text.
"""

import os
import PyPDF2
import docx
from pathlib import Path

def extract_text(file_path):
    """
    Extract text from various file formats
    
    Args:
        file_path (str): Path to the uploaded file
        
    Returns:
        str: Extracted text content
        
    Raises:
        ValueError: If file format is not supported
    """
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.txt':
        return extract_from_txt(file_path)
    elif file_extension == '.pdf':
        return extract_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def extract_from_txt(file_path):
    """Extract text from a plain text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

def extract_from_pdf(file_path):
    """Extract text from a PDF file"""
    text = ""
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
        return text
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

def extract_from_docx(file_path):
    """Extract text from a DOCX file"""
    try:
        doc = docx.Document(file_path)
        full_text = []
        
        for para in doc.paragraphs:
            full_text.append(para.text)
            
        return '\n'.join(full_text)
    except Exception as e:
        raise ValueError(f"Error extracting text from DOCX: {str(e)}")