# PDF Catalog Extractor

自动化解析产品目录PDF，生成结构化JSON知识库。

## 目录结构
- pdf_catalog_extractor/  # 核心代码
- data/                  # 原始PDF
- output/                # 结构化输出
- scripts/               # 入口脚本
- tests/                 # 单元测试

## 安装依赖
pip install -r requirements.txt

## 使用方法
python scripts/run_extract.py --pdf data/Catalogue.pdf --output output/products.json

## 输出格式
详见 output/products.json 示例

## 贡献与测试
欢迎提交PR和建议。 