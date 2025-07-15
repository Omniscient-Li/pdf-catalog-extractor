import argparse
import os
import json
from pdf_catalog_extractor.extractor import extract_products_from_pdf

def main():
    parser = argparse.ArgumentParser(description='PDF Catalog Extractor')
    parser.add_argument('--pdf', type=str, required=True, help='PDF file path')
    parser.add_argument('--output', type=str, required=True, help='Output JSON file')
    parser.add_argument('--start_page', type=int, default=1, help='Start page (1-based)')
    parser.add_argument('--end_page', type=int, default=None, help='End page (1-based, inclusive)')
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"PDF文件不存在: {args.pdf}")
        return

    # 计算结束页
    import fitz
    doc = fitz.open(args.pdf)
    total_pages = len(doc)
    doc.close()
    end_page = args.end_page if args.end_page else total_pages

    results = extract_products_from_pdf(args.pdf, args.start_page - 1, end_page - 1)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'提取完成，结果已保存到: {args.output}')

if __name__ == '__main__':
    main() 