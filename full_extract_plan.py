#!/usr/bin/env python3
"""
完整的PDF提取计划
"""

def calculate_batches():
    """计算批次划分"""
    start_page = 16  # 第16页
    end_page = 736   # 第736页
    batch_size = 30  # 每批次30页
    
    total_pages = end_page - start_page + 1
    num_batches = (total_pages + batch_size - 1) // batch_size  # 向上取整
    
    print(f"PDF提取计划分析")
    print(f"=" * 50)
    print(f"起始页: 第{start_page}页")
    print(f"结束页: 第{end_page}页")
    print(f"总页数: {total_pages}页")
    print(f"每批次: {batch_size}页")
    print(f"总批次数: {num_batches}个批次")
    print(f"=" * 50)
    
    batches = []
    for i in range(num_batches):
        batch_start = start_page - 1 + (i * batch_size)  # 转换为0索引
        batch_end = min(start_page - 1 + ((i + 1) * batch_size) - 1, end_page - 1)
        
        actual_start = batch_start + 1  # 转换回1索引显示
        actual_end = batch_end + 1
        
        batches.append((batch_start, batch_end))
        
        print(f"批次 {i+1:2d}: 第{actual_start:3d}-{actual_end:3d}页 (共{actual_end-actual_start+1:2d}页)")
    
    print(f"=" * 50)
    print(f"预计总产品数: {num_batches * 30} 个 (基于之前每批次约30个产品)")
    print(f"预计处理时间: {num_batches * 2} 分钟 (基于之前每批次约2分钟)")
    print(f"预计总文件大小: {num_batches * 10} KB (基于之前每批次约10KB)")
    
    return batches

