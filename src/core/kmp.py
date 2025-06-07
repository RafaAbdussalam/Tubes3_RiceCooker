def compute_lps_array(pattern: str) -> list[int]:
    """Menghitung tabel LPS untuk algoritma KMP."""
    length = 0
    lps = [0] * len(pattern)
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text: str, pattern: str) -> list[int]:
    """
    Mencari semua kemunculan pattern dalam text menggunakan KMP.

    Returns:
        List berisi indeks awal dari semua kemunculan pattern.
    """
    if not pattern:
        return []
        
    m, n = len(pattern), len(text)
    lps = compute_lps_array(pattern)
    indices = []
    i = 0  # Indeks untuk text
    j = 0  # Indeks untuk pattern

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            indices.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return indices