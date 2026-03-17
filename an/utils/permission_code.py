"""
Permission code generation and auto-grant logic for the Professor Portal.
- available_seats = total_seats - enrolled_count
- Eligible students: status === "waiting", sorted by waitlist_position ascending
- Top N (N = available_seats) get a code; status set to "approved"
"""

import random
import string
from typing import List, Dict, Any, Tuple


def generate_permission_code(course_code: str) -> str:
    """Generate a realistic-looking permission code, e.g. PERM-CS146-8F3K2."""
    # Normalize course code (e.g. "CS 146" -> "CS146")
    base = course_code.replace(" ", "")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"PERM-{base}-{suffix}"


def get_eligible_waiting_students(course: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return waitlist students with status 'waiting', sorted by waitlist_position ascending."""
    waiting = [s for s in course.get("waitlist", []) if s.get("status") == "waiting"]
    return sorted(waiting, key=lambda s: s.get("waitlist_position", 999))


def auto_grant_permission_codes(
    course: Dict[str, Any],
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Auto-grant permission codes to top N waitlisted students where N = available_seats.
    Modifies course["waitlist"] in place: assigns permission_code and sets status="approved".
    Returns (count_granted, list of updated student entries that were granted).
    """
    total = course.get("total_seats", 0)
    enrolled = course.get("enrolled_count", 0)
    available_seats = max(0, total - enrolled)

    if available_seats == 0:
        return 0, []

    course_code = course.get("course_code", "COURSE")
    eligible = get_eligible_waiting_students(course)
    to_grant = eligible[:available_seats]
    granted = []

    for student in to_grant:
        code = generate_permission_code(course_code)
        student["permission_code"] = code
        student["status"] = "approved"
        granted.append(student)

    return len(granted), granted
