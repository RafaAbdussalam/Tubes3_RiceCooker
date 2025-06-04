def kmp_search(text, pattern):
    """Simulate KMP search with dummy results."""
    # Simulate occurrences based on pattern and text
    if "Farhan" in text and pattern.lower() in ["react", "html"]:
        return [10, 20]  # Two occurrences
    elif "Aland" in text and pattern.lower() == "react":
        return [15]  # One occurrence
    elif "Ariel" in text and pattern.lower() == "express":
        return [25]  # One occurrence
    elif "Budi" in text and pattern.lower() in ["python", "html"]:
        return [5, 10]  # Two occurrences
    elif "Citra" in text and pattern.lower() in ["java", "sql"]:
        return [30]  # One occurrence
    return []  # No match