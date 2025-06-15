# File: src/core/regex_extractor.py
# Perbaikan: Mengganti nama fungsi utama menjadi extract_all_sections untuk mengatasi ImportError.

import re
from collections import OrderedDict

# Definisi header dari setiap seksi yang akan dicari
SECTION_KEYWORDS = {
    'summary': r'summary|profile|objective|about me|professional summary',
    'skills': r'skills|highlights|technical skills|core competencies|expertise',
    'experience': r'experience|work experience|employment history|professional experience',
    'education': r'education|academic background|qualifications',
    'boundary': r'accomplishments|affiliations|interests|certifications|languages'
}

def clean_text(text: str) -> str:
    """Membersihkan teks dari hasil ekstraksi PDF/OCR yang kotor."""
    if not text:
        return ""
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
    """Mengekstrak blok teks mentah untuk setiap seksi berdasarkan keywords."""
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
            sections[section_name] = cleaned_text[content_start:content_end].strip()
    return sections

def parse_skills(text: str) -> list:
    """Mem-parsing blok teks skills menjadi daftar yang bersih dan unik."""
    if not text:
        return []
    text = re.sub(r'[\n;*•●,]', '|', text)
    text = re.sub(r'\|+', '|', text)
    skills = [skill.strip() for skill in text.split('|') if 2 < len(skill.strip()) < 50]
    return list(OrderedDict.fromkeys(skills))

def parse_experience(text: str) -> list:
    """Mem-parsing blok pengalaman kerja dengan metode yang lebih cerdas dan fleksibel."""
    if not text:
        return []
    experiences = []
    entry_pattern = r'((?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4})\s*[-–to]+\s*(?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4}|Present|Current))'
    entries = re.split(fr'(?={entry_pattern})', text, flags=re.IGNORECASE)
    for entry_block in entries:
        entry_block = entry_block.strip()
        if not entry_block:
            continue
        lines = entry_block.split('\n')
        date_range_match = re.match(entry_pattern, lines[0], re.IGNORECASE)
        date_range = date_range_match.group(1).strip() if date_range_match else "N/A"
        first_line_content = re.sub(entry_pattern, '', lines[0], count=1, flags=re.IGNORECASE).strip()
        position, company, description = "N/A", "N/A", ""
        remaining_lines = [first_line_content] + lines[1:] if first_line_content else lines[1:]
        content_lines = [line.strip() for line in remaining_lines if line.strip()]
        if not content_lines:
            continue
        position = content_lines[0]
        if len(content_lines) > 1:
            company = content_lines[1]
            description_start_index = 2
        else:
            description_start_index = 1
        description = '\n'.join(content_lines[description_start_index:]).strip()
        if position != "N/A" or company != "N/A":
            experiences.append({'date_range': date_range, 'position': position, 'company': company, 'description': description})
    return experiences

def parse_education(text: str) -> list:
    """Mem-parsing blok pendidikan dengan metode yang andal."""
    if not text:
        return []
    entry_pattern = re.compile(r'^\s*(Bachelor|Master|Doctor|Associate|High School Diploma|(?:\b(19|20)\d{2}\b))', re.IGNORECASE | re.MULTILINE)
    entry_starts = list(entry_pattern.finditer(text))
    parsed_entries = []
    for i, start_match in enumerate(entry_starts):
        start_pos = start_match.start()
        end_pos = entry_starts[i + 1].start() if i + 1 < len(entry_starts) else len(text)
        entry_block = text[start_pos:end_pos].strip()
        year, degree, institution = 'N/A', 'N/A', 'N/A'
        year_match = re.search(r'\b(19|20)\d{2}\b', entry_block)
        if year_match:
            year = year_match.group(0)
            entry_block = entry_block.replace(year, "").strip()
        lines = [line.strip() for line in entry_block.split('\n') if line.strip()]
        if lines:
            if ":" in lines[0]:
                parts = lines[0].split(":", 1)
                degree, institution = parts[0].strip(), parts[1].strip()
            else:
                degree, institution = lines[0], ' '.join(lines[1:])
        parsed_entry = {'year': year, 'degree': degree.replace(":", "").strip(), 'institution': institution.strip()}
        if parsed_entry not in parsed_entries:
            parsed_entries.append(parsed_entry)
    return parsed_entries

# --- PERUBAHAN DI SINI ---
# Nama fungsi diubah dari 'extract_all_info' menjadi 'extract_all_sections'
def extract_all_sections(text: str) -> dict:
    """
    Fungsi utama untuk mengekstrak semua informasi dari teks CV.
    Nama fungsi ini disesuaikan agar bisa diimpor oleh file UI Anda.
    """
    sections = extract_raw_sections(text)
    summary_text = sections.get('summary', '')
    skills_list = parse_skills(sections.get('skills', ''))
    experience_list = parse_experience(sections.get('experience', ''))
    education_list = parse_education(sections.get('education', ''))

    return {
        'summary': clean_text(summary_text).replace("\n", " ") or 'N/A',
        'skills': ', '.join(skills_list) if skills_list else 'N/A',
        'experience': experience_list or [],
        'education': education_list or []
    }