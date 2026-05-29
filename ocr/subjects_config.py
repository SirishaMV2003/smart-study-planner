"""
Predefined Subject Codes Configuration
Maps all subject codes to their names and metadata
"""

SUBJECTS_MAP = {
    # Exact matches with full names
    '25MT21': 'MATHEMATICS',
    '25CHC22': 'CHEMISTRY',
    '25CED23': 'CIVIL ENGINEERING DESIGN',
    '25PL25': 'PYTHON',
    '25ICO27': 'INDIAN CONSTITUTION',
    '25ENL26': 'ENGLISH',
    '25PHC22': 'PHYSICS',
    '25ES24': 'ENVIRONMENTAL SCIENCE',
    '25ET25': 'ENVIRONMENTAL TECHNOLOGY',
}

# Pattern variations (handles * and other characters)
SUBJECT_PATTERNS = {
    'MT': 'MATHEMATICS',
    'CHC': 'CHEMISTRY',
    'CED': 'CIVIL ENGINEERING DESIGN',
    'PL': 'PYTHON',
    'ICO': 'INDIAN CONSTITUTION',
    'ENL': 'ENGLISH',
    'PHC': 'PHYSICS',
    'ES': 'ENVIRONMENTAL SCIENCE',
    'ET': 'ENVIRONMENTAL TECHNOLOGY',
    'SKK': 'SANSKRIT',
    'BKK': 'PUNJABI',
}


def get_subject_name(code):
    """
    Extract subject name from code
    
    Args:
        code: Subject code (e.g., '25MT21', '25PHC22')
        
    Returns:
        Subject name or None if not found
    """
    if not code:
        return None
    
    # Clean code: remove special characters
    clean_code = ''.join(c for c in code if c.isalnum())
    
    # Check exact match first
    if clean_code in SUBJECTS_MAP:
        return SUBJECTS_MAP[clean_code]
    
    # Check pattern match
    for pattern, name in SUBJECT_PATTERNS.items():
        if pattern in clean_code.upper():
            return name
    
    return None


def extract_subject_codes_from_text(text):
    """
    Extract all subject codes from text
    Looks for pattern: 25XXXXX
    """
    import re
    pattern = r'25[A-Z]{2,3}[\*]?[\d]{1,2}[*/]?'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return list(set(matches))


def get_all_defined_subjects():
    """Get all defined subjects"""
    return SUBJECTS_MAP.copy()
