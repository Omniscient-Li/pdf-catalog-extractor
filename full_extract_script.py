#!/usr/bin/env python3
"""
完整的PDF产品信息提取脚本
"""

import fitz  # PyMuPDF
import json
import os
import re
from typing import List, Dict, Any
import argparse

# -*- coding: utf-8 -*-
import fitz  # PyMuPDF
import json
import re
import argparse

SERIES_PATTERNS = [
    r'AVENTOS', r'CLIP', r'LEGRABOX', r'TANDEMBOX', r'BLUMOTION', r'MOVENTO', r'MODUL', r'METABOX', r'COMPACT', r'MINIPRESS', r'ORGA-LINE', r'SERVO-DRIVE', r'TIP-ON', r'RESPOND',
]
PARTNO_PATTERN = r'(?:Part\.?\s*No\.?|Product\s*#|Art\.\s*No\.?|Item\s*No\.?|Code)[:\s]*([A-Za-z0-9\-\/\.]+)'

# 简单参数行识别（可根据实际PDF内容优化）
PARAM_PATTERN = r'([A-Za-z][A-Za-z0-9\-\s\(\)%]+):?\s*([A-Za-z0-9\-\.\s\(\)%]+)'


def extract_components_from_text(text):
    lines = text.split('\n')
    components = []
    current = None
    for line in lines:
        l = line.strip()
        if not l or len(l) < 3:
            continue
        # 识别部件/区块名（如以数字或序号开头，或大写字母+set等）
        if re.match(r'^(\d+\.|[A-Z][a-zA-Z\s\-]+set)', l):
            if current:
                components.append(current)
            current = {'name': l, 'params': {}, 'part_numbers': []}
            continue
        # 提取参数
        param_match = re.findall(PARAM_PATTERN, l)
        if param_match and current:
            for k, v in param_match:
                current['params'][k.strip()] = v.strip()
        # 提取Part No.
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

def main():
    parser = argparse.ArgumentParser(description='PDF Catalogue Structured Extractor')
    parser.add_argument('--pdf', type=str, required=True, help='PDF catalogue path')
    parser.add_argument('--start_page', type=int, required=True, help='Start page (1-based)')
    parser.add_argument('--end_page', type=int, required=True, help='End page (1-based, inclusive)')
    parser.add_argument('--output', type=str, default='catalogue_structured.json', help='Output JSON file')
    args = parser.parse_args()
    results = extract_products_from_pdf(args.pdf, args.start_page - 1, args.end_page - 1)
    print(f'提取页数: {args.end_page - args.start_page + 1}, 区块数: {sum(len(r["components"]) for r in results)}')
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'已保存到: {args.output}')

if __name__ == '__main__':
    main()
