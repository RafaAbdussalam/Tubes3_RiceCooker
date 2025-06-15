# File: src/core/regex_extractor.py (Dengan Perbaikan Logika Experience)

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
    normalized_str = re.sub(r'\s*[\n;*•●]\s*', '|', content)
    normalized_str = re.sub(r'\s{2,}', '|', normalized_str)
    skills_list = [skill.strip(' .,') for skill in normalized_str.split('|') if len(skill.strip()) > 2]
    unique_skills = list(OrderedDict.fromkeys(skills_list))
    return '\n'.join(unique_skills)

def _clean_paragraph_section(content: str) -> str:
    """Fungsi pembersih umum untuk seksi berbasis paragraf seperti Experience atau Education."""
    if not content:
        return ""
    cleaned = re.sub(r'^\s*[•*-]\s*', '', content, flags=re.MULTILINE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def _format_job_history(content: str) -> str:
    """Fungsi untuk memformat job history menjadi format yang lebih terstruktur."""
    if not content:
        return ""
    
    # Pisahkan setiap entri pekerjaan berdasarkan nomor atau tanggal
    entries = re.split(r'(?:\d+\.\s*|\d{4}\s*\n)', content)
    formatted_entries = []
    
    for entry in entries:
        if not entry.strip():
            continue
            
        # Coba ekstrak tanggal dengan pattern yang lebih komprehensif
        date_pattern = r'(?:\d{2}/\d{4}\s*to\s*\d{2}/\d{4}|\d{4})'
        dates = re.findall(date_pattern, entry)
        
        # Pisahkan judul dan deskripsi
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            continue
            
        # Ekstrak judul (biasanya baris pertama)
        title = lines[0]
        
        # Ekstrak lokasi/company (biasanya baris kedua)
        location = ""
        if len(lines) > 1 and not re.search(date_pattern, lines[1]):
            location = lines[1]
            
        # Gabungkan sisa baris sebagai deskripsi
        description = '\n'.join(lines[2:]) if len(lines) > 2 else ""
        
        # Format entri
        formatted_entry = f"{title}\n"
        if location:
            formatted_entry += f"{location}\n"
        if dates:
            formatted_entry += f"{dates[0]}\n"
        if description:
            formatted_entry += f"{description}\n"
        
        formatted_entries.append(formatted_entry)
    
    return '\n\n'.join(formatted_entries)

def _format_education(content: str) -> str:
    """Fungsi untuk memformat education menjadi format yang lebih terstruktur."""
    if not content:
        return ""
    
    # Pisahkan setiap entri pendidikan berdasarkan tahun atau gelar
    entries = re.split(r'(?:\d{4}\s*\n|Bachelor|Master|Doctor|High School)', content)
    formatted_entries = []
    
    for entry in entries:
        if not entry.strip():
            continue
            
        # Coba ekstrak tanggal dengan pattern yang lebih komprehensif
        date_pattern = r'(?:\d{4})'
        dates = re.findall(date_pattern, entry)
        
        # Pisahkan judul dan deskripsi
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            continue
            
        # Ekstrak judul (biasanya baris pertama)
        title = lines[0]
        
        # Ekstrak institusi (biasanya baris kedua)
        institution = ""
        if len(lines) > 1 and not re.search(date_pattern, lines[1]):
            institution = lines[1]
            
        # Gabungkan sisa baris sebagai deskripsi
        description = '\n'.join(lines[2:]) if len(lines) > 2 else ""
        
        # Format entri
        formatted_entry = f"{title}\n"
        if institution:
            formatted_entry += f"{institution}\n"
        if dates:
            formatted_entry += f"{dates[0]}\n"
        if description:
            formatted_entry += f"{description}\n"
        
        formatted_entries.append(formatted_entry)
    
    return '\n\n'.join(formatted_entries)

def extract_all_sections(text: str) -> dict:
    """
    Fungsi utama yang dipanggil dari luar. Mengekstrak semua seksi dari teks CV.
    """
    final_sections = {
        'summary': 'Tidak dapat menemukan bagian Summary.',
        'skills': 'Tidak dapat menemukan bagian Skills.',
        'experience': 'Tidak dapat menemukan bagian Experience.',
        'education': 'Tidak dapat menemukan bagian Education.'
    }
    if not text or not isinstance(text, str):
        return final_sections
        
    text = text.replace('ï¼', ':').replace('â€', '').replace('Â', '')

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

    raw_sections = OrderedDict()
    for i, section in enumerate(title_matches):
        content_start = section['end']
        content_end = title_matches[i+1]['start'] if i + 1 < len(title_matches) else len(text)
        content = text[content_start:content_end].strip()
        raw_sections[section['name']] = raw_sections.get(section['name'], "") + "\n" + content

    # --- PERBAIKAN LOGIKA UTAMA ADA DI SINI ---
    skills_content_to_parse = []
    for name, content in raw_sections.items():
        if name in ['skills', 'accomplishments']:
            skills_content_to_parse.append(content)
        elif name == 'experience':
            final_sections[name] = _format_job_history(content)
        elif name == 'education':
            final_sections[name] = _format_education(content)
        elif name == 'summary':
            final_sections[name] = _clean_paragraph_section(content)

    if skills_content_to_parse:
        final_sections['skills'] = _parse_skills_from_block('\n'.join(skills_content_to_parse))
    
    return final_sections