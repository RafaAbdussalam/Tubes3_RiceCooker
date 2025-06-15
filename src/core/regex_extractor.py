# File: src/core/regex_extractor.py
# Perbaikan: Logika penggabungan seksi dan parser skills yang lebih cerdas.

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
    """
    Mengekstrak blok teks mentah.
    PERBAIKAN: Sekarang menggunakan list untuk mengakomodasi beberapa seksi dengan nama sama (misal: skills dan highlights).
    """
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
            
            # Logika baru: Append ke list, jangan overwrite
            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(content_block)
            
    return sections

def parse_skills(text_blocks: list) -> list:
    """
    Fungsi parser skills dengan logika baru yang lebih andal.
    Mencoba menggabungkan baris yang terpotong sebelum mem-parsing.
    """
    if not text_blocks:
        return []

    full_text = '\n'.join(text_blocks)

    # --- LOGIKA BARU: PRE-PROCESSING UNTUK MENGGABUNGKAN BARIS ---
    # Ganti newline (\n) dengan spasi, KECUALI jika newline tersebut diikuti
    # oleh huruf kapital atau bullet point, yang menandakan item baru.
    # Ini adalah heuristik untuk menggabungkan frasa yang terpotong.
    # Regex (?![A-Z•*]) adalah negative lookahead.
    processed_text = re.sub(r'\n(?![A-Z•*-])', ' ', full_text)
    
    all_skills = []
    # Sekarang, pisahkan teks yang sudah lebih bersih berdasarkan baris baru yang tersisa.
    lines = processed_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Jika baris mengandung ':', anggap sebagai satu item utuh.
        if ':' in line:
            # Bersihkan spasi berlebih yang mungkin muncul dari proses join
            all_skills.append(re.sub(r'\s+', ' ', line).strip())
        else:
            # Jika tidak, baru pecah berdasarkan koma.
            sub_skills = re.split(r',\s*', line)
            all_skills.extend([skill.strip() for skill in sub_skills if skill.strip()])
    
    # Membersihkan dan menghilangkan duplikasi hasil akhir
    cleaned_skills = [skill.strip(' .,') for skill in all_skills if len(skill.strip(' .,')) > 1]
    unique_skills = list(OrderedDict.fromkeys(cleaned_skills))
    
    return unique_skills


def parse_experience(text: str) -> list:
    # Fungsi ini tetap sama
    if not text: return []
    experiences = []
    entry_pattern = r'((?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4})\s*[-–to]+\s*(?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4}|Present|Current))'
    entries = re.split(fr'(?={entry_pattern})', text, flags=re.IGNORECASE)
    for entry_block in entries:
        entry_block = entry_block.strip()
        if not entry_block: continue
        lines = entry_block.split('\n')
        date_range_match = re.match(entry_pattern, lines[0], re.IGNORECASE)
        date_range = date_range_match.group(1).strip() if date_range_match else "N/A"
        first_line_content = re.sub(entry_pattern, '', lines[0], count=1, flags=re.IGNORECASE).strip()
        position, company, description = "N/A", "N/A", ""
        remaining_lines = [first_line_content] + lines[1:] if first_line_content else lines[1:]
        content_lines = [line.strip() for line in remaining_lines if line.strip()]
        if not content_lines: continue
        position = content_lines[0]
        if len(content_lines) > 1:
            company = content_lines[1]
            description = '\n'.join(content_lines[2:]).strip()
        else:
            description = ""
        if position != "N/A" or company != "N/A":
            experiences.append({'date_range': date_range, 'position': position, 'company': company, 'description': description})
    return experiences

def parse_education(text: str) -> list:
    """
    Mem-parsing blok pendidikan dengan pendekatan baru yang lebih fleksibel.
    Mengasumsikan setiap baris adalah entri dan mencoba memisahkannya secara cerdas.
    """
    if not text:
        return []

    parsed_entries = []
    # Asumsikan setiap baris dalam blok education adalah entri terpisah
    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        year, degree, institution = 'N/A', 'N/A', 'N/A'

        # Mencoba mencari tahun (opsional)
        year_match = re.search(r'\b((19|20)\d{2})\b', line)
        if year_match:
            year = year_match.group(0)
            line = line.replace(year, '').strip()

        # Mencoba memisahkan institusi dari gelar berdasarkan kata kunci gelar
        degree_keywords = ['Certificate', 'Diploma', 'Bachelor', 'Master', 'Technician', 'Job-Related Training']
        found_degree = False
        for keyword in degree_keywords:
            match = re.search(rf'\b({keyword}.*)\b', line, re.IGNORECASE)
            if match:
                degree = match.group(1).strip()
                # Teks sebelum kata kunci dianggap sebagai institusi
                institution = line[:match.start()].strip(' ,')
                found_degree = True
                break
        
        # Jika tidak ada kata kunci yang cocok, gunakan fallback
        if not found_degree:
            # Asumsikan bagian setelah "City , State" adalah gelar
            parts = re.split(r'City\s*,\s*State', line, flags=re.IGNORECASE)
            if len(parts) > 1:
                institution = parts[0].strip() + " City, State"
                degree = parts[1].strip()
            else:
                institution = line # Jika gagal total, anggap semua sebagai institusi

        # Buat dictionary untuk entri yang sudah diparsing
        parsed_entry = {'year': year, 'degree': degree, 'institution': institution}

        # Hanya tambahkan jika entri valid dan belum ada
        if (parsed_entry['degree'] != 'N/A' or parsed_entry['institution'] != 'N/A') and parsed_entry not in parsed_entries:
            parsed_entries.append(parsed_entry)

    return parsed_entries

def extract_all_sections(text: str) -> dict:
    """
    Fungsi utama untuk mengekstrak semua informasi dari teks CV.
    PERBAIKAN: Cara memanggil parse_skills diubah untuk menangani gabungan seksi.
    """
    sections = extract_raw_sections(text)
    
    # PERBAIKAN: Mengambil daftar blok teks dari 'skills'
    skills_blocks = sections.get('skills', [])
    skills_list = parse_skills(skills_blocks)

    # Mengambil teks tunggal untuk experience dan education (asumsi hanya ada satu seksi utama)
    experience_text = '\n'.join(sections.get('experience', []))
    experience_list = parse_experience(experience_text)
    
    education_text = '\n'.join(sections.get('education', []))
    education_list = parse_education(education_text)
    
    summary_text = '\n'.join(sections.get('summary', []))

    return {
        'summary': clean_text(summary_text).replace("\n", " ") or 'N/A',
        'skills': skills_list or 'N/A', # Sekarang mengembalikan list
        'work_experience': experience_list or [],
        'education': education_list or []
    }