# File: src/core/regex_extractor.py
# PERBAIKAN: Logika parse_education dirombak total untuk menangani format kompleks.

import re
from collections import OrderedDict

SECTION_KEYWORDS = {
    'summary': r'summary|profile|objective|about me|professional summary',
    'skills': r'skills|highlights|technical skills|core competencies|expertise|proficiencies',
    'experience': r'experience|work experience|employment history|professional experience|work history|professional background|work|employment',
    'education': r'education|academic background|qualifications|education and training|academic history',
    'boundary': r'accomplishments|affiliations|interests|certifications|languages|awards|projects|publications|references'
}

def clean_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' \n', '\n', text)
    text = re.sub(r'\n ', '\n', text)
    text = re.sub(r'^\s*[•\-\*]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()

def extract_raw_sections(text: str) -> dict:
    cleaned_text = clean_text(text)
    all_kw_pattern = '|'.join(SECTION_KEYWORDS.values())
    title_pattern = re.compile(fr'^\s*({all_kw_pattern})\b\s*:?', re.IGNORECASE | re.MULTILINE)
    matches = list(title_pattern.finditer(cleaned_text))
    sections = {}
    for i, match in enumerate(matches):
        title_text = match.group(1).lower()
        section_name = next((name for name, pattern in SECTION_KEYWORDS.items() if re.fullmatch(pattern, title_text, re.IGNORECASE)), None)
        if section_name and section_name != 'boundary':
            content_start = match.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
            content_block = cleaned_text[content_start:content_end].strip()
            if section_name not in sections: sections[section_name] = []
            sections[section_name].append(content_block)
    return sections

def parse_skills(text_blocks: list) -> list:
    if not text_blocks: return []
    full_text = '\n'.join(text_blocks)
    processed_text = re.sub(r'\n(?![A-Z•*-])', ' ', full_text)
    all_skills = []
    lines = processed_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        if ':' in line:
            all_skills.append(re.sub(r'\s+', ' ', line).strip())
        else:
            sub_skills = re.split(r',\s*', line)
            all_skills.extend([skill.strip() for skill in sub_skills if skill.strip()])
    cleaned_skills = [skill.strip(' .,') for skill in all_skills if len(skill.strip(' .,')) > 1]
    return list(OrderedDict.fromkeys(cleaned_skills))

def parse_experience(text: str) -> list:
    if not text: return []
    experiences = []
    current_experience = None
    date_pattern = re.compile(
        r'((?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4})\s*to\s*(?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4}|Present|Current))',
        re.IGNORECASE
    )
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        date_match = date_pattern.search(line)
        if date_match:
            if current_experience:
                current_experience['description'] = '\n'.join(current_experience['description']).strip()
                experiences.append(current_experience)
            date_range = date_match.group(1).strip()
            company = line[:date_match.start()].strip()
            position = line[date_match.end():].strip()
            current_experience = {
                'date_range': date_range,
                'company': company.replace('Company Name', '').strip(' ,'),
                'position': position.strip(' ,'),
                'description': []
            }
        elif current_experience:
            current_experience['description'].append(line)
    if current_experience:
        current_experience['description'] = '\n'.join(current_experience['description']).strip()
        experiences.append(current_experience)
    return experiences

def parse_education(text: str) -> list:
    """
    Parser pendidikan yang ditulis ulang untuk menangani format kompleks dan beragam.
    """
    if not text:
        return []

    # Daftar kata kunci untuk membantu identifikasi
    degree_keywords = ['Associate', 'Associates', 'Bachelors', 'Certificate', 'Diploma']
    institution_keywords = ['College', 'School', 'University']
    
    parsed_entries = []
    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        year, degree, institution, description = 'N/A', 'N/A', 'N/A', ''

        # 1. Cari tahun terlebih dahulu
        year_match = re.search(r'\b((19|20)\d{2})\b', line)
        if year_match:
            year = year_match.group(0)

        # 2. Cari gelar & institusi berdasarkan kata kunci
        found_institution = ""
        for keyword in institution_keywords:
            # Cari institusi yang mengandung keyword, contoh "Northern Maine Community College"
            match = re.search(fr'([A-Za-z\s,]*{keyword}[A-Za-z\s,]*)', line, re.IGNORECASE)
            if match:
                found_institution = match.group(1).strip()
                break
        
        found_degree = ""
        for keyword in degree_keywords:
            # Cari gelar yang mengandung keyword, contoh "Associate: Accounting"
            match = re.search(fr'({keyword}[A-Za-z\s:]*)', line, re.IGNORECASE)
            if match:
                found_degree = match.group(1).strip()
                break

        # 3. Tentukan nilai akhir berdasarkan apa yang ditemukan
        if found_institution and found_degree:
            institution = found_institution
            degree = found_degree
        elif found_institution: # Hanya institusi ditemukan
            institution = found_institution
            # Sisa teks dianggap sebagai gelar/deskripsi
            degree = line.replace(institution, '').replace(year, '').strip(' :,')
        elif found_degree: # Hanya gelar ditemukan
            degree = found_degree
            # Sisa teks dianggap sebagai institusi
            institution = line.replace(degree, '').replace(year, '').strip(' :,')
        else: # Tidak ada keyword yang cocok, anggap sebagai deskripsi
            degree = "Informasi Tambahan / Kursus Profesional"
            description = line

        entry = {'year': year, 'degree': degree, 'institution': institution}
        if description:
            entry['description'] = description
        
        parsed_entries.append(entry)
            
    return parsed_entries


def extract_all_sections(text: str) -> dict:
    sections = extract_raw_sections(text)
    skills_blocks = sections.get('skills', [])
    skills_list = parse_skills(skills_blocks)
    experience_text = '\n'.join(sections.get('experience', []))
    experience_list = parse_experience(experience_text)
    education_text = '\n'.join(sections.get('education', []))
    education_list = parse_education(education_text)
    summary_text = '\n'.join(sections.get('summary', []))
    return {
        'summary': clean_text(summary_text).replace("\n", " ") or 'N/A',
        'skills': skills_list,
        'experience': experience_list,
        'education': education_list or []
    }