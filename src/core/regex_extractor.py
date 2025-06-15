# File: src/core/regex_extractor.py (Versi Optimisasi Final)

import re
from collections import OrderedDict

# Kamus kata kunci yang komprehensif, termasuk sinonim penting.
# 'additional information' ditambahkan untuk menangani kasus CV Akuntan.
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
    
    # 1. Ganti semua pemisah umum (baris baru, titik koma, bullet) menjadi pemisah tunggal '|'.
    normalized_str = re.sub(r'\s*[\n;*•●]\s*', '|', content)
    # 2. Ganti spasi ganda atau lebih (untuk skill dalam satu baris) menjadi '|'.
    normalized_str = re.sub(r'\s{2,}', '|', normalized_str)
    
    # 3. Pisahkan menjadi list, bersihkan spasi, dan buang item yang terlalu pendek/kosong.
    skills_list = [skill.strip(' .,') for skill in normalized_str.split('|') if len(skill.strip()) > 2]
    
    # 4. Filter skills yang valid (tidak mengandung kata-kata umum yang bukan skill)
    invalid_keywords = ['and', 'or', 'with', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'by']
    valid_skills = []
    for skill in skills_list:
        # Skip jika skill terlalu pendek atau hanya berisi kata-kata umum
        if len(skill.split()) <= 1 and skill.lower() in invalid_keywords:
            continue
        # Skip jika skill mengandung kata-kata umum di awal
        if skill.lower().split()[0] in invalid_keywords:
            continue
        valid_skills.append(skill)
    
    # 5. Hilangkan duplikat sambil menjaga urutan
    unique_skills = list(OrderedDict.fromkeys(valid_skills))
    
    # 6. Kembalikan sebagai satu string yang dipisahkan oleh baris baru
    return '\n'.join(unique_skills)

def _clean_paragraph_section(content: str) -> str:
    """Fungsi pembersih umum untuk seksi berbasis paragraf seperti Experience atau Education."""
    if not content:
        return ""
    # Hapus bullet points di awal setiap baris
    cleaned = re.sub(r'^\s*[•*-]\s*', '', content, flags=re.MULTILINE)
    # Ganti spasi/newline ganda atau lebih dengan satu spasi
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def _format_job_history(content: str) -> str:
    """Memformat job history menjadi format yang lebih terstruktur."""
    if not content:
        return ""
    
    # 1. Bersihkan teks dari karakter khusus dan format yang tidak diinginkan
    content = re.sub(r'•\s*(\d+)\s*•', '', content)  # Hapus nomor urut
    content = re.sub(r'•\s*', '', content)  # Hapus bullet points
    content = re.sub(r'\s+', ' ', content)  # Normalisasi spasi
    
    # 2. Pisahkan setiap pengalaman kerja
    # Pola yang lebih fleksibel untuk menangkap berbagai format tanggal
    job_patterns = [
        # Format MM/YYYY to MM/YYYY
        r'(?i)(.*?)\s*(\d{2}/\d{4})\s+(?:to|until|-)\s+(\d{2}/\d{4})\s*(?:Company Name|.*?)(?:City\s*,\s*State|.*?)(?:\(.*?\))?\s*(.*?)(?=\s*(?:\d{2}/\d{4}\s+(?:to|until|-)|$))',
        # Format Month YYYY to Month YYYY
        r'(?i)(.*?)\s*(\w+)\s+(\d{4})\s+(?:to|until|-)\s+(\w+)\s+(\d{4})\s*(?:Company Name|.*?)(?:City\s*,\s*State|.*?)(?:\(.*?\))?\s*(.*?)(?=\s*(?:\w+\s+\d{4}\s+(?:to|until|-)|$))',
        # Format YYYY to YYYY
        r'(?i)(.*?)\s*(\d{4})\s+(?:to|until|-)\s+(\d{4})\s*(?:Company Name|.*?)(?:City\s*,\s*State|.*?)(?:\(.*?\))?\s*(.*?)(?=\s*(?:\d{4}\s+(?:to|until|-)|$))'
    ]
    
    formatted_jobs = []
    
    for pattern in job_patterns:
        jobs = re.finditer(pattern, content, re.DOTALL)
        for job in jobs:
            try:
                title = job.group(1).strip()
                
                # Handle different date formats
                if len(job.groups()) == 4:  # MM/YYYY format
                    start_date = job.group(2).strip()
                    end_date = job.group(3).strip()
                    description = job.group(4).strip()
                elif len(job.groups()) == 6:  # Month YYYY format
                    start_month = job.group(2).strip()
                    start_year = job.group(3).strip()
                    end_month = job.group(4).strip()
                    end_year = job.group(5).strip()
                    description = job.group(6).strip()
                    start_date = f"{start_month} {start_year}"
                    end_date = f"{end_month} {end_year}"
                else:  # YYYY format
                    start_year = job.group(2).strip()
                    end_year = job.group(3).strip()
                    description = job.group(4).strip()
                    start_date = start_year
                    end_date = end_year
                
                # Bersihkan judul dari karakter khusus
                title = re.sub(r'[•*]', '', title)
                title = re.sub(r'\s+', ' ', title)
                
                # Format deskripsi menjadi bullet points
                description_points = re.split(r'(?<=[.!?])\s+(?=[A-Z])', description)
                description_points = [point.strip() for point in description_points if point.strip()]
                
                if len(description_points) <= 1:
                    description_points = [point.strip() for point in description.split(',') if point.strip()]
                
                # Buat format yang rapi
                job_entry = f"{title}\n{start_date} - {end_date}\n"
                job_entry += "\n".join(f"• {point}" for point in description_points)
                formatted_jobs.append(job_entry)
                
            except Exception as e:
                print(f"Error processing job entry: {e}")
                continue
        
        if formatted_jobs:  # Jika sudah menemukan job dengan pola ini, tidak perlu coba pola lain
            break
    
    # Jika tidak ada job yang ditemukan, coba format ulang dengan pola yang lebih sederhana
    if not formatted_jobs:
        lines = content.split('.')
        formatted_content = []
        current_job = []
        current_date = None
        
        for line in lines:
            line = line.strip()
            if line:
                # Cek berbagai format tanggal
                date_match = re.search(r'(\d{2}/\d{4}|\w+\s+\d{4}|\d{4})\s+(?:to|until|-)\s+(\d{2}/\d{4}|\w+\s+\d{4}|\d{4})', line)
                if date_match:
                    if current_job:
                        formatted_content.append('\n'.join(current_job))
                        current_job = []
                    current_date = f"{date_match.group(1)} - {date_match.group(2)}"
                    title = line[:date_match.start()].strip()
                    if title:
                        current_job.append(title)
                    current_job.append(current_date)
                else:
                    if current_job:
                        current_job.append(f"• {line}")
        
        if current_job:
            formatted_content.append('\n'.join(current_job))
        
        return '\n\n'.join(formatted_content)
    
    return "\n\n".join(formatted_jobs)

def _format_education(content: str) -> str:
    """Memformat education menjadi format yang lebih terstruktur."""
    if not content:
        return ""
    
    # 1. Bersihkan teks dari karakter khusus dan format yang tidak diinginkan
    content = re.sub(r'•\s*', '', content)  # Hapus bullet points
    content = re.sub(r'\s+', ' ', content)  # Normalisasi spasi
    
    # 2. Pisahkan setiap entri pendidikan
    # Pola yang lebih fleksibel untuk menangkap berbagai format
    edu_patterns = [
        # Format dengan tahun di tengah
        r'(?i)(.*?)\s*(\d{4})\s*(.*?)(?:GPA:.*?)?(.*?)(?=\s*(?:\d{4}|$))',
        # Format dengan tahun di akhir
        r'(?i)(.*?)\s*(.*?)\s*(\d{4})(?:GPA:.*?)?(.*?)(?=\s*(?:\d{4}|$))',
        # Format dengan tahun di awal
        r'(?i)(\d{4})\s*(.*?)\s*(.*?)(?:GPA:.*?)?(.*?)(?=\s*(?:\d{4}|$))'
    ]
    
    formatted_edus = []
    
    for pattern in edu_patterns:
        educations = re.finditer(pattern, content, re.DOTALL)
        for edu in educations:
            try:
                groups = edu.groups()
                
                # Handle different formats
                if pattern == edu_patterns[0]:  # Tahun di tengah
                    institution = groups[0].strip()
                    year = groups[1].strip()
                    degree = groups[2].strip()
                    details = groups[3].strip()
                elif pattern == edu_patterns[1]:  # Tahun di akhir
                    institution = groups[0].strip()
                    degree = groups[1].strip()
                    year = groups[2].strip()
                    details = groups[3].strip()
                else:  # Tahun di awal
                    year = groups[0].strip()
                    institution = groups[1].strip()
                    degree = groups[2].strip()
                    details = groups[3].strip()
                
                # Bersihkan teks
                institution = re.sub(r'[•*]', '', institution)
                institution = re.sub(r'\s+', ' ', institution)
                degree = re.sub(r'[•*]', '', degree)
                degree = re.sub(r'\s+', ' ', degree)
                
                # Format detail menjadi bullet points
                detail_points = re.split(r'(?<=[.!?])\s+(?=[A-Z])', details)
                detail_points = [point.strip() for point in detail_points if point.strip()]
                
                if len(detail_points) <= 1:
                    detail_points = [point.strip() for point in details.split(',') if point.strip()]
                
                # Buat format yang rapi
                edu_entry = f"{institution}\n{year}\n{degree}"
                if detail_points:
                    edu_entry += "\n" + "\n".join(f"• {point}" for point in detail_points)
                formatted_edus.append(edu_entry)
                
            except Exception as e:
                print(f"Error processing education entry: {e}")
                continue
        
        if formatted_edus:  # Jika sudah menemukan education dengan pola ini, tidak perlu coba pola lain
            break
    
    # Jika tidak ada education yang ditemukan, coba format ulang dengan pola yang lebih sederhana
    if not formatted_edus:
        lines = content.split('.')
        formatted_content = []
        current_edu = []
        current_year = None
        
        for line in lines:
            line = line.strip()
            if line:
                # Cek apakah baris mengandung tahun
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    if current_edu:
                        formatted_content.append('\n'.join(current_edu))
                        current_edu = []
                    current_year = year_match.group(0)
                    # Ambil nama institusi dari sebelum tahun
                    institution = line[:year_match.start()].strip()
                    if institution:
                        current_edu.append(institution)
                    current_edu.append(current_year)
                else:
                    if current_edu:
                        current_edu.append(f"• {line}")
        
        if current_edu:
            formatted_content.append('\n'.join(current_edu))
        
        return '\n\n'.join(formatted_content)
    
    return "\n\n".join(formatted_edus)

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
        
        # Gabungkan konten jika nama seksi sama
        raw_sections[section['name']] = raw_sections.get(section['name'], "") + "\n" + content

    # 3. Lakukan pembersihan dan parsing akhir untuk setiap seksi.
    skills_content_to_parse = []
    
    for name, content in raw_sections.items():
        if name in ['skills', 'accomplishments']:
            skills_content_to_parse.append(content)
        elif name == 'experience':
            final_sections[name] = _format_job_history(content)
        elif name == 'education':
            final_sections[name] = _format_education(content)
        elif name in final_sections:
            final_sections[name] = _clean_paragraph_section(content)

    # Parsing khusus untuk gabungan semua skills.
    if skills_content_to_parse:
        final_sections['skills'] = _parse_skills_from_block('\n'.join(skills_content_to_parse))
    
    return final_sections