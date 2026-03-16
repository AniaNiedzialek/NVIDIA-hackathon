from data.student_data import Student, get_degree_requirements, get_f1_requirements

def get_personalized_answer(student: Student, question: str) -> str:
    """Generate personalized answers based on student's exact data."""
    
    question_lower = question.lower()
    reqs = get_degree_requirements(student)
    
    # Calculate exact remaining units
    total_completed = student.units_completed + student.units_in_progress
    remaining_units = reqs['total_units'] - total_completed
    
    # Get remaining major courses
    remaining_major = reqs['courses']['remaining']
    remaining_ge = reqs['ge_units'] - reqs['current']['ge']
    remaining_electives = reqs['elective_units'] - reqs['current']['elective']
    
    answers = []
    
    # Graduation timing
    if any(word in question_lower for word in ['graduat', 'when will i', 'when can i', 'finish', 'complete']):
        answers.append(f"## 🎓 Your Graduation Timeline\n")
        answers.append(f"**Expected Graduation: {student.expected_graduation}**\n")
        answers.append(f"- You need **{remaining_units} more units** to graduate")
        answers.append(f"- You've completed {total_completed}/{reqs['total_units']} total units ({total_completed/reqs['total_units']*100:.1f}%)")
        if remaining_major:
            answers.append(f"- Remaining major courses: {', '.join(remaining_major)}")
        answers.append(f"- GE remaining: {remaining_ge} units")
        answers.append(f"- Electives remaining: {remaining_electives} units")
    
    # Units needed
    if any(word in question_lower for word in ['unit', 'credits', 'hour']):
        if 'need' in question_lower or 'how many' in question_lower:
            answers.append(f"## 📊 Your Unit Status\n")
            answers.append(f"**Total Units Required: {reqs['total_units']}**\n")
            answers.append(f"- ✅ Completed: {student.units_completed} units")
            answers.append(f"- 📚 In Progress: {student.units_in_progress} units")
            answers.append(f"- ⏳ Remaining: {remaining_units} units")
            answers.append(f"\n**Breakdown:**")
            answers.append(f"- GE: {reqs['current']['ge']}/{reqs['ge_units']} (need {remaining_ge} more)")
            answers.append(f"- Major: {reqs['current']['major']}/{reqs['major_units']} (need {len(remaining_major)} more courses)")
            answers.append(f"- Electives: {reqs['current']['elective']}/{reqs['elective_units']} (need {remaining_electives} more)")
    
    # F-1 Status
    if student.visa_status == 'f1' and any(word in question_lower for word in ['f1', 'visa', 'status', 'maintain', 'compliance', 'full-time', 'minimum']):
        f1 = get_f1_requirements(student)
        answers.append(f"## 🛂 Your F-1 Compliance Status\n")
        answers.append(f"**Status: {f1['status']}**\n")
        answers.append(f"- Minimum required: {f1['min_units']} units/semester")
        answers.append(f"- You're enrolled in: {f1['current_units']} units")
        if f1['current_units'] >= f1['min_units']:
            answers.append(f"✅ **You're compliant!** You meet the full-time enrollment requirement.")
        else:
            answers.append(f"⚠️ **Action needed:** You're below the minimum {f1['min_units']} units.")
        answers.append(f"\n**This semester's courses:**")
        for course in f1['required_courses_for_full_time'][:4]:
            answers.append(f"- {course}")
    
    # Advisor
    if any(word in question_lower for word in ['advisor', 'advis']):
        answers.append(f"## 👤 Your Advisor\n")
        answers.append(f"**Advisor: {student.advisor}**\n")
        answers.append(f"- Student ID: {student.sjsu_id}")
        answers.append(f"- To schedule: Book through Spartans Engage or visit the Advising Center")
        answers.append(f"- Bring your degree worksheet and updated plan")
    
    # Holds
    if any(word in question_lower for word in ['hold', 'block', 'restrict']):
        answers.append(f"## ⚠️ Account Holds\n")
        if student.holds:
            for hold in student.holds:
                answers.append(f"- 🚫 **{hold}**")
            answers.append(f"\n**Action:** Visit the specific office to resolve each hold")
        else:
            answers.append(f"✅ **No holds** on your account!")
    
    # GPA
    if any(word in question_lower for word in ['gpa', 'grade', 'gpa']):
        answers.append(f"## 📈 Your Academic Standing\n")
        answers.append(f"**Current GPA: {student.gpa}/4.0**\n")
        if student.gpa >= 3.5:
            answers.append(f"🎉 You're on the Dean's List! Great work!")
        elif student.gpa >= 3.0:
            answers.append(f"📊 Good standing - keep it up!")
        else:
            answers.append(f"📌 Meet with your advisor to discuss strategies")
    
    # Current courses
    if any(word in question_lower for word in ['current', 'enrolled', 'taking', 'class']):
        enrolled = [c for c in student.courses if c.status == 'enrolled']
        answers.append(f"## 📚 Your Current Courses\n")
        answers.append(f"**{student.units_in_progress} units this semester:**\n")
        for course in enrolled:
            answers.append(f"- **{course.code}**: {course.name} ({course.units} units)")
    
    # Remaining courses
    if any(word in question_lower for word in ['remaining', 'need to take', 'left', 'prerequisite']):
        answers.append(f"## 📝 Your Remaining Courses\n")
        if remaining_major:
            answers.append(f"**Major ({len(remaining_major)} courses):**")
            for c in remaining_major:
                answers.append(f"- {c}")
        if remaining_ge > 0:
            answers.append(f"\n**GE:** {remaining_ge} more units")
        if remaining_electives > 0:
            answers.append(f"**Electives:** {remaining_electives} more units")
    
    # Career/Electives
    if any(word in question_lower for word in ['career', 'job', 'internship', 'elective']):
        answers.append(f"## 💼 Career & Electives\n")
        answers.append(f"**{student.first_name}, based on your {student.major} major:**\n")
        
        if "Computer Science" in student.major or "Data Science" in student.major:
            answers.append(f"**Recommended electives for Software Engineering track:**")
            answers.append(f"- CS 256: Advanced Algorithms")
            answers.append(f"- CS 264: Mobile App Development")
            answers.append(f"- CS 272: Cybersecurity Fundamentals")
            answers.append(f"- CS 281: Blockchain Development")
            answers.append(f"\n**Career paths to explore:**")
            answers.append(f"- Software Engineer, Full-Stack Developer")
            answers.append(f"- Cloud Engineer, DevOps")
            answers.append(f"- Machine Learning Engineer")
        
        answers.append(f"\n**To improve employability:**")
        answers.append(f"1. Complete an internship (CS 297, CPT)")
        answers.append(f"2. Build a strong GitHub portfolio")
        answers.append(f"3. Practice LeetCode for interviews")
    
    # Default response if no specific match
    if not answers:
        answers.append(f"## 📋 Your Academic Summary\n")
        answers.append(f"**{student.first_name} {student.last_name}**\n")
        answers.append(f"- **Major:** {student.major}")
        if student.concentration:
            answers.append(f"- **Concentration:** {student.concentration}")
        answers.append(f"- **GPA:** {student.gpa}")
        answers.append(f"- **Units Completed:** {student.units_completed} + {student.units_in_progress} in progress = {total_completed}")
        answers.append(f"- **Remaining:** {remaining_units} units to graduate")
        answers.append(f"- **Expected Graduation:** {student.expected_graduation}")
        answers.append(f"- **Advisor:** {student.advisor}")
        if student.visa_status == 'f1':
            f1 = get_f1_requirements(student)
            answers.append(f"- **F-1 Status:** {f1['status']}")
        answers.append(f"\n💬 Ask me about your graduation, courses, F-1 status, or career!")
    
    return "\n".join(answers)


def get_quick_facts(student: Student) -> str:
    """Get quick facts summary for the student."""
    reqs = get_degree_requirements(student)
    total = student.units_completed + student.units_in_progress
    remaining = reqs['total_units'] - total
    
    facts = f"""
**🎓 {student.first_name} {student.last_name}**
- **Major:** {student.major} ({student.concentration})
- **GPA:** {student.gpa} | **Graduation:** {student.expected_graduation}
- **Progress:** {total}/{reqs['total_units']} units ({remaining} remaining)
- **Advisor:** {student.advisor}
"""
    if student.visa_status == 'f1':
        f1 = get_f1_requirements(student)
        facts += f"- **F-1:** {f1['status']}"
    
    return facts
