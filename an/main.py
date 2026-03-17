import streamlit as st
import pandas as pd
from data.student_data import get_student, get_degree_requirements, get_f1_requirements, get_student_context, Student
from data.knowledge_base import get_personalized_answer, get_quick_facts
from agents import route_question, handle_registrar_question, handle_career_question, handle_compliance_question
from utils.nvidia_client import chat
from professor_views import (
    render_professor_login,
    render_professor_dashboard,
    render_course_management,
)

st.set_page_config(page_title="🎓 SJSU AI Counselor", page_icon="🎓", layout="wide")

if "student" not in st.session_state:
    st.session_state.student = None
if "messages" not in st.session_state:
    st.session_state.messages = []
# Portal: None = landing, "student" = student login, "professor" = professor flow
if "portal" not in st.session_state:
    st.session_state.portal = None

def landing_section():
    """Choose Student or Professor portal (hackathon: both in one app)."""
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 30px 0;">
        <h1>🎓 SJSU Assistant</h1>
        <p style="font-size: 18px; color: #555;">Student counseling & professor course management</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Choose your portal")
        a, b = st.columns(2)
        with a:
            if st.button("🎓 **Student Login**", use_container_width=True, type="primary"):
                st.session_state.portal = "student"
                st.rerun()
        with b:
            if st.button("👩‍🏫 **Professor Portal**", use_container_width=True):
                st.session_state.portal = "professor"
                st.rerun()
        st.caption("Students: AI counselor, degree progress, F-1 status. Professors: waitlist & permission codes.")


