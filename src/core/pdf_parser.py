def extract_text_from_pdf(pdf_path):
    """Simulate extracting text from a PDF file with dummy data."""
    # Dummy CV texts based on path
    dummy_texts = {
        "data/HR/cv1.pdf": "Farhan\nPhone: 081234567890\nEmail: farhan@example.com\nSkills: React, HTML, Python\nSoftware Engineer at Google (2018-2020)\nB.S. in Computer Science, MIT, 2014-2018",
        "data/HR/cv2.pdf": "Aland\nPhone: 081298765432\nEmail: aland@example.com\nSkills: React, Java\nData Analyst at Amazon (2019-2021)\nM.S. in Data Science, Stanford, 2015-2019",
        "data/Designer/cv_designer1.pdf": "Ariel\nPhone: 081212345678\nEmail: ariel@example.com\nSkills: Express, SQL\nUX Designer at Adobe (2020-2022)\nB.A. in Design, RISD, 2016-2020",
        "data/Designer/cv_designer2.pdf": "Budi\nPhone: 081287654321\nEmail: budi@example.com\nSkills: Python, HTML\nGraphic Designer at Canva (2017-2019)\nB.F.A. in Graphic Design, SVA, 2013-2017",
        "data/HR/cv3.pdf": "Citra\nPhone: 081276543210\nEmail: citra@example.com\nSkills: Java, SQL\nHR Specialist at IBM (2018-2021)\nM.B.A., Harvard, 2014-2018"
    }
    return dummy_texts.get(pdf_path, "")