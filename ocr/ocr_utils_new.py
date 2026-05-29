"""
OCR utilities for extracting text from PDFs and images
"""

import re
import os
from datetime import datetime, date
from PIL import Image
import PyPDF2

try:
    import easyocr
    EASY_OCR_ENABLED = True
except ImportError:
    EASY_OCR_ENABLED = False

try:
    import pytesseract
    TESSERACT_ENABLED = True
except ImportError:
    TESSERACT_ENABLED = False

from .subjects_config import get_subject_name, extract_subject_codes_from_text

READER = None


def get_reader():
    """Get EasyOCR reader instance"""
    global READER
    if READER is None and EASY_OCR_ENABLED:
        READER = easyocr.Reader(['en'], gpu=False)
    return READER


def normalize_text(text):
    """Normalize whitespace in text"""
    return re.sub(r'\s+', ' ', text).strip()


def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    if EASY_OCR_ENABLED:
        try:
            reader = get_reader()
            if reader:
                results = reader.readtext(image_path, detail=0, paragraph=True)
                text = '\n'.join(results).strip()
                if text:
                    return text
        except Exception:
            pass

    if TESSERACT_ENABLED:
        try:
            image = Image.open(image_path).convert('RGB')
            return pytesseract.image_to_string(image)
        except Exception:
            raise RuntimeError('Tesseract not found. Install Tesseract OCR.')

    raise RuntimeError('OCR engine not available. Install easyocr or pytesseract.')


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        extracted = []
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ''
            except Exception:
                page_text = ''
            if page_text:
                extracted.append(page_text)
    return '\n'.join(extracted).strip()


def parse_timetable_file(file_path):
    """
    Parse timetable to extract exam subjects and dates
    Returns: List of {subject, date}
    """
    text = ''
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)

    text = normalize_text(text)
    
    # Extract subject codes
    codes = extract_subject_codes_from_text(text)
    if not codes:
        return []
    
    # Extract dates
    date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'
    dates = re.findall(date_pattern, text)
    
    exam_items = []
    for i, code in enumerate(codes):
        subject = get_subject_name(code) or code
        exam_date = dates[i] if i < len(dates) else date.today().isoformat()
        exam_items.append({
            'subject': subject,
            'code': code,
            'date': exam_date
        })
    
    return exam_items


def parse_syllabus_file(file_path):
    """
    Parse syllabus to extract subjects and topics
    Returns: List of {subject, topics, hours_needed}
    """
    text = ''
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)
    
    text = normalize_text(text)
    
    # Extract subject codes
    codes = extract_subject_codes_from_text(text)
    
    syllabus_items = []
    for code in codes:
        subject = get_subject_name(code) or code
        
        # Extract topics (numbered or bulleted items)
        topic_pattern = r'\d+\.\s+([A-Z][^\n]{10,100})'
        topics = re.findall(topic_pattern, text)
        
        if not topics:
            topics = ['Introduction', 'Core Concepts', 'Applications']
        
        # Calculate hours based on topic count
        num_topics = len(topics)
        if num_topics <= 2:
            hours = 2.0
        elif num_topics <= 5:
            hours = 2.5
        else:
            hours = 3.0
        
        syllabus_items.append({
            'subject': subject,
            'topics': topics[:5],
            'num_topics': num_topics,
            'hours_needed': hours,
            'days_needed': max(1, int(hours / 2.5)),
            'difficulty': 'Hard' if hours >= 3.0 else 'Medium' if hours >= 2.5 else 'Easy'
        })
    
    return syllabus_items
