def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Menghitung Levenshtein distance antara dua string.
    """
    s1, s2 = s1.lower(), s2.lower()
    m, n = len(s1), len(s2)
    
    # Inisialisasi matriks DP
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Isi matriks
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1,        # Deletion
                           dp[i][j - 1] + 1,        # Insertion
                           dp[i - 1][j - 1] + cost) # Substitution
    
    return dp[m][n]