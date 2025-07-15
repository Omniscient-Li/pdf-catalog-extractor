from pdf_catalog_extractor.extractor import extract_components_from_text

def test_extract_components():
    text = '''
    1. Lift mechanism set
    Cabinet height KH (mm): 300–389
    Part no.: 2212210
    '''
    components = extract_components_from_text(text)
    assert len(components) == 1
    assert components[0]['name'].startswith('1. Lift mechanism')
    assert 'Cabinet height KH (mm)' in components[0]['params']
    assert '2212210' in components[0]['part_numbers']
    print('test_extract_components passed')

if __name__ == '__main__':
    test_extract_components() 