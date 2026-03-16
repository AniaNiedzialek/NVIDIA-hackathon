from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Course:
    code: str
    name: str
    units: int
    grade: Optional[str] = None
    term: str = ""
    status: str = "enrolled"  # enrolled, completed, planned

@dataclass
class Student:
    sjsu_id: str
    email: str
    first_name: str
    last_name: str
    major: str
    concentration: str
    catalog_year: int
    gpa: float
    units_completed: int
    units_in_progress: int
    expected_graduation: str
    visa_status: str  # domestic, f1, etc
    enrollment_status: str  # full-time, part-time
    holds: List[str]
    advisor: str
    courses: List[Course]

MOCK_STUDENTS = {
    "alex.chen@sjsu.edu": Student(
        sjsu_id="012345678",
        email="alex.chen@sjsu.edu",
        first_name="Alex",
        last_name="Chen",
        major="Computer Science",
        concentration="Software Engineering",
        catalog_year=2023,
        gpa=3.75,
        units_completed=87,
        units_in_progress=15,
        expected_graduation="Spring 2026",
        visa_status="f1",
        enrollment_status="full-time",
        holds=[],
        advisor="Dr. Sarah Johnson",
        courses=[
            Course("CS 146", "Data Structures & Algorithms", 3, grade="A", term="Fall 2024", status="completed"),
            Course("CS 151", "Object-Oriented Design", 3, grade="A-", term="Fall 2024", status="completed"),
            Course("CS 157A", "Intro to Database Management", 3, grade="B+", term="Fall 2024", status="completed"),
            Course("CS 160", "Intro to Software Engineering", 3, grade="A", term="Spring 2025", status="completed"),
            Course("CS 174", "Enterprise Distributed Systems", 3, "A", term="Spring 2025", status="completed"),
            Course("CS 180", "Operating Systems", 3, "A-", term="Fall 2025", status="completed"),
            Course("CS 200", "Grad Orientation", 1, "P", term="Fall 2025", status="completed"),
            Course("CS 255", "Adv Software Engineering", 3, status="enrolled"),
            Course("CS 271", "Software Architecture", 3, status="enrolled"),
            Course("CS 289", "Cloud Native Development", 3, status="enrolled"),
            Course("CS 297", "Software Engineering Project", 3, status="enrolled"),
            Course("MATH 161A", "Applied Probability & Statistics", 3, grade="B+", term="Fall 2024", status="completed"),
            Course("ENGR 100W", "Technical Writing", 3, grade="A", term="Spring 2025", status="completed"),
        ]
    ),
    "priya.patel@sjsu.edu": Student(
        sjsu_id="012345679",
        email="priya.patel@sjsu.edu",
        first_name="Priya",
        last_name="Patel",
        major="Data Science",
        concentration="Machine Learning",
        catalog_year=2022,
        gpa=3.92,
        units_completed=105,
        units_in_progress=12,
        expected_graduation="Fall 2025",
        visa_status="f1",
        enrollment_status="full-time",
        holds=["Immunization Hold"],
        advisor="Dr. Michael Lee",
        courses=[
            Course("CS 146", "Data Structures", 3, grade="A", term="Fall 2023", status="completed"),
            Course("MATH 163", "Probability & Statistics", 3, grade="A", term="Fall 2023", status="completed"),
            Course("CS 166", "Data Mining", 3, grade="A", term="Spring 2024", status="completed"),
            Course("CS 229", "Machine Learning", 3, grade="A", term="Spring 2024", status="completed"),
            Course("CS 235", "Advanced Database Systems", 3, grade="A-", term="Fall 2024", status="completed"),
            Course("DS 201", "Intro to Data Science", 3, grade="A", term="Fall 2024", status="completed"),
            Course("CS 274", "Cloud Computing", 3, grade="A", term="Spring 2025", status="completed"),
            Course("CS 258", "Neural Networks", 3, "A", term="Fall 2025", status="completed"),
            Course("CS 259", "Deep Learning", 3, "A-", term="Fall 2025", status="completed"),
            Course("CS 295", "Data Science Capstone", 3, status="enrolled"),
        ]
    ),
    "james.wilson@sjsu.edu": Student(
        sjsu_id="012345680",
        email="james.wilson@sjsu.edu",
        first_name="James",
        last_name="Wilson",
        major="Business Administration",
        concentration="Business Analytics",
        catalog_year=2023,
        gpa=3.45,
        units_completed=60,
        units_in_progress=15,
        expected_graduation="Spring 2027",
        visa_status="domestic",
        enrollment_status="full-time",
        holds=[],
        advisor="Prof. Emily Davis",
        courses=[
            Course("BUS1 101", "Financial Accounting", 3, grade="B+", term="Fall 2024", status="completed"),
            Course("BUS1 102", "Managerial Accounting", 3, grade="B", term="Fall 2024", status="completed"),
            Course("BUS3 101", "Legal Environment of Business", 3, grade="A-", term="Fall 2024", status="completed"),
            Course("BUS3 160", "Fundamentals of Business Analytics", 3, grade="A", term="Spring 2025", status="completed"),
            Course("BUS3 140", "Financial Management", 3, grade="B+", term="Spring 2025", status="completed"),
            Course("BUS3 165", "Data Visualization", 3, "A", term="Fall 2025", status="completed"),
            Course("BUS3 170", "Marketing Analytics", 3, "B+", term="Fall 2025", status="completed"),
            Course("BUS4 188", "Business Ethics", 3, status="enrolled"),
            Course("BUS5 189", "Predictive Analytics", 3, status="enrolled"),
            Course("BUS3 195", "Strategic Management", 3, status="enrolled"),
        ]
    ),
}

def get_student_context(student: Student) -> str:
    """Generate detailed context about the student for AI prompts."""
    reqs = get_degree_requirements(student)
    f1_info = get_f1_requirements(student) if student.visa_status == "f1" else None
    
    completed_courses = [c for c in student.courses if c.status == "completed"]
    enrolled_courses = [c for c in student.courses if c.status == "enrolled"]
    
    course_list = "\n".join([f"- {c.code}: {c.name} ({c.units} units) - {c.grade or 'In Progress'}" 
                            for c in completed_courses + enrolled_courses])
    
    context = f"""
STUDENT PROFILE:
- Name: {student.first_name} {student.last_name}
- SJSU ID: {student.sjsu_id}
- Email: {student.email}
- Major: {student.major}
- Concentration: {student.concentration}
- Catalog Year: {student.catalog_year}
- GPA: {student.gpa}
- Units Completed: {student.units_completed}
- Units In Progress: {student.units_in_progress}
- Expected Graduation: {student.expected_graduation}
- Visa Status: {student.visa_status.upper()}
- Enrollment Status: {student.enrollment_status}
- Advisor: {student.advisor}
- Account Holds: {', '.join(student.holds) if student.holds else 'None'}

CURRENT ENROLLMENT ({student.units_in_progress} units):
{chr(10).join([f"- {c.code}: {c.name}" for c in enrolled_courses])}

COMPLETED COURSES ({sum(c.units for c in completed_courses)} units):
{course_list}

DEGREE PROGRESS:
- Total Units Required: {reqs['total_units']}
- GE: {reqs['current']['ge']}/{reqs['ge_units']} ({reqs['current']['ge']/reqs['ge_units']*100:.1f}%)
- Major: {reqs['current']['major']}/{reqs['major_units']} ({reqs['current']['major']/reqs['major_units']*100:.1f}%)
- Electives: {reqs['current']['elective']}/{reqs['elective_units']} ({reqs['current']['elective']/reqs['elective_units']*100:.1f}%)
- Remaining Major Courses: {', '.join(reqs['courses']['remaining']) if reqs['courses']['remaining'] else 'None'}
"""
    
    if f1_info:
        context += f"""
F-1 COMPLIANCE STATUS:
- Minimum Units Required: {f1_info['min_units']}
- Current Units: {f1_info['current_units']}
- Status: {f1_info['status']}
- Next Semester Deadline: {f1_info['next_semester_deadline']}
"""
    
    return context


def get_student(email: str) -> Optional[Student]:
    return MOCK_STUDENTS.get(email.lower())

def get_degree_requirements(student: Student) -> dict:
    if "Computer Science" in student.major:
        return {
            "total_units": 120,
            "ge_units": 48,
            "major_units": 51,
            "elective_units": 21,
            "current": {
                "ge": 42,
                "major": 45,
                "elective": 0
            },
            "courses": {
                "completed": ["CS 146", "CS 151", "CS 157A", "CS 160", "CS 174", "CS 180", "CS 200"],
                "remaining": ["CS 256", "CS 264", "CS 272", "CS 281"]
            }
        }
    elif "Data Science" in student.major:
        return {
            "total_units": 120,
            "ge_units": 48,
            "major_units": 48,
            "elective_units": 24,
            "current": {
                "ge": 45,
                "major": 42,
                "elective": 15
            },
            "courses": {
                "completed": ["CS 146", "MATH 163", "CS 166", "CS 229", "CS 235", "DS 201", "CS 274"],
                "remaining": ["CS 256", "CS 277", "CS 289"]
            }
        }
    else:
        return {
            "total_units": 120,
            "ge_units": 48,
            "major_units": 42,
            "elective_units": 30,
            "current": {
                "ge": 30,
                "major": 21,
                "elective": 9
            },
            "courses": {
                "completed": [],
                "remaining": []
            }
        }

def get_f1_requirements(student: Student) -> dict:
    min_units = 8 if "Graduate" in student.major else 12
    
    return {
        "min_units": min_units,
        "current_units": student.units_in_progress,
        "status": "✅ Compliant" if student.units_in_progress >= min_units else "❌ Below Minimum",
        "next_semester_deadline": "January 15, 2026",
        "required_courses_for_full_time": [
            "CS 255 - Adv Software Engineering (3 units)",
            "CS 271 - Software Architecture (3 units)", 
            "CS 289 - Cloud Native Development (3 units)",
            "CS 297 - Software Engineering Project (3 units)"
        ],
        "recommended_actions": [
            "Schedule appointment with ISS for OPT advisement",
            "Apply for CPT after completing 2 semesters"
        ] if student.units_completed > 24 else []
    }
