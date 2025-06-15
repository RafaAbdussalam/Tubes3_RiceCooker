# File: src/core/regex_extractor.py (Versi Perbaikan Final v3)

import re
from collections import OrderedDict
# Menambahkan 'qualifications', 'professional profile', 'leadership', 'activities and honors', dll.
# untuk mencakup variasi dari CV yang diberikan.
SECTION_KEYWORDS = {
    'summary': r'summary|objective|profile|about me|professional profile|career focus',
    'skills': r'skills|technical skills|proficiencies|technologies|qualifications',
    'experience': r'experience|work history|employment history|professional experience',
    'education': r'education|education and training|academic background|academic qualifications',
    'highlights': r'highlights',
    'accomplishments': r'accomplishments|leadership|activities and honors|awards and professional recognition',
    'projects': r'projects|personal projects|projects at work'
}

def extract_all_sections(text: str) -> dict:
    """
    Mengekstrak semua seksi dari teks CV dengan pendekatan yang lebih andal.
    1. Cari semua judul seksi yang diketahui dan lokasinya.
    2. Urutkan berdasarkan lokasi kemunculannya.
    3. Ekstrak konten yang berada di antara setiap pasangan judul.
    """
    all_keywords_pattern = '|'.join(v for v in SECTION_KEYWORDS.values())
    # Pola ini sekarang lebih fleksibel untuk menangani judul yang mungkin diikuti oleh titik dua
    section_title_pattern = re.compile(fr'^\s*({all_keywords_pattern})\b\s*:?', re.IGNORECASE | re.MULTILINE)

    found_sections = []
    for match in section_title_pattern.finditer(text):
        matched_title = match.group(1).lower()
        for section_name, keywords_pattern in SECTION_KEYWORDS.items():
            if re.search(fr'\b({keywords_pattern})\b', matched_title, re.IGNORECASE):
                found_sections.append({
                    'name': section_name,
                    'title_start': match.start(),
                    'content_start': match.end()
                })
                break
    
    if not found_sections:
        return {}

    extracted_content = OrderedDict()
    for i, section in enumerate(found_sections):
        content_start = section['content_start']
        
        content_end = len(text)
        if i + 1 < len(found_sections):
            content_end = found_sections[i+1]['title_start']
        
        content = text[content_start:content_end].strip()
        
        # Menghapus bullet points, karakter aneh, dan spasi berlebih
        content = re.sub(r'^\s*[•*-]\s*', '', content, flags=re.MULTILINE)
        content = content.replace('ï¼', ':')
        content = content.replace('â€', '') # Menghapus karakter artefak
        content = content.replace('Â', '')   # Menghapus karakter artefak
        content = re.sub(r'\s{2,}', ' ', content) # Mengganti spasi ganda dengan tunggal
        
        if content:
            extracted_content[section['name']] = content

    return dict(extracted_content)

def extract_skills(text: str) -> str:
    """
    Fungsi yang diperbaiki: Mengekstrak, membersihkan, dan menstandarkan format skills.
    """
    sections = extract_all_sections(text)
    
    # Mengambil konten mentah dari seksi-seksi yang relevan
    raw_content_list = []
    for key in ['skills', 'highlights', 'accomplishments']:
        if key in sections and sections[key]:
            raw_content_list.append(sections[key])
    
    if not raw_content_list:
        return "Tidak dapat menemukan bagian Skills, Highlights, atau Accomplishments."
    
    full_content_str = ' '.join(raw_content_list)

    # Menambahkan titik koma (;) ke dalam daftar pemisah [;,\n•*-]
    # Ini akan menggantikan setiap titik koma, koma, baris baru, atau bullet point dengan '|'
    normalized_str = re.sub(r'\s+and\s+|\s+etc\s*|[;,\n•*-]|A\b', '|', full_content_str, flags=re.IGNORECASE)
    
    # Pisahkan menjadi skill individual, bersihkan spasi, dan buang yang kosong
    skills_list = [skill.strip() for skill in normalized_str.split('|') if len(skill.strip()) > 1]
    
    # Menghilangkan duplikat sambil mempertahankan urutan
    unique_skills = list(OrderedDict.fromkeys(skills_list))
    
    # Kembalikan sebagai satu string yang dipisahkan oleh baris baru
    return '\n'.join(unique_skills)

def extract_experience(text: str) -> str:
    sections = extract_all_sections(text)
    return sections.get('experience', "Tidak dapat menemukan bagian Experience.")

def extract_education(text: str) -> str:
    sections = extract_all_sections(text)
    return sections.get('education', "Tidak dapat menemukan bagian Education.")