def build_bad_char_table(pattern: str) -> dict:
    """Membangun tabel bad character (kemunculan terakhir)."""
    bad_char = {}
    for i, char in enumerate(pattern):
        bad_char[char] = i
    return bad_char

def preprocess_good_suffix(pattern: str) -> list[int]:
    """
    Melakukan pre-processing untuk membuat tabel shift Good Suffix.
    """
    m = len(pattern)
    shift = [0] * (m + 1)
    border_pos = [0] * (m + 1)
    
    # Inisialisasi
    i = m
    j = m + 1
    border_pos[i] = j
    
    # Case 1: Mencari good suffix yang muncul lagi di pattern
    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if shift[j] == 0:
                shift[j] = j - i
            j = border_pos[j]
        i -= 1
        j -= 1
        border_pos[i] = j

    # Case 2: Sebagian good suffix cocok dengan prefix pattern
    j = border_pos[0]
    for i in range(m + 1):
        if shift[i] == 0:
            shift[i] = j
        if i == j:
            j = border_pos[j]
            
    return shift

def bm_search(text: str, pattern: str) -> list[int]:
    """
    Mencari semua kemunculan pattern dalam text menggunakan Boyer-Moore
    dengan Bad Character dan Good Suffix Heuristics.
    """
    if not pattern or not text or len(pattern) > len(text):
        return []

    m = len(pattern)
    n = len(text)
    
    # Pre-processing
    bad_char_table = build_bad_char_table(pattern)
    good_suffix_shift_table = preprocess_good_suffix(pattern)
    
    indices = []
    s = 0  # s adalah shift dari pattern relatif terhadap text

    while s <= n - m:
        j = m - 1 # Mulai perbandingan dari kanan ke kiri
        
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        if j < 0:
            # Pattern ditemukan
            indices.append(s)
            # Geser pattern berdasarkan tabel good suffix untuk mencari kemunculan berikutnya
            s += good_suffix_shift_table[0]
        else:
            # Mismatch terjadi
            # Hitung pergeseran dari kedua heuristik
            bad_char_shift = j - bad_char_table.get(text[s + j], -1)
            good_suffix_shift = good_suffix_shift_table[j + 1]
            
            # Pilih pergeseran terbesar untuk memaksimalkan lompatan
            s += max(bad_char_shift, good_suffix_shift)
            
    return indices