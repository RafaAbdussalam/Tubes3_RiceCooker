# File: src/core/regex_extractor.py

import re
from collections import OrderedDict

# Definisi section keywords tetap sama
SECTION_KEYWORDS = {
    'summary': r'summary|objective|profile|about me|professional summary',
    'experience': r'experience|work history|employment history|professional experience|work experience',
    'education': r'education|academic background|education and training',
    'skills': r'skills|highlights|qualifications|technical skills|proficiencies|technologies',
    'accomplishments': r'accomplishments|awards|professional recognition',
    'boundary': r'affiliations|interests|certifications'
}

def _clean_text_block(text: str) -> str:
    """General utility to clean a block of text by normalizing whitespace."""
    if not text:
        return ""
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text.strip()

def _parse_skills_section_final(text: str) -> str:
    """
    Final version of the skills parser with intelligent handling of parentheses.
    It protects parenthetical blocks from being split by commas.
    """
    if not text:
        return ""

    all_skills = []
    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for the "Category: description" format
        category_match = re.match(r'^([\w\s-]+):\s*(.*)', line)
        if category_match:
            category, description = category_match.groups()
            all_skills.append(category.strip())
            
            # --- START: PERBAIKAN LOGIKA TANDA KURUNG ---
            
            # 1. Simpan semua blok dalam tanda kurung dan ganti dengan placeholder
            paren_blocks = re.findall(r'\(.*?\)', description)
            # Ganti blok dalam kurung dengan placeholder unik
            for i, block in enumerate(paren_blocks):
                description = description.replace(block, f'__PAREN_BLOCK_{i}__', 1)

            # 2. Sekarang aman untuk memisahkan berdasarkan koma
            # Split by comma or 'and'
            sub_skills_split = re.split(r',\s*|\s+and\s+', description)
            
            # 3. Gabungkan kembali placeholder dengan isinya
            restored_skills = []
            for skill_part in sub_skills_split:
                # Kembalikan blok tanda kurung ke tempatnya
                for i, block in enumerate(paren_blocks):
                    skill_part = skill_part.replace(f'__PAREN_BLOCK_{i}__', block)
                restored_skills.append(skill_part.strip())

            all_skills.extend([s for s in restored_skills if s])
            # --- END: PERBAIKAN LOGIKA TANDA KURUNG ---

        else:
            # Handle simple lists (comma-separated or bulleted)
            line = re.sub(r'[*•●;]', ',', line)
            sub_skills = line.split(',')
            all_skills.extend([skill.strip() for skill in sub_skills if skill.strip()])

    # Clean up the final list
    cleaned_skills = [skill.strip(' .,') for skill in all_skills if len(skill.strip(' .,')) > 1]
    unique_skills = list(OrderedDict.fromkeys(cleaned_skills))
    
    return '\n'.join(unique_skills)

def _format_structured_section(text: str) -> str:
    """Formats 'Experience' or 'Education' sections by separating distinct entries with double newlines."""
    if not text:
        return ""
    
    entry_start_pattern = re.compile(
        r'^\s*(\d+\.\s*|'
        r'[A-Za-z]+\s+\d{4}\s+to\s+[A-Za-z]+\s+\d{4}|'
        r'\d{2}/\d{4}\s+to\s+\d{2}/\d{4}|'
        r'Associate|Bachelor|Master|High School Diploma)',
        re.IGNORECASE
    )
    text_with_separators = entry_start_pattern.sub(r'<<ENTRY_BREAK>>\1', text)
    entries = text_with_separators.split('<<ENTRY_BREAK>>')
    cleaned_entries = [re.sub(r'\s+', ' ', entry.strip()) for entry in entries if entry.strip()]
    
    return '\n\n'.join(cleaned_entries)

def extract_all_sections(text: str) -> dict:
    """Main function to extract all key sections from a CV's text content."""
    final_sections = {
        'summary': 'Summary section not found.',
        'skills': 'Skills section not found.',
        'experience': 'Experience section not found.',
        'education': 'Education section not found.'
    }

    if not text or not isinstance(text, str):
        return final_sections
        
    text = text.replace('ï¼', ':').replace('â€', '-').replace('Â', '')

    all_keywords_pattern = '|'.join(val for val in SECTION_KEYWORDS.values())
    title_pattern = re.compile(fr'^\s*({all_keywords_pattern})\b\s*:?', re.IGNORECASE | re.MULTILINE)

    matches = []
    for match in title_pattern.finditer(text):
        title_text = match.group(1).lower()
        for section_name, pattern in SECTION_KEYWORDS.items():
            if re.fullmatch(pattern, title_text, re.IGNORECASE):
                matches.append({'name': section_name, 'start': match.start(), 'end': match.end()})
                break
    
    if not matches:
        return final_sections

    raw_sections = {name: [] for name in SECTION_KEYWORDS.keys()}
    for i, match in enumerate(matches):
        section_name = match['name']
        content_start = match['end']
        content_end = matches[i + 1]['start'] if i + 1 < len(matches) else len(text)
        
        content = text[content_start:content_end].strip()
        if content and section_name != 'boundary':
            raw_sections[section_name].append(content)

    if raw_sections['summary']:
        final_sections['summary'] = _clean_text_block('\n'.join(raw_sections['summary']))
        
    if raw_sections['skills'] or raw_sections['accomplishments']:
        full_skills_text = '\n'.join(raw_sections.get('skills', [])) + '\n' + '\n'.join(raw_sections.get('accomplishments', []))
        # Menggunakan fungsi parser yang sudah final
        final_sections['skills'] = _parse_skills_section_final(full_skills_text)
        
    if raw_sections['experience']:
        final_sections['experience'] = _format_structured_section('\n'.join(raw_sections['experience']))

    if raw_sections['education']:
        final_sections['education'] = _format_structured_section('\n'.join(raw_sections['education']))
            
    return final_sections