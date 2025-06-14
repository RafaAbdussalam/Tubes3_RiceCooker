# Simulated database operations with dummy data

def fetch_candidates():
    """Simulate fetching candidates from the database with dummy data."""
    return [
        {"id": 1, "name": "Farhan", "cv_path": "../data/HR/cv1.pdf"},
        {"id": 2, "name": "Aland", "cv_path": "../data/HR/10276858.pdf"},
        {"id": 3, "name": "Ariel", "cv_path": "../data/Designer/11152490.pdf"},
    ]

def save_candidate_profile(candidate_data):
    """Simulate saving a candidate profile to the database."""
    print(f"Saving candidate to database: {candidate_data}")
    return True