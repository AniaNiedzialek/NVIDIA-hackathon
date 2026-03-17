"""
Hardcoded professor credentials and profile data for the Professor Portal (hackathon MVP).
No real authentication; used for demo only.
"""

# Demo professors. Password checked as plain text for MVP.
MOCK_PROFESSORS = [
    {
        "id": "prof_001",
        "name": "Dr. Sarah Johnson",
        "email": "sarah.johnson@sjsu.edu",
        "department": "Computer Science",
        "password": "prof123",
        "course_ids": ["course_cs146_01", "course_cs151_01"],
    },
    {
        "id": "prof_002",
        "name": "Dr. Michael Lee",
        "email": "michael.lee@sjsu.edu",
        "department": "Computer Engineering",
        "password": "prof456",
        "course_ids": ["course_se165_01", "course_cmpe120_01"],
    },
]


def get_professor_by_credentials(email: str, password: str):
    """Validate login against hardcoded credentials. Returns professor dict or None."""
    email_clean = (email or "").strip().lower()
    for p in MOCK_PROFESSORS:
        if p["email"].lower() == email_clean and p["password"] == password:
            return {**p}  # return a copy so we don't mutate original
    return None


def get_professor_by_id(professor_id: str):
    """Return professor dict by id."""
    for p in MOCK_PROFESSORS:
        if p["id"] == professor_id:
            return {**p}
    return None