def generate_extract_script(batches):
    """生成完整的提取脚本"""
    script_content = '''#!/usr/bin/env python3
"""
完整的PDF产品信息提取脚本
从第16页到第736页，分25个批次处理
"""

import fitz  # PyMuPDF
import json
import os
import re
from typing import List, Dict, Any

def extract_text_from_pages(pdf_path: str, start_page: int, end_page: int) -> str:
    """从指定页码范围提取文本"""
    doc = fitz.open(pdf_path)
    all_text = ""
    
    for page_num in range(start_page, min(end_page + 1, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        all_text += f"\\n{text}"
    
    doc.close()
    return all_text

def clean_description(text: str) -> str:
    """清理描述文本"""
    # 移除页面导航路径
    text = re.sub(r'\\d+ 〉 [^〉]+〉 [^〉]+', '', text)
    # 移除目录标题
    text = re.sub(r'Catalogue 2024/2025', '', text)
    # 移除页面标记
    text = re.sub(r'--- 第 \\d+ 页 ---', '', text)
    # 移除多余空格
    text = re.sub(r'\\s+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[▬●○]', '', text)
    return text.strip()

def is_navigation_or_header(text: str) -> bool:
    """判断是否为导航或标题文本"""
    # 包含导航箭头的文本
    if '〉' in text:
        return True
    # 包含目录标题的文本
    if 'Catalogue 2024/2025' in text:
        return True
    # 包含页码的文本
    if re.search(r'第 \\d+ 页', text):
        return True
    # 过短的文本（可能是标题）
    if len(text.strip()) < 20:
        return True
    return False

def extract_product_description(text: str, product_name: str) -> str:
    """提取产品描述（改进版本）"""
    lines = text.split('\\n')
    description_lines = []
    
    # 查找包含产品名称的行
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 检查是否包含产品名称（完整匹配或部分匹配）
        if product_name in line or any(word in line for word in product_name.split()):
            # 获取产品名称行及其前后几行作为描述
            start = max(0, i - 1)
            end = min(len(lines), i + 2)
            
            for j in range(start, end):
                desc_line = lines[j].strip()
                if desc_line and len(desc_line) > 15:  # 过滤太短的行
                    # 跳过导航和标题文本
                    if is_navigation_or_header(desc_line):
                        continue
                    # 清理描述行
                    desc_line = clean_description(desc_line)
                    if desc_line and len(desc_line) > 10:
                        description_lines.append(desc_line)
    
    # 合并描述文本
    if description_lines:
        description = " ".join(description_lines)
        # 清理和截断
        description = re.sub(r'\\s+', ' ', description)  # 清理多余空格
        if len(description) > 150:
            description = description[:150] + "..."
        return description
    
    return "Product specifications and technical details"

def extract_products_from_text(text: str, start_page: int, end_page: int) -> List[Dict[str, Any]]:
    """从文本中提取产品信息（改进版本）"""
    products = []
    seen_names = set()  # 用于去重
    
    # 统一英文产品系列和类别映射
    product_series = {
        'AVENTOS': 'Lift Systems',
        'CLIP': 'Hinge Systems', 
        'LEGRABOX': 'Box Systems',
        'TANDEMBOX': 'Box Systems',
        'BLUMOTION': 'Hardware Components'
    }
    
    # 查找产品信息
    lines = text.split('\\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # 跳过导航和标题行
        if is_navigation_or_header(line):
            continue
        
        # 检测产品系列
        found_series = None
        for series_name in product_series.keys():
            if series_name in line:
                found_series = series_name
                break
        
        if found_series:
            # 提取产品名称
            product_name = line
            if len(product_name) > 100:
                product_name = product_name[:100]
            
            # 清理产品名称
            product_name = clean_description(product_name)
            
            # 去重检查
            if product_name in seen_names:
                continue
            seen_names.add(product_name)
            
            # 获取类别
            category = product_series[found_series]
            
            # 提取产品描述（使用产品名称而不是系列名称）
            description = extract_product_description(text, product_name)
            
            # 创建改进的产品对象
            product = {
                "name": product_name,
                "category": category,
                "description": description
            }
            
            products.append(product)
    
    return products

def process_batch(pdf_path: str, batch_num: int, start_page: int, end_page: int) -> Dict[str, Any]:
    """处理一个批次"""
    print(f"\\n=== 处理第 {batch_num} 批 ===")
    print(f"页码范围: 第 {start_page + 1} - {end_page + 1} 页")
    
    # 提取文本
    text = extract_text_from_pages(pdf_path, start_page, end_page)
    print(f"提取文本长度: {len(text):,} 字符")
    
    # 提取产品信息
    products = extract_products_from_text(text, start_page, end_page)
    
    # 创建改进的批次结果
    batch_result = {
        "batch_info": {
            "batch_number": batch_num,
            "start_page": start_page + 1,
            "end_page": end_page + 1,
            "total_pages": end_page - start_page + 1,
            "products_count": len(products)
        },
        "products": products
    }
    
    print(f"提取到 {len(products)} 个产品")
    
    return batch_result

def main():
    """主函数 - 完整PDF提取"""
    pdf_path = "Catalogue and technical manual 2024-2025.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    # 定义完整的批次（从第16页到第736页）
    batches = [
'''
    
    # 添加批次定义
    for i, (start_page, end_page) in enumerate(batches):
        script_content += f"        ({start_page}, {end_page}),   # 第{start_page+1}-{end_page+1}页\\n"
    
    script_content += '''    ]
    
    all_products = []
    
    # 循环处理所有批次
    for batch_num, (start_page, end_page) in enumerate(batches, 1):
        print(f"\\n{'='*50}")
        print(f"开始处理第 {batch_num} 批")
        print(f"{'='*50}")
        
        # 处理当前批次
        batch_result = process_batch(pdf_path, batch_num, start_page, end_page)
        all_products.extend(batch_result["products"])
        
        # 保存当前批次的JSON文件
        batch_filename = f"full_products_batch_{batch_num:02d}.json"
        with open(batch_filename, 'w', encoding='utf-8') as f:
            json.dump(batch_result, f, ensure_ascii=False, indent=2)
        
        print(f"第 {batch_num} 批结果已保存到: {batch_filename}")
    
    # 保存完整的合并结果
    combined_result = {
        "total_products": len(all_products),
        "products": all_products
    }
    
    # 保存合并结果
    combined_filename = "full_products_combined.json"
    with open(combined_filename, 'w', encoding='utf-8') as f:
        json.dump(combined_result, f, ensure_ascii=False, indent=2)
    
    print(f"\\n{'='*50}")
    print("完整PDF提取完成！")
    print(f"总共提取了 {len(all_products)} 个产品")
    print(f"合并结果已保存到: {combined_filename}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
'''
    
    # 保存完整提取脚本
    with open('full_extract_script.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\\n完整提取脚本已生成: full_extract_script.py")
    print(f"运行命令: python full_extract_script.py")

if __name__ == "__main__":
    batches = calculate_batches()
    generate_extract_script(batches) 