"""
Hardcoded courses and waitlist data for the Professor Portal (hackathon MVP).
Courses include roster counts and waitlisted students. Data is copied into session state
so we can mutate status/permission_code when granting codes.
"""

import copy
from typing import List, Dict, Any, Optional

# Waitlist entry: status is "waiting" | "approved" | "denied"; permission_code set when approved.
def _wl(id: str, name: str, student_id: str, major: str, standing: str, gpa: float,
        units_completed: int, position: int, request_ts: str, priority_tag: str = "",
        status: str = "waiting", permission_code: Optional[str] = None):
    return {
        "id": id,
        "name": name,
        "student_id": student_id,
        "major": major,
        "standing": standing,
        "gpa": gpa,
        "units_completed": units_completed,
        "waitlist_position": position,
        "request_timestamp": request_ts,
        "priority_tag": priority_tag or "",
        "status": status,
        "permission_code": permission_code,
    }

# All courses (multiple professors). professor_id links to mock_professors.
MOCK_COURSES_RAW = [
    {
        "id": "course_cs146_01",
        "course_code": "CS 146",
        "title": "Data Structures and Algorithms",
        "section": "01",
        "professor_id": "prof_001",
        "total_seats": 35,
        "enrolled_count": 32,
        "semester": "Spring 2026",
        "waitlist": [
            _wl("w1", "Alex Chen", "012345678", "Computer Science", "Senior", 3.75, 87, 1, "2026-01-10 09:00", "Major requirement", "waiting", None),
            _wl("w2", "Jordan Kim", "012345681", "Computer Science", "Junior", 3.62, 72, 2, "2026-01-10 09:15", "", "waiting", None),
            _wl("w3", "Sam Rivera", "012345682", "Software Engineering", "Senior", 3.45, 95, 3, "2026-01-10 10:00", "Graduating", "waiting", None),
            _wl("w4", "Casey Morgan", "012345683", "Computer Science", "Sophomore", 3.90, 45, 4, "2026-01-11 08:00", "", "waiting", None),
            _wl("w5", "Riley Taylor", "012345684", "Data Science", "Junior", 3.20, 68, 5, "2026-01-11 14:00", "", "waiting", None),
        ],
    },
    {
        "id": "course_cs151_01",
        "course_code": "CS 151",
        "title": "Object-Oriented Design",
        "section": "01",
        "professor_id": "prof_001",
        "total_seats": 40,
        "enrolled_count": 40,
        "semester": "Spring 2026",
        "waitlist": [
            _wl("w6", "Jamie Lopez", "012345685", "Computer Science", "Sophomore", 3.55, 52, 1, "2026-01-12 11:00", "", "waiting", None),
            _wl("w7", "Avery Brooks", "012345686", "Computer Science", "Junior", 3.88, 75, 2, "2026-01-12 12:00", "", "waiting", None),
        ],
    },
    {
        "id": "course_se165_01",
        "course_code": "SE 165",
        "title": "Software Engineering Process",
        "section": "01",
        "professor_id": "prof_002",
        "total_seats": 30,
        "enrolled_count": 28,
        "semester": "Spring 2026",
        "waitlist": [
            _wl("w8", "Morgan Bell", "012345687", "Software Engineering", "Senior", 3.70, 98, 1, "2026-01-09 08:30", "Graduating", "waiting", None),
            _wl("w9", "Quinn Davis", "012345688", "Computer Science", "Junior", 3.42, 70, 2, "2026-01-09 09:00", "", "waiting", None),
            _wl("w10", "Reese Clark", "012345689", "Computer Engineering", "Master's", 3.95, 24, 3, "2026-01-09 10:00", "Graduate", "waiting", None),
        ],
    },
    {
        "id": "course_cmpe120_01",
        "course_code": "CMPE 120",
        "title": "Computer Architecture",
        "section": "01",
        "professor_id": "prof_002",
        "total_seats": 35,
        "enrolled_count": 35,
        "semester": "Spring 2026",
        "waitlist": [
            _wl("w11", "Skyler Green", "012345690", "Computer Engineering", "Junior", 3.60, 65, 1, "2026-01-13 09:00", "", "waiting", None),
        ],
    },
]


def get_courses_for_professor(professor_id: str) -> List[Dict[str, Any]]:
    """Return deep copies of courses taught by this professor (for mutable session state)."""
    out = []
    for c in MOCK_COURSES_RAW:
        if c["professor_id"] == professor_id:
            out.append(copy.deepcopy(c))
    return out


def get_course_by_id(course_id: str) -> Optional[Dict[str, Any]]:
    """Return a deep copy of one course by id."""
    for c in MOCK_COURSES_RAW:
        if c["id"] == course_id:
            return copy.deepcopy(c)
    return None
