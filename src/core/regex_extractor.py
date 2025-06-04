def extract_candidate_info(text):
    """Simulate extracting candidate information with dummy data."""
    dummy_data = {
        "Farhan": {
            "name": "Farhan",
            "phone": "081234567890",
            "email": "farhan@example.com",
            "skills": ["React", "HTML", "Python"],
            "job_history": [{"position": "Software Engineer", "company": "Google", "years": "2018-2020"}],
            "education": [{"degree": "B.S. in Computer Science", "university": "MIT", "years": "2014-2018"}]
        },
        "Aland": {
            "name": "Aland",
            "phone": "081298765432",
            "email": "aland@example.com",
            "skills": ["React", "Java"],
            "job_history": [{"position": "Data Analyst", "company": "Amazon", "years": "2019-2021"}],
            "education": [{"degree": "M.S. in Data Science", "university": "Stanford", "years": "2015-2019"}]
        },
        "Ariel": {
            "name": "Ariel",
            "phone": "081212345678",
            "email": "ariel@example.com",
            "skills": ["Express", "SQL"],
            "job_history": [{"position": "UX Designer", "company": "Adobe", "years": "2020-2022"}],
            "education": [{"degree": "B.A. in Design", "university": "RISD", "years": "2016-2020"}]
        },
        "Budi": {
            "name": "Budi",
            "phone": "081287654321",
            "email": "budi@example.com",
            "skills": ["Python", "HTML"],
            "job_history": [{"position": "Graphic Designer", "company": "Canva", "years": "2017-2019"}],
            "education": [{"degree": "B.F.A. in Graphic Design", "university": "SVA", "years": "2013-2017"}]
        },
        "Citra": {
            "name": "Citra",
            "phone": "081276543210",
            "email": "citra@example.com",
            "skills": ["Java", "SQL"],
            "job_history": [{"position": "HR Specialist", "company": "IBM", "years": "2018-2021"}],
            "education": [{"degree": "M.B.A.", "university": "Harvard", "years": "2014-2018"}]
        }
    }
    # Extract name from text to determine which dummy data to return
    for name in dummy_data:
        if name in text:
            return dummy_data[name]
    return {"name": "Unknown", "phone": "N/A", "email": "N/A", "skills": [], "job_history": [], "education": []}