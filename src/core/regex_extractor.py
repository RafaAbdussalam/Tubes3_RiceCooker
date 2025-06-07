import re

def extract_section(text: str, start_keyword: str, end_keywords: list[str]) -> str:
    """Fungsi helper untuk mengekstrak teks di antara keyword."""
    # MODIFIKASI: Menggunakan non-capturing group (?:...) untuk start_keyword.
    # Ini memastikan bahwa (.*?) selalu menjadi group(1), tidak peduli bentuk start_keyword.
    pattern_str = fr'(?:{start_keyword})(.*?)(?={"|".join(end_keywords)}|$)'
    match = re.search(pattern_str, text, re.IGNORECASE | re.DOTALL)
    if match:
        # Sekarang match.group(1) akan selalu berisi konten yang kita inginkan.
        return match.group(1).strip()
    return ""

def extract_skills(text: str) -> str:
    """Mengekstrak bagian Skills dari teks CV."""
    end_keywords = ['Experience', 'Work History', 'Education', 'Projects', 'Accomplishments']
    return extract_section(text, 'Skills', end_keywords)

def extract_experience(text: str) -> str:
    """Mengekstrak bagian Experience/Work History dari teks CV."""
    # MODIFIKASI: Hapus tanda kurung, biarkan helper yang menanganinya.
    start_keywords = r'Experience|Work History|Employment History'
    end_keywords = ['Education', 'Projects', 'Skills', 'Certifications', 'Accomplishments']
    return extract_section(text, start_keywords, end_keywords)
    
def extract_education(text: str) -> str:
    """Mengekstrak bagian Education dari teks CV."""
    end_keywords = ['Skills', 'Experience', 'Work History', 'Projects', 'Certifications']
    return extract_section(text, 'Education', end_keywords)

# --- Untuk pengujian mandiri ---
if __name__ == '__main__':
    sample_text = """
    John Doe
    
    SKILLS
    Python, Java, SQL, Git, Docker.
    Problem Solving.
    
    WORK HISTORY
    Software Engineer at Tech Corp (2020 - Present)
    - Developed cool stuff.
    
    EDUCATION
    Bachelor of Science in Computer Science, University of Life (2016 - 2020)
    """
    skills = extract_skills(sample_text)
    print("--- SKILLS ---")
    print(skills)

    experience = extract_experience(sample_text)
    print("\n--- EXPERIENCE ---")
    print(experience)

    education = extract_education(sample_text)
    print("\n--- EDUCATION ---")
    print(education)