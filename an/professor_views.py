"""
Professor Portal UI: login, dashboard, and course waitlist / permission code management.
Renders Streamlit views and uses session state for navigation and mutable course data.
"""

import streamlit as st
from typing import Dict, Any, List, Optional

from data.mock_professors import get_professor_by_credentials
from data.mock_courses import get_courses_for_professor
from utils.permission_code import (
    auto_grant_permission_codes,
    generate_permission_code,
)


# ---------- Session state keys ----------
def _ensure_professor_state():
    if "professor_user" not in st.session_state:
        st.session_state.professor_user = None
    if "professor_page" not in st.session_state:
        st.session_state.professor_page = "login"
    if "professor_courses" not in st.session_state:
        st.session_state.professor_courses = []
    if "selected_course_id" not in st.session_state:
        st.session_state.selected_course_id = None
    if "permission_code_history" not in st.session_state:
        st.session_state.permission_code_history = []


def _get_current_course() -> Optional[Dict[str, Any]]:
    """Get the selected course dict from professor_courses (mutable)."""
    cid = st.session_state.get("selected_course_id")
    if not cid:
        return None
    for c in st.session_state.get("professor_courses", []):
        if c["id"] == cid:
            return c
    return None


# ---------- Professor Login ----------
def render_professor_login():
    _ensure_professor_state()
    if st.button("← Back to home", key="prof_back_home"):
        st.session_state.portal = None
        st.session_state.professor_user = None
        st.session_state.professor_page = "login"
        st.rerun()
    st.markdown("""
    <div style="text-align: center; padding: 30px 0 20px 0;">
        <h1>👩‍🏫 Professor Portal</h1>
        <p style="font-size: 16px; color: #555;">Manage your courses and waitlist permission codes</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("### 🔐 Sign in")
            email = st.text_input("Email", placeholder="sarah.johnson@sjsu.edu", key="prof_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="prof_password")
            st.caption("Demo credentials (no real auth):")
            st.code("sarah.johnson@sjsu.edu / prof123\nmichael.lee@sjsu.edu / prof456", language=None)
            if st.button("Login", type="primary", key="prof_login_btn"):
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    professor = get_professor_by_credentials(email.strip(), password)
                    if professor:
                        st.session_state.professor_user = professor
                        st.session_state.professor_courses = get_courses_for_professor(professor["id"])
                        st.session_state.professor_page = "dashboard"
                        st.session_state.selected_course_id = None
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Try a demo account above.")


# ---------- Professor Dashboard ----------
def render_professor_dashboard():
    _ensure_professor_state()
    prof = st.session_state.get("professor_user")
    if not prof:
        st.session_state.professor_page = "login"
        st.rerun()
        return

    with st.sidebar:
        st.markdown(f"### 👩‍🏫 {prof['name']}")
        st.markdown(f"**Dept:** {prof['department']}")
        st.markdown(f"**Email:** {prof['email']}")
        st.divider()
        if st.button("🚪 Logout", key="prof_logout"):
            st.session_state.professor_user = None
            st.session_state.professor_courses = []
            st.session_state.professor_page = "login"
            st.session_state.selected_course_id = None
            st.session_state.portal = None  # Return to landing
            st.rerun()

    st.markdown(f"## Welcome, {prof['name']}")
    st.markdown("Manage your courses, view seat availability, and grant permission codes to waitlisted students.")
    st.divider()

    courses = st.session_state.get("professor_courses", [])
    if not courses:
        st.info("You have no courses assigned.")
        return

    for course in courses:
        available = max(0, course["total_seats"] - course["enrolled_count"])
        waitlist_count = len(course.get("waitlist", []))
        waiting_count = len([s for s in course.get("waitlist", []) if s.get("status") == "waiting"])

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.subheader(f"{course['course_code']} — {course['title']}")
                st.caption(f"Section {course['section']} · {course['semester']}")
            with col2:
                st.metric("Seats", f"{course['enrolled_count']}/{course['total_seats']}")
                st.metric("Available", available)
            with col3:
                st.metric("Waitlist", waitlist_count)
                if waiting_count < waitlist_count:
                    st.caption(f"({waiting_count} waiting)")

            if st.button("Manage Waitlist", key=f"manage_{course['id']}"):
                st.session_state.selected_course_id = course["id"]
                st.session_state.professor_page = "course_management"
                st.rerun()
            st.divider()


# ---------- Course Management (Waitlist + Permission Codes) ----------
def _add_audit_entry(student_name: str, student_id: str, course_code: str, professor_name: str, permission_code: str):
    import datetime
    st.session_state.permission_code_history.append({
        "student_name": student_name,
        "student_id": student_id,
        "course_code": course_code,
        "professor_name": professor_name,
        "permission_code": permission_code,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    })


def render_course_management():
    _ensure_professor_state()
    prof = st.session_state.get("professor_user")
    course = _get_current_course()
    if not prof or not course:
        st.session_state.professor_page = "dashboard"
        st.session_state.selected_course_id = None
        st.rerun()
        return

    # Back to dashboard
    if st.button("← Back to Dashboard", key="back_to_dashboard"):
        st.session_state.professor_page = "dashboard"
        st.session_state.selected_course_id = None
        st.rerun()

    st.markdown(f"## {course['course_code']} — {course['title']}")
    st.caption(f"Section {course['section']} · {course['semester']} · {prof['name']}")

    available = max(0, course["total_seats"] - course["enrolled_count"])
    waitlist = course.get("waitlist", [])
    waiting = [s for s in waitlist if s.get("status") == "waiting"]
    approved = [s for s in waitlist if s.get("status") == "approved"]
    denied = [s for s in waitlist if s.get("status") == "denied"]

    # Summary cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Seats", course["total_seats"])
    c2.metric("Enrolled", course["enrolled_count"])
    c3.metric("Available Seats", available)
    c4.metric("Waitlist", len(waitlist))

    can_issue = available > 0 and len(waiting) > 0
    if can_issue:
        st.success(f"Permission codes can be issued. There are **{available}** seat(s) available and **{len(waiting)}** student(s) waiting.")
    else:
        if available == 0:
            st.warning("No available seats. Permission codes cannot be issued until seats open.")
        elif len(waiting) == 0:
            st.info("No students currently waiting on the waitlist.")

    # Fairness banner
    st.info("Students are prioritized by waitlist order. Final enrollment decisions remain subject to instructor and department policy.")

    # Auto-grant button
    if st.button("Auto-Grant to Top Waitlisted Students", type="primary", key="auto_grant_btn"):
        count, granted = auto_grant_permission_codes(course)
        for s in granted:
            _add_audit_entry(s["name"], s["student_id"], course["course_code"], prof["name"], s["permission_code"])
        if count > 0:
            st.success(f"**{count}** permission code(s) granted successfully. Students can use their codes to enroll.")
            st.toast("Permission codes issued and ready to send to students.")
        else:
            st.warning("No codes granted. Either no available seats or no eligible waiting students.")
        st.rerun()

    # Search/filter and sort
    st.subheader("Waitlisted Students")
    search = st.text_input("Search by name or ID", key="waitlist_search", placeholder="e.g. Alex or 012345678")
    sort_by = st.selectbox(
        "Sort by",
        ["Waitlist position", "GPA (high first)", "Standing", "Request date"],
        key="waitlist_sort",
    )

    # Filter by search
    filtered_waitlist = waitlist
    if search:
        q = search.strip().lower()
        filtered_waitlist = [
            s for s in waitlist
            if q in (s.get("name") or "").lower() or q in (s.get("student_id") or "")
        ]

    # Build display list and sort
    def sort_key(s):
        if sort_by == "Waitlist position":
            return (0, s.get("waitlist_position", 999))
        if sort_by == "GPA (high first)":
            return (1, -s.get("gpa", 0))
        if sort_by == "Standing":
            order = {"Master's": 0, "Senior": 1, "Junior": 2, "Sophomore": 3, "Freshman": 4}
            return (2, order.get(s.get("standing", ""), 5))
        return (3, s.get("request_timestamp", ""))

    sorted_waitlist = sorted(filtered_waitlist, key=sort_key)

    # Table / rows
    for s in sorted_waitlist:
        status = s.get("status", "waiting")
        if status == "approved":
            badge = "🟢 Approved"
            expander_label = f"#{s.get('waitlist_position')} — {s.get('name')} — Approved"
        elif status == "denied":
            badge = "🔴 Denied"
            expander_label = f"#{s.get('waitlist_position')} — {s.get('name')} — Denied"
        else:
            badge = "🟡 Waiting"
            expander_label = f"#{s.get('waitlist_position')} — {s.get('name')} — Waiting"

        with st.expander(expander_label):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {s.get('name')}  \n**ID:** {s.get('student_id')}  \n**Major:** {s.get('major')}  \n**Standing:** {s.get('standing')}")
            with col2:
                st.markdown(f"**GPA:** {s.get('gpa')}  \n**Units completed:** {s.get('units_completed')}  \n**Requested:** {s.get('request_timestamp')}")
                if s.get("priority_tag"):
                    st.caption(f"Priority: {s['priority_tag']}")
            st.markdown(f"**Status:** {badge}")
            if s.get("permission_code"):
                st.code(s["permission_code"], language=None)
                if st.button("Copy permission code", key=f"copy_{s['id']}"):
                    st.toast(f"Permission code copied: {s['permission_code']}")
            # Manual actions (only for waiting students)
            if status == "waiting":
                sub1, sub2 = st.columns(2)
                with sub1:
                    if st.button("Approve", key=f"approve_{s['id']}"):
                        code = generate_permission_code(course["course_code"])
                        s["permission_code"] = code
                        s["status"] = "approved"
                        _add_audit_entry(s["name"], s["student_id"], course["course_code"], prof["name"], code)
                        st.rerun()
                with sub2:
                    if st.button("Deny", key=f"deny_{s['id']}"):
                        s["status"] = "denied"
                        st.rerun()
            if status == "approved":
                if st.button("Revoke approval", key=f"revoke_{s['id']}"):
                    s["status"] = "waiting"
                    s["permission_code"] = None
                    st.rerun()

    # Summary
    st.divider()
    st.markdown("**Summary** · Seats available: **{}** · Approved: **{}** · Waiting: **{}** · Denied: **{}**".format(
        available, len(approved), len(waiting), len(denied)))

    # Permission Code History / Audit Panel
    st.subheader("Permission Code History")
    history = st.session_state.get("permission_code_history", [])
    # Filter to this course for clarity in demo
    course_history = [h for h in history if h.get("course_code") == course["course_code"]]
    if not course_history:
        st.caption("No permission codes granted yet for this course.")
    else:
        for h in course_history:
            st.markdown(f"- **{h['student_name']}** ({h['student_id']}) — `{h['permission_code']}` — {h['timestamp']}")