def login_section():
    # Back to landing
    if st.button("← Back"):
        st.session_state.portal = None
        st.rerun()
    st.markdown("""
    <div style="text-align: center; padding: 30px 0 20px 0;">
        <h1>🎓 Welcome to SJSU AI Counselor</h1>
        <p style="font-size: 18px; color: #666;">Your personal AI assistant for navigating SJSU</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login with SJSU Email")
        email = st.text_input("Email", placeholder="alex.chen@sjsu.edu")
        
        demo_accounts = """
        **Demo Accounts:**
        - `alex.chen@sjsu.edu` - CS, F-1 Visa (Senior)
        - `priya.patel@sjsu.edu` - Data Science, F-1 Visa (Graduate)  
        - `james.wilson@sjsu.edu` - Business Analytics, Domestic
        """
        st.info(demo_accounts)
        
        if st.button("Login", type="primary"):
            if email:
                student = get_student(email)
                if student:
                    st.session_state.student = student
                    st.rerun()
                else:
                    st.error("Student not found. Try a demo account.")
            else:
                st.error("Please enter your SJSU email.")

def show_dashboard(student: Student):
    with st.sidebar:
        st.markdown(f"### 👤 {student.first_name} {student.last_name}")
        st.markdown(f"**ID:** {student.sjsu_id}")
        st.markdown(f"**Email:** {student.email}")
        st.markdown(f"**Major:** {student.major}")
        if student.concentration:
            st.markdown(f"**Concentration:** {student.concentration}")
        
        st.divider()
        
        if st.button("🚪 Logout"):
            st.session_state.student = None
            st.session_state.messages = []
            st.rerun()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "📚 Courses", "🎯 Degree Progress", "🛂 F-1 Status", "💬 AI Assistant"
    ])
    
    with tab1:
        show_overview(student)
    
    with tab2:
        show_courses(student)
    
    with tab3:
        show_degree_progress(student)
    
    with tab4:
        if student.visa_status == "f1":
            show_f1_status(student)
        else:
            st.info("This tab is for F-1 international students only.")
    
    with tab5:
        show_ai_assistant(student)

def show_overview(student: Student):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("GPA", f"{student.gpa:.2f}/4.0", delta="Dean's List" if student.gpa >= 3.5 else None)
    with col2:
        st.metric("Units Completed", student.units_completed)
    with col3:
        st.metric("Units In Progress", student.units_in_progress)
    with col4:
        st.metric("Expected Graduation", student.expected_graduation)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Academic Info")
        info = {
            "Catalog Year": student.catalog_year,
            "Major": student.major,
            "Concentration": student.concentration or "N/A",
            "Advisor": student.advisor,
            "Enrollment Status": student.enrollment_status,
            "Visa Status": student.visa_status.upper()
        }
        df = pd.DataFrame(info.items(), columns=["Field", "Value"])
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Holds")
        if student.holds:
            for hold in student.holds:
                st.error(f"🚫 {hold}")
        else:
            st.success("✅ No holds on your account")

def show_courses(student: Student):
    st.subheader("📚 Current & Completed Courses")
    
    enrolled = [c for c in student.courses if c.status == "enrolled"]
    completed = [c for c in student.courses if c.status == "completed"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎒 Currently Enrolled")
        if enrolled:
            for course in enrolled:
                st.info(f"**{course.code}** - {course.name} ({course.units} units)")
        else:
            st.info("No courses currently enrolled")
    
    with col2:
        st.markdown("### ✅ Completed")
        if completed:
            df = pd.DataFrame([
                {"Course": c.code, "Name": c.name, "Grade": c.grade, "Units": c.units, "Term": c.term}
                for c in completed
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No completed courses")

def show_degree_progress(student: Student):
    reqs = get_degree_requirements(student)
    
    total = reqs["total_units"]
    completed = student.units_completed + student.units_in_progress
    remaining = total - completed
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Units Required", total)
    with col2:
        st.metric("Units Completed", completed, delta=f"{completed/total*100:.1f}%")
    with col3:
        st.metric("Units Remaining", remaining, delta=f"-{remaining}")
    
    st.subheader("📈 Progress by Category")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ge_pct = reqs["current"]["ge"] / reqs["ge_units"] * 100
        st.progress(min(ge_pct/100, 1.0))
        st.caption(f"GE: {reqs['current']['ge']}/{reqs['ge_units']} units ({ge_pct:.1f}%)")
    with col2:
        major_pct = reqs["current"]["major"] / reqs["major_units"] * 100
        st.progress(min(major_pct/100, 1.0))
        st.caption(f"Major: {reqs['current']['major']}/{reqs['major_units']} units ({major_pct:.1f}%)")
    with col3:
        elective_pct = reqs["current"]["elective"] / reqs["elective_units"] * 100
        st.progress(min(elective_pct/100, 1.0))
        st.caption(f"Electives: {reqs['current']['elective']}/{reqs['elective_units']} units ({elective_pct:.1f}%)")
    
    st.subheader("📝 Remaining Major Courses")
    remaining_courses = reqs["courses"]["remaining"]
    if remaining_courses:
        for course in remaining_courses:
            st.markdown(f"- **{course}**")
    else:
        st.success("🎉 All major courses completed!")

def show_f1_status(student: Student):
    f1 = get_f1_requirements(student)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Minimum Units Required", f1["min_units"])
        st.metric("Current Units", f1["current_units"])
    
    with col2:
        status_color = "success" if "✅" in f1["status"] else "error"
        st.markdown(f"**Status:** {f1['status']}")
    
    st.subheader("📋 This Semester's Full-Time Enrollment")
    for course in f1["required_courses_for_full_time"]:
        st.markdown(f"- {course}")
    
    if f1["recommended_actions"]:
        st.subheader("💡 Recommended Actions")
        for action in f1["recommended_actions"]:
            st.markdown(f"- {action}")
    
    st.info("📅 **Next Semester Enrollment Deadline:** " + f1["next_semester_deadline"])
    
    st.warning("⚠️ Please verify all information with ISS (International Student Services) for official guidance.")

def show_ai_assistant(student: Student):
    st.subheader("💬 Ask Your Personal AI Counselor")
    
    quick_facts = get_quick_facts(student)
    st.info(quick_facts)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about YOUR courses, graduation, F-1 status, advisor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Looking up YOUR specific information..."):
                response = get_personalized_answer(student, prompt)
                st.markdown(response)
                full_response = response
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    # Student logged in: show student dashboard
    if st.session_state.student:
        show_dashboard(st.session_state.student)
    # Professor portal flow
    elif st.session_state.portal == "professor":
        if "professor_page" not in st.session_state:
            st.session_state.professor_page = "login"
        if st.session_state.professor_page == "login":
            render_professor_login()
        elif st.session_state.professor_page == "dashboard":
            render_professor_dashboard()
        else:
            render_course_management()
    # Student portal: show student login
    elif st.session_state.portal == "student":
        login_section()
    # Landing: choose Student or Professor
    else:
        landing_section()
