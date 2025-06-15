# File: src/core/regex_extractor.py (Versi Baru yang Andal)

import re
from collections import OrderedDict

# Kamus kata kunci yang komprehensif untuk mendeteksi berbagai judul seksi.
SECTION_KEYWORDS = {
    'summary': r'summary|objective|profile|about me|professional profile',
    'skills': r'skills|technical skills|proficiencies|technologies|qualifications|additional information',
    'experience': r'experience|work history|employment history|professional experience',
    'education': r'education|education and training|academic background|academic qualifications',
    'accomplishments': r'accomplishments|highlights|awards|certifications|professional recognition'
}

def _parse_skills_from_block(content: str) -> str:
    """Fungsi internal untuk secara spesifik mem-parsing blok teks skills menjadi daftar yang rapi."""
    if not content:
        return ""
    
    # 1. Normalisasi semua jenis pemisah (baris baru, titik koma, bullet) menjadi '|'.
    normalized_str = re.sub(r'\s*[\n;*•●]\s*', '|', content)
    # 2. Ganti spasi ganda atau lebih (untuk skill dalam satu baris) menjadi '|'.
    normalized_str = re.sub(r'\s{2,}', '|', normalized_str)
    
    # 3. Pisahkan, bersihkan, dan buang item kosong/terlalu pendek.
    skills_list = [skill.strip(' .,') for skill in normalized_str.split('|') if len(skill.strip()) > 2]
    
    # 4. Hilangkan duplikat sambil menjaga urutan.
    unique_skills = list(OrderedDict.fromkeys(skills_list))
    
    return '\n'.join(unique_skills)

def extract_all_sections(text: str) -> dict:
    """
    Fungsi utama yang dipanggil dari luar. Mengekstrak semua seksi dari teks CV.
    """
    # Inisialisasi hasil dengan nilai default.
    final_sections = {
        'summary': 'Tidak dapat menemukan bagian Summary.',
        'skills': 'Tidak dapat menemukan bagian Skills.',
        'experience': 'Tidak dapat menemukan bagian Experience.',
        'education': 'Tidak dapat menemukan bagian Education.'
    }

    if not text or not isinstance(text, str):
        return final_sections
        
    # Pra-pembersihan teks mentah dari artefak PDF.
    text = text.replace('ï¼', ':').replace('â€', '').replace('Â', '')

    # 1. Temukan semua posisi judul seksi.
    all_kw_pattern = '|'.join(v for v in SECTION_KEYWORDS.values())
    title_pattern = re.compile(fr'^\s*({all_kw_pattern})\b\s*:?', re.IGNORECASE | re.MULTILINE)

    title_matches = []
    for match in title_pattern.finditer(text):
        title_str = match.group(1).lower()
        for name, pattern in SECTION_KEYWORDS.items():
            if re.fullmatch(pattern, title_str, re.IGNORECASE):
                title_matches.append({'name': name, 'start': match.start(), 'end': match.end()})
                break
    
    if not title_matches:
        return final_sections

    # 2. Ekstrak konten mentah berdasarkan posisi judul.
    raw_sections = OrderedDict()
    for i, section in enumerate(title_matches):
        content_start = section['end']
        content_end = title_matches[i+1]['start'] if i + 1 < len(title_matches) else len(text)
        content = text[content_start:content_end].strip()
        
        # Gabungkan konten jika nama seksi sama (misal, 'skills' dari 'qualifications').
        raw_sections[section['name']] = raw_sections.get(section['name'], "") + "\n" + content

    # 3. Lakukan pembersihan dan parsing akhir untuk setiap seksi.
    skills_content_to_parse = []
    for name, content in raw_sections.items():
        if name in ['skills', 'accomplishments']:
            skills_content_to_parse.append(content)
        elif name in final_sections:
            final_sections[name] = re.sub(r'\s+', ' ', content).strip() # Pembersihan dasar untuk paragraf

    # Parsing khusus untuk gabungan semua skills.
    if skills_content_to_parse:
        final_sections['skills'] = _parse_skills_from_block('\n'.join(skills_content_to_parse))
    
    return final_sections