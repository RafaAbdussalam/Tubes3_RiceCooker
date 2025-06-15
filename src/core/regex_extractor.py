import re

# Daftar semua kemungkinan sinonim untuk setiap seksi
# Didefinisikan di satu tempat agar mudah dikelola
SECTION_KEYWORDS = {
    'skills': r'Skills',
    'summary': r'Summary|Objective|Profile',
    'experience': r'Experience|Work History|Employment History',
    'education': r'Education',
    'highlights': r'Highlights',
    'accomplishments': r'Accomplishments'
}

def extract_all_sections(text: str) -> dict:
    """
    Mengekstrak semua seksi dari teks CV menggunakan pendekatan terprogram.
    1. Cari semua judul seksi dan lokasinya.
    2. Urutkan berdasarkan lokasi.
    3. Ekstrak konten di antara setiap pasangan judul.
    """
    all_keywords = []
    for section_name, keywords in SECTION_KEYWORDS.items():
        all_keywords.append(keywords)
    
    # Gabungkan semua keyword menjadi satu pola regex untuk menemukan semua judul sekaligus
    combined_pattern = fr'^\s*({ "|".join(all_keywords) })'
    
    # Temukan semua judul dan posisinya
    found_sections = []
    for match in re.finditer(combined_pattern, text, re.MULTILINE | re.IGNORECASE):
        # Cari nama seksi yang cocok dari SECTION_KEYWORDS
        found_title = match.group(1).lower()
        section_name = ''
        for name, keywords in SECTION_KEYWORDS.items():
            if re.search(fr'\b({keywords})\b', found_title, re.IGNORECASE):
                section_name = name
                break
        
        if section_name:
            found_sections.append({
                'name': section_name,
                'start_index': match.start(),
                'end_index': match.end()
            })

    # Jika tidak ada seksi yang ditemukan, kembalikan dictionary kosong
    if not found_sections:
        return {}

    # Urutkan seksi berdasarkan indeks awal
    found_sections.sort(key=lambda x: x['start_index'])
    
    # Ekstrak konten untuk setiap seksi
    extracted_content = {}
    for i, section in enumerate(found_sections):
        content_start = section['end_index']
        
        # Tentukan akhir konten: awal seksi berikutnya atau akhir file
        content_end = len(text)
        if i + 1 < len(found_sections):
            content_end = found_sections[i+1]['start_index']
            
        content = text[content_start:content_end].strip()
        extracted_content[section['name']] = content

    return extracted_content

# Fungsi-fungsi di bawah ini sekarang menjadi lebih sederhana.
# Mereka hanya perlu mengambil data dari hasil extract_all_sections.

def extract_skills(text: str) -> str:
    sections = extract_all_sections(text)
    return sections.get('skills', '')

def extract_experience(text: str) -> str:
    sections = extract_all_sections(text)
    return sections.get('experience', '')

def extract_education(text: str) -> str:
    sections = extract_all_sections(text)
    return sections.get('education', '')