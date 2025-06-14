# File: src/core/regex_extractor.py (Versi Perbaikan Final v2)

import re
from collections import OrderedDict

# Daftar semua kemungkinan sinonim untuk setiap seksi
SECTION_KEYWORDS = {
    'summary': r'summary|objective|profile|about me',
    'skills': r'skills|technical skills|proficiencies|technologies',
    'experience': r'experience|work history|employment history|professional experience',
    'education': r'education|academic background|academic qualifications',
    'highlights': r'highlights',
    'accomplishments': r'accomplishments',
    'projects': r'projects|personal projects'
}

def extract_all_sections(text: str) -> dict:
    """
    Mengekstrak semua seksi dari teks CV dengan pendekatan yang lebih andal.
    1. Cari semua judul seksi yang diketahui dan lokasinya.
    2. Urutkan berdasarkan lokasi kemunculannya.
    3. Ekstrak konten yang berada di antara setiap pasangan judul.
    """
    all_keywords_pattern = '|'.join(v for v in SECTION_KEYWORDS.values())
    section_title_pattern = re.compile(fr'^\s*({all_keywords_pattern})\b', re.IGNORECASE | re.MULTILINE)

    found_sections = []
    for match in section_title_pattern.finditer(text):
        matched_title = match.group(1).lower()
        for section_name, keywords_pattern in SECTION_KEYWORDS.items():
            if re.search(fr'\b({keywords_pattern})\b', matched_title, re.IGNORECASE):
                # Simpan informasi yang lebih lengkap: awal judul dan awal konten
                found_sections.append({
                    'name': section_name,
                    'title_start': match.start(), # Posisi awal dari judul (misal, 'S' dari 'Skills')
                    'content_start': match.end()  # Posisi setelah judul
                })
                break
    
    if not found_sections:
        return {}

    extracted_content = OrderedDict()
    for i, section in enumerate(found_sections):
        content_start = section['content_start']
        
        # --- LOGIKA PERBAIKAN UTAMA ADA DI SINI ---
        # Posisi akhir konten adalah posisi awal dari judul seksi BERIKUTNYA.
        # Ini jauh lebih andal daripada mencari ulang.
        content_end = len(text) # Default untuk seksi terakhir
        if i + 1 < len(found_sections):
            content_end = found_sections[i+1]['title_start']
        
        content = text[content_start:content_end].strip()
        
        # Membersihkan bullet points dan karakter aneh
        content = re.sub(r'^\s*[•*-]\s*', '', content, flags=re.MULTILINE)
        content = content.replace('ï¼', ':')
        
        # Jangan tambahkan seksi jika kontennya kosong
        if content:
            extracted_content[section['name']] = content

    return dict(extracted_content)

# Wrapper functions di bawah ini tidak perlu diubah, mereka akan otomatis menggunakan logika baru.

def extract_skills(text: str) -> str:
    sections = extract_all_sections(text)
    skills_content = []
    for key in ['skills', 'highlights', 'accomplishments']:
        if key in sections:
            skills_content.append(sections[key])
    return '\n---\n'.join(skills_content) if skills_content else "Tidak dapat menemukan bagian Skills."

def extract_experience(text: str) -> str:
    sections = extract_all_sections(text)
    return sections.get('experience', "Tidak dapat menemukan bagian Experience.")

def extract_education(text: str) -> str:
    sections = extract_all_sections(text)
    return sections.get('education', "Tidak dapat menemukan bagian Education.")