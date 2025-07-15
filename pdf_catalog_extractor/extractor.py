import fitz  # PyMuPDF
import re
import json
from typing import List, Dict

SERIES_PATTERNS = [
    r'AVENTOS', r'CLIP', r'LEGRABOX', r'TANDEMBOX', r'BLUMOTION', r'MOVENTO', r'MODUL', r'METABOX', r'COMPACT', r'MINIPRESS', r'ORGA-LINE', r'SERVO-DRIVE', r'TIP-ON', r'RESPOND',
]
PARTNO_PATTERN = r'(?:Part\.?\s*No\.?|Product\s*#|Art\.\s*No\.?|Item\s*No\.?|Code)[:\s]*([A-Za-z0-9\-\/\.]+)'
PARAM_PATTERN = r'([A-Za-z][A-Za-z0-9\-\s\(\)%]+):?\s*([A-Za-z0-9\-\.\s\(\)%]+)'


def extract_components_from_text(text):
    lines = text.split('\n')
    components = []
    current = None
    for line in lines:
        l = line.strip()
        if not l or len(l) < 3:
            continue
        if re.match(r'^(\d+\.|[A-Z][a-zA-Z\s\-]+set)', l):
            if current:
                components.append(current)
            current = {'name': l, 'params': {}, 'part_numbers': []}
            continue
        param_match = re.findall(PARAM_PATTERN, l)
        if param_match and current:
            for k, v in param_match:
                current['params'][k.strip()] = v.strip()
        for m in re.findall(PARTNO_PATTERN, l):
            if current and m not in current['part_numbers']:
                current['part_numbers'].append(m)
    if current:
        components.append(current)
    return components

def extract_series_from_text(text):
    for pat in SERIES_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return pat
    return "Unknown"

def extract_products_from_pdf(pdf_path, start_page, end_page):
    doc = fitz.open(pdf_path)
    all_results = []
    for page_num in range(start_page, min(end_page + 1, len(doc))):
        text = doc[page_num].get_text()
        series = extract_series_from_text(text)
        components = extract_components_from_text(text)
        if components:
            all_results.append({
                'page': page_num + 1,
                'series': series,
                'components': components
            })
    doc.close()
    return all_results 