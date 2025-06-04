def levenshtein_distance(s1, s2):
    """Simulate Levenshtein distance with dummy results."""
    # Simulate close match if keyword is similar to CV content
    if "Farhan" in s1 and s2.lower() in ["reactt", "htmml"]:  # Typo simulation
        return 1
    elif "Aland" in s1 and s2.lower() == "reakt":
        return 1
    elif "Ariel" in s1 and s2.lower() == "expresss":
        return 1
    elif "Budi" in s1 and s2.lower() in ["pythn", "htnl"]:
        return 1
    elif "Citra" in s1 and s2.lower() in ["jva", "sgl"]:
        return 1
    return 10  # Large distance for no match