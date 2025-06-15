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
            content_block = cleaned_text[content_start:content_end].strip()
            if section_name not in sections: sections[section_name] = []
            sections[section_name].append(content_block)
    return sections

def parse_skills(text_blocks: list) -> list:
    """Parser skills yang menggabungkan baris terpotong dan mem-parsing secara kontekstual."""
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

def parse_education(text: str) -> list:
    """Parser pendidikan yang andal."""
    if not text: return []
    parsed_entries = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        year, degree, institution, description = 'N/A', 'N/A', 'N/A', None
        if ':' in line:
            parts = line.split(':', 1)
            degree = parts[0].strip()
            institution_part = parts[1].strip()
            year_match = re.search(r'\b((19|20)\d{2})\b', institution_part)
            if year_match:
                year = year_match.group(0)
                institution = re.sub(r'\s+', ' ', institution_part.replace(year, '')).strip()
            else:
                institution = institution_part
        else:
            degree = "Informasi Tambahan"
            institution = "N/A"
            description = line
            year_match = re.search(r'\b((19|20)\d{2})\b', line)
            if year_match: year = year_match.group(0)
        parsed_entry = {'year': year, 'degree': degree, 'institution': institution}
        if description: parsed_entry['description'] = description
        if (parsed_entry.get('degree') != 'N/A' or parsed_entry.get('institution') != 'N/A') and parsed_entry not in parsed_entries:
            parsed_entries.append(parsed_entry)
    return parsed_entries

def parse_experience(text: str) -> list:
    """
    Parser experience universal dengan pendekatan "Jangkar Tanggal".
    """
    if not text:
        return []

    experiences = []
    current_experience = None

    # Pola tanggal yang fleksibel, bisa menangani "Month YYYY" dan "MM/YYYY"
    date_pattern = re.compile(
        r'((?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4})\s*to\s*(?:\d{2}/\d{4}|[A-Za-z]+\s+\d{4}|Present|Current))',
        re.IGNORECASE
    )

    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        date_match = date_pattern.search(line)

        # Jika sebuah baris mengandung pola tanggal, anggap itu awal entri baru.
        if date_match:
            # Simpan dulu entri sebelumnya jika ada
            if current_experience:
                current_experience['description'] = '\n'.join(current_experience['description']).strip()
                experiences.append(current_experience)

            # Buat entri baru
            date_range = date_match.group(1).strip()
            
            # Teks sebelum tanggal adalah Perusahaan
            company = line[:date_match.start()].strip()
            # Teks setelah tanggal adalah Posisi
            position = line[date_match.end():].strip()

            current_experience = {
                'date_range': date_range,
                'company': company.replace('Company Name', '').strip(' ,'),
                'position': position.strip(' ,'),
                'description': [] # Siapkan list untuk menampung deskripsi
            }
        
        # Jika bukan baris tanggal, maka ini adalah bagian dari deskripsi pekerjaan saat ini.
        elif current_experience:
            current_experience['description'].append(line)

    # Simpan entri pekerjaan terakhir setelah loop selesai
    if current_experience:
        current_experience['description'] = '\n'.join(current_experience['description']).strip()
        experiences.append(current_experience)

    return experiences

def extract_all_sections(text: str) -> dict:
    """Fungsi utama untuk mengekstrak semua informasi dari teks CV."""
    sections = extract_raw_sections(text)
    
    skills_blocks = sections.get('skills', [])
    skills_list = parse_skills(skills_blocks)
    
    experience_text = '\n'.join(sections.get('experience', []))
    experience_list = parse_experience(experience_text)
    
    education_text = '\n'.join(sections.get('education', []))
    education_list = parse_education(education_text)
    
    summary_text = '\n'.join(sections.get('summary', []))

    # Mengembalikan dengan kunci 'experience' sesuai permintaan Anda.
    return {
        'summary': clean_text(summary_text).replace("\n", " ") or 'N/A',
        'skills': skills_list,
        'experience': experience_list,
        'education': education_list or []
    }