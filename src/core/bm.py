def build_bad_char_table(pattern: str) -> dict:
    """Membangun tabel bad character untuk algoritma Boyer-Moore."""
    bad_char = {}
    for i in range(len(pattern)):
        bad_char[pattern[i]] = i
    return bad_char

def bm_search(text: str, pattern: str) -> list[int]:
    """
    Mencari semua kemunculan pattern dalam text menggunakan Boyer-Moore.

    Returns:
        List berisi indeks awal dari semua kemunculan pattern.
    """
    if not pattern:
        return []

    m = len(pattern)
    n = len(text)
    bad_char = build_bad_char_table(pattern)
    indices = []
    s = 0  # Shift dari pattern relatif terhadap text

    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        if j < 0:
            indices.append(s)
            s += (m - bad_char.get(text[s + m], -1)) if s + m < n else 1
        else:
            s += max(1, j - bad_char.get(text[s + j], -1))
    return indices