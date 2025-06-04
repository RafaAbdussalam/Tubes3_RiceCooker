def bm_search(text, pattern):
    """Simulate Boyer-Moore search with dummy results."""
    # Same dummy results as kmp_search for consistency
    if "Farhan" in text and pattern.lower() in ["react", "html"]:
        return [10, 20]
    elif "Aland" in text and pattern.lower() == "react":
        return [15]
    elif "Ariel" in text and pattern.lower() == "express":
        return [25]
    elif "Budi" in text and pattern.lower() in ["python", "html"]:
        return [5, 10]
    elif "Citra" in text and pattern.lower() in ["java", "sql"]:
        return [30]
    return []