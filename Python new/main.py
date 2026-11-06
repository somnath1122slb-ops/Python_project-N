
import os
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Campus Event Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. PROFESSIONAL UI DESIGN
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F4F6FB;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* Headings */

h1, h2, h3 {
    color: #172554 !important;
    font-weight: 750 !important;
}

p {
    color: #64748B;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #172554, #312E81);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,0.06);
    padding: 10px 12px;
    border-radius: 9px;
    margin-bottom: 5px;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.15);
}

/* Metric cards */

div[data-testid="stMetric"] {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 12px rgba(15,23,42,0.04);
}

div[data-testid="stMetricLabel"] {
    color: #64748B;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #312E81;
    font-weight: 800;
}

/* Buttons */

.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(90deg, #4F46E5, #6366F1);
    color: white !important;
    border: none;
    border-radius: 9px;
    padding: 9px 20px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: #3730A3;
    transform: translateY(-1px);
}

/* Inputs */

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

/* Dataframes */

[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

/* Tabs */

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
}

/* Dashboard banner */

.dashboard-banner {
    background: linear-gradient(110deg, #312E81, #4F46E5);
    padding: 28px;
    border-radius: 17px;
    color: white;
    margin-bottom: 25px;
}

.dashboard-banner h2 {
    color: white !important;
    margin: 0;
}

.dashboard-banner p {
    color: #E0E7FF !important;
    margin-bottom: 0;
}

hr {
    border-color: #E2E8F0;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. CUSTOM EXCEPTIONS
# =====================================================

class EventNotFoundError(Exception):
    pass


class EventFullError(Exception):
    pass


class DuplicateRegistrationError(Exception):
    pass


class RegistrationNotFoundError(Exception):
    pass


# =====================================================
# 4. CSV FILE PATHS
# =====================================================

EVENTS_FILE = "events.csv"
STUDENTS_FILE = "students.csv"
REGISTRATIONS_FILE = "registrations.csv"


# =====================================================
# 5. OOP CLASSES
# =====================================================

class Event:

    def __init__(self, event_id, name, event_date, venue, max_participants):
        self.event_id = str(event_id)
        self.name = str(name)
        self.date = str(event_date)
        self.venue = str(venue)
        self.max_participants = int(max_participants)

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "name": self.name,
            "date": self.date,
            "venue": self.venue,
            "max_participants": self.max_participants
        }


class Student:

    def __init__(self, student_id, name, email):
        self.student_id = str(student_id)
        self.name = str(name)
        self.email = str(email)

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email
        }


class Registration:

    def __init__(self, registration_id, event_id, student_id, rating=None):
        self.registration_id = str(registration_id)
        self.event_id = str(event_id)
        self.student_id = str(student_id)
        self.rating = rating

    def to_dict(self):
        return {
            "registration_id": self.registration_id,
            "event_id": self.event_id,
            "student_id": self.student_id,
            "rating": self.rating if self.rating is not None else ""
        }


# =====================================================
# 6. CSV FILE HANDLING
# =====================================================

def read_csv_file(filename, columns):

    if os.path.exists(filename):

        try:
            df = pd.read_csv(filename, dtype=str)

            for col in columns:
                if col not in df.columns:
                    df[col] = ""

            return df[columns].fillna("")

        except pd.errors.EmptyDataError:
            pass

    return pd.DataFrame(columns=columns)


def load_data():

    events = read_csv_file(
        EVENTS_FILE,
        ["event_id", "name", "date", "venue", "max_participants"]
    )

    students = read_csv_file(
        STUDENTS_FILE,
        ["student_id", "name", "email"]
    )

    registrations = read_csv_file(
        REGISTRATIONS_FILE,
        ["registration_id", "event_id", "student_id", "rating"]
    )

    return events, students, registrations


def save_data():

    st.session_state.events_df.to_csv(
        EVENTS_FILE, index=False
    )

    st.session_state.students_df.to_csv(
        STUDENTS_FILE, index=False
    )

    st.session_state.regs_df.to_csv(
        REGISTRATIONS_FILE, index=False
    )


# =====================================================
# 7. EVENT ID GENERATION
# =====================================================

def generate_event_id():

    events_df = st.session_state.events_df

    if events_df.empty:
        return "E001"

    existing_ids = events_df["event_id"].astype(str)

    numbers = []

    for eid in existing_ids:

        if eid.startswith("E") and eid[1:].isdigit():
            numbers.append(int(eid[1:]))

    next_number = max(numbers, default=0) + 1

    return f"E{next_number:03d}"


# =====================================================
# 8. EVENT STATUS MANAGEMENT
# =====================================================

def get_event_status(event_date):

    try:

        event_date = pd.to_datetime(event_date).date()

        today = date.today()

        if event_date < today:
            return "Completed / Expired"

        elif event_date == today:
            return "Ongoing / Today"

        else:
            return "Upcoming"

    except (ValueError, TypeError):
        return "Unknown"


def is_event_expired(event_date):

    try:
        return pd.to_datetime(event_date).date() < date.today()

    except (ValueError, TypeError):
        return True


# =====================================================
# 9. FIXED EVENT TIMELINE
# NO HTML - ONLY NATIVE STREAMLIT COMPONENTS
# =====================================================

def display_event_timeline(events_df):

    st.subheader("Event Timeline")

    if events_df.empty:
        st.info("No events available.")
        return

    sorted_events = events_df.copy()

    sorted_events["_date"] = pd.to_datetime(
        sorted_events["date"],
        errors="coerce"
    )

    sorted_events = sorted_events.sort_values(
        "_date",
        ascending=True
    )

    for _, event in sorted_events.iterrows():

        status = get_event_status(event["date"])

        # Native Streamlit event card
        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.subheader(str(event["name"]))

                st.caption(
                    f"Event ID: {event['event_id']}"
                )

            with col2:

                if status == "Upcoming":
                    st.info("Upcoming")

                elif status == "Ongoing / Today":
                    st.warning("Today")

                else:
                    st.success("Completed")

            st.divider()

            c1, c2, c3 = st.columns(3)

            with c1:

                st.markdown("**Date**")

                st.write(str(event["date"]))

            with c2:

                st.markdown("**Venue**")

                st.write(str(event["venue"]))

            with c3:

                st.markdown("**Maximum Participants**")

                st.write(str(event["max_participants"]))


# =====================================================
# 10. INITIALIZE SESSION STATE
# =====================================================

if "events_df" not in st.session_state:

    events, students, registrations = load_data()

    st.session_state.events_df = events

    st.session_state.students_df = students

    st.session_state.regs_df = registrations


# =====================================================
# 11. SIDEBAR
# =====================================================

with st.sidebar:

    st.title("CAMPUS")
    st.caption("Event Management System")

    st.markdown("---")

    menu = [
        "Analytics Dashboard",
        "Create Event",
        "Student Registration",
        "Submit Feedback",
        "View Stored Files",
        "Search Registered Students",
        "Cancel Registration"
    ]

    choice = st.radio(
        "MAIN MENU",
        menu,
        label_visibility="visible"
    )

    st.markdown("---")

    st.caption("Campus Management System")
    st.caption("Version 3.0")


# =====================================================
# 12. ANALYTICS DASHBOARD
# =====================================================

if choice == "Analytics Dashboard":

    st.title("Campus Event Analytics Dashboard")
    st.write(
        "Monitor events, student participation and feedback "
        "through interactive analytics."
    )

    events_df = st.session_state.events_df
    students_df = st.session_state.students_df
    regs_df = st.session_state.regs_df

    total_events = len(events_df)
    total_regs = len(regs_df)

    unique_students = (
        regs_df["student_id"].nunique()
        if not regs_df.empty else 0
    )

    if not events_df.empty:

        expired_count = sum(
            is_event_expired(d)
            for d in events_df["date"]
        )

        today_count = sum(
            get_event_status(d) == "Ongoing / Today"
            for d in events_df["date"]
        )

        upcoming_count = (
            total_events - expired_count - today_count
        )

    else:

        expired_count = 0
        today_count = 0
        upcoming_count = 0

    if not regs_df.empty:

        ratings = pd.to_numeric(
            regs_df["rating"],
            errors="coerce"
        ).dropna()

        avg_rating = (
            ratings.mean() if not ratings.empty else 0
        )

    else:

        ratings = pd.Series(dtype=float)
        avg_rating = 0

    # Main metrics

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Events", total_events)

    c2.metric("Total Registrations", total_regs)

    c3.metric("Unique Students", unique_students)

    c4.metric(
        "Average Rating",
        f"{avg_rating:.2f}/5" if avg_rating > 0 else "N/A"
    )

    # Event status

    st.markdown("### Event Status Overview")

    s1, s2, s3 = st.columns(3)

    s1.metric("Upcoming Events", upcoming_count)

    s2.metric("Today's Events", today_count)

    s3.metric("Completed / Expired", expired_count)

    st.markdown("---")

    # Charts

    if not events_df.empty:

        tab1, tab2, tab3 = st.tabs([
            "Event Participation",
            "Average Ratings",
            "Rating Distribution"
        ])

        # Participation chart

        with tab1:

            event_counts = (
                regs_df.groupby("event_id")
                .size()
                .reset_index(name="participants")
                if not regs_df.empty
                else pd.DataFrame(
                    columns=["event_id", "participants"]
                )
            )

            merged = pd.merge(
                events_df,
                event_counts,
                on="event_id",
                how="left"
            )

            merged["participants"] = (
                merged["participants"].fillna(0)
            )

            fig1 = px.bar(
                merged,
                x="name",
                y="participants",
                color="participants",
                text_auto=True,
                title="Event-wise Student Participation",
                color_continuous_scale="Purples"
            )

            fig1.update_layout(
                template="plotly_white",
                xaxis_title="Event Name",
                yaxis_title="Participants"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        # Average ratings chart

        with tab2:

            if not regs_df.empty:

                temp = regs_df.copy()

                temp["rating"] = pd.to_numeric(
                    temp["rating"],
                    errors="coerce"
                )

                avg_df = (
                    temp.groupby("event_id")["rating"]
                    .mean()
                    .reset_index()
                )

            else:

                avg_df = pd.DataFrame(
                    columns=["event_id", "rating"]
                )

            merged = pd.merge(
                events_df,
                avg_df,
                on="event_id",
                how="left"
            )

            fig2 = px.bar(
                merged,
                x="name",
                y="rating",
                text_auto=".2f",
                color="rating",
                title="Average Feedback Rating",
                color_continuous_scale="Purples"
            )

            fig2.update_layout(
                template="plotly_white",
                yaxis=dict(range=[0, 5.2])
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        # Rating distribution

        with tab3:

            if not ratings.empty:

                rating_df = pd.DataFrame({
                    "rating": ratings
                })

                fig3 = px.histogram(
                    rating_df,
                    x="rating",
                    nbins=9,
                    title="Feedback Rating Distribution",
                    color_discrete_sequence=["#6366F1"]
                )

                fig3.update_layout(
                    template="plotly_white",
                    xaxis=dict(range=[0.5, 5.5])
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True
                )

            else:

                st.info(
                    "No feedback ratings available yet."
                )

    else:

        st.info(
            "Create your first event to view analytics."
        )

    # Event Timeline

    st.markdown("---")

    display_event_timeline(events_df)


# =====================================================
# 13. CREATE EVENT
# =====================================================

elif choice == "Create Event":

    st.title("Create New Event")

    st.write(
        "Create a campus event and automatically generate its Event ID."
    )

    next_event_id = generate_event_id()

    st.info(
        f"Automatically Generated Event ID: **{next_event_id}**"
    )

    with st.form(
        "create_event_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            event_name = st.text_input("Event Name")

            event_date = st.date_input(
                "Event Date",
                min_value=date.today()
            )

        with col2:

            venue = st.text_input("Event Venue")

            max_participants = st.number_input(
                "Maximum Participants",
                min_value=1,
                max_value=10000,
                value=50
            )

        submitted = st.form_submit_button(
            "Create Event",
            use_container_width=True
        )

        if submitted:

            try:

                if not event_name.strip():
                    raise ValueError(
                        "Event Name cannot be empty."
                    )

                if not venue.strip():
                    raise ValueError(
                        "Venue cannot be empty."
                    )

                eid = generate_event_id()

                new_event = Event(
                    eid,
                    event_name.strip(),
                    event_date,
                    venue.strip(),
                    max_participants
                )

                new_df = pd.DataFrame([
                    new_event.to_dict()
                ])

                st.session_state.events_df = pd.concat(
                    [
                        st.session_state.events_df,
                        new_df
                    ],
                    ignore_index=True
                )

                save_data()

                st.success(
                    f"Event created successfully! Event ID: {eid}"
                )

            except Exception as e:

                st.error(f"Error: {e}")

    st.markdown("---")

    st.subheader("Existing Events")

    display_event_timeline(
        st.session_state.events_df
    )


# =====================================================
# 14. STUDENT REGISTRATION
# =====================================================

elif choice == "Student Registration":

    st.title("Student Registration Portal")

    st.write(
        "Register students for available campus events."
    )

    events_df = st.session_state.events_df

    if events_df.empty:

        st.warning(
            "Please create an event first."
        )

    else:

        active_events = events_df[
            ~events_df["date"].apply(is_event_expired)
        ].copy()

        if active_events.empty:

            st.warning(
                "There are no upcoming or today's events available for registration."
            )

            st.subheader("Event Timeline")

            display_event_timeline(events_df)

        else:

            event_dict = {
                f"{row['name']} ({row['event_id']})":
                str(row["event_id"])
                for _, row in active_events.iterrows()
            }

            with st.form(
                "registration_form",
                clear_on_submit=True
            ):

                col1, col2 = st.columns(2)

                with col1:

                    sid = st.text_input(
                        "Student ID"
                    ).strip()

                    sname = st.text_input(
                        "Student Name"
                    ).strip()

                with col2:

                    semail = st.text_input(
                        "Student Email"
                    ).strip()

                    selected_event = st.selectbox(
                        "Select Event",
                        list(event_dict.keys())
                    )

                submitted = st.form_submit_button(
                    "Complete Registration",
                    use_container_width=True
                )

                if submitted:

                    try:

                        if not sid or not sname or not semail:

                            raise ValueError(
                                "All student details are required."
                            )

                        if "@" not in semail or "." not in semail:

                            raise ValueError(
                                "Please enter a valid email address."
                            )

                        eid = event_dict[selected_event]

                        current_events = (
                            st.session_state.events_df
                        )

                        event_info = current_events[
                            current_events["event_id"] == eid
                        ].iloc[0]

                        if is_event_expired(event_info["date"]):

                            raise ValueError(
                                "This event has already expired."
                            )

                        regs_df = st.session_state.regs_df

                        students_df = (
                            st.session_state.students_df
                        )

                        current_count = len(
                            regs_df[
                                regs_df["event_id"] == eid
                            ]
                        )

                        capacity = int(
                            event_info["max_participants"]
                        )

                        if current_count >= capacity:

                            raise EventFullError(
                                f"Event is full. Maximum capacity: {capacity}"
                            )

                        duplicate = regs_df[
                            (regs_df["event_id"] == eid) &
                            (regs_df["student_id"] == sid)
                        ]

                        if not duplicate.empty:

                            raise DuplicateRegistrationError(
                                "Student is already registered for this event."
                            )

                        existing_student = students_df[
                            students_df["student_id"] == sid
                        ]

                        if existing_student.empty:

                            new_student = Student(
                                sid,
                                sname,
                                semail
                            )

                            st.session_state.students_df = pd.concat(
                                [
                                    students_df,
                                    pd.DataFrame([
                                        new_student.to_dict()
                                    ])
                                ],
                                ignore_index=True
                            )

                        else:

                            old_email = str(
                                existing_student.iloc[0]["email"]
                            )

                            if old_email != semail:

                                raise ValueError(
                                    "This Student ID is already associated with another email address."
                                )

                        reg_id = (
                            f"REG{len(regs_df) + 1:03d}"
                        )

                        new_registration = Registration(
                            reg_id,
                            eid,
                            sid
                        )

                        st.session_state.regs_df = pd.concat(
                            [
                                regs_df,
                                pd.DataFrame([
                                    new_registration.to_dict()
                                ])
                            ],
                            ignore_index=True
                        )

                        save_data()

                        st.success(
                            f"{sname} successfully registered for {event_info['name']}!"
                        )

                        st.info(
                            f"Registration ID: {reg_id}"
                        )

                    except Exception as e:

                        st.error(
                            f"Registration Error: {e}"
                        )

            st.markdown("---")

            st.subheader("Event Availability")

            for _, event in active_events.iterrows():

                registered = len(
                    st.session_state.regs_df[
                        st.session_state.regs_df["event_id"]
                        == event["event_id"]
                    ]
                )

                capacity = int(
                    event["max_participants"]
                )

                st.write(
                    f"**{event['name']}** — "
                    f"{registered}/{capacity} participants"
                )

                st.progress(
                    min(registered / capacity, 1.0)
                )


# =====================================================
# 15. SUBMIT FEEDBACK
# =====================================================

elif choice == "Submit Feedback":

    st.title("Feedback & Rating Collection")

    st.write(
        "Collect ratings from students who registered for campus events."
    )

    regs_df = st.session_state.regs_df

    if regs_df.empty:

        st.info(
            "No student registrations found."
        )

    else:

        with st.form(
            "feedback_form",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)

            with col1:

                sid = st.text_input(
                    "Student ID"
                ).strip()

                eid = st.text_input(
                    "Event ID"
                ).strip()

            with col2:

                rating = st.slider(
                    "Rating Stars",
                    min_value=1.0,
                    max_value=5.0,
                    value=5.0,
                    step=0.5
                )

            submitted = st.form_submit_button(
                "Submit Feedback",
                use_container_width=True
            )

            if submitted:

                try:

                    if not sid or not eid:

                        raise ValueError(
                            "Student ID and Event ID are required."
                        )

                    if eid not in st.session_state.events_df[
                        "event_id"
                    ].astype(str).values:

                        raise EventNotFoundError(
                            "Invalid Event ID."
                        )

                    mask = (
                        (st.session_state.regs_df["student_id"] == sid) &
                        (st.session_state.regs_df["event_id"] == eid)
                    )

                    if st.session_state.regs_df[mask].empty:

                        raise RegistrationNotFoundError(
                            "Student is not registered for this event."
                        )

                    st.session_state.regs_df.loc[
                        mask, "rating"
                    ] = rating

                    save_data()

                    st.success(
                        "Feedback rating submitted successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"Feedback Error: {e}"
                    )


# =====================================================
# 16. VIEW STORED FILES
# =====================================================

elif choice == "View Stored Files":

    st.title("Stored Information Explorer")

    st.write(
        "View all records saved in the CSV storage files."
    )

    tab1, tab2, tab3 = st.tabs([
        "Events Data",
        "Students Data",
        "Registrations & Ratings"
    ])

    with tab1:

        st.subheader("Events Information")

        st.dataframe(
            st.session_state.events_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Events CSV",
            st.session_state.events_df.to_csv(index=False),
            "events.csv",
            "text/csv"
        )

    with tab2:

        st.subheader("Students Information")

        st.dataframe(
            st.session_state.students_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Students CSV",
            st.session_state.students_df.to_csv(index=False),
            "students.csv",
            "text/csv"
        )

    with tab3:

        st.subheader("Registration Information")

        st.dataframe(
            st.session_state.regs_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Registrations CSV",
            st.session_state.regs_df.to_csv(index=False),
            "registrations.csv",
            "text/csv"
        )


# =====================================================
# 17. SEARCH REGISTERED STUDENTS
# =====================================================

elif choice == "Search Registered Students":

    st.title("Search Registered Students")

    st.write(
        "Find students registered for a particular campus event."
    )

    events_df = st.session_state.events_df

    if events_df.empty:

        st.info(
            "No events available."
        )

    else:

        event_dict = {
            f"{row['name']} ({row['event_id']})":
            str(row["event_id"])
            for _, row in events_df.iterrows()
        }

        selected_label = st.selectbox(
            "Select Event",
            list(event_dict.keys())
        )

        selected_eid = event_dict[selected_label]

        if st.button(
            "Search Records",
            use_container_width=True
        ):

            event_regs = st.session_state.regs_df[
                st.session_state.regs_df["event_id"] == selected_eid
            ]

            if event_regs.empty:

                st.info(
                    "No students registered for this event."
                )

            else:

                merged = pd.merge(
                    event_regs,
                    st.session_state.students_df,
                    on="student_id",
                    how="left"
                )

                merged = merged.rename(
                    columns={
                        "name": "Student Name",
                        "email": "Student Email",
                        "student_id": "Student ID",
                        "registration_id": "Registration ID"
                    }
                )

                st.success(
                    f"{len(merged)} registration(s) found."
                )

                st.dataframe(
                    merged[
                        [
                            "Student ID",
                            "Student Name",
                            "Student Email",
                            "Registration ID"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )


# =====================================================
# 18. CANCEL REGISTRATION
# =====================================================

elif choice == "Cancel Registration":

    st.title("Cancel Student Registration")

    st.write(
        "Remove a student's existing event registration."
    )

    regs_df = st.session_state.regs_df

    if regs_df.empty:

        st.info(
            "No registrations are currently available."
        )

    else:

        with st.form("cancel_form"):

            col1, col2 = st.columns(2)

            with col1:

                sid = st.text_input(
                    "Student ID"
                ).strip()

            with col2:

                eid = st.text_input(
                    "Event ID"
                ).strip()

            submitted = st.form_submit_button(
                "Cancel Registration",
                use_container_width=True
            )

            if submitted:

                try:

                    if not sid or not eid:

                        raise ValueError(
                            "Please enter both Student ID and Event ID."
                        )

                    if eid not in st.session_state.events_df[
                        "event_id"
                    ].astype(str).values:

                        raise EventNotFoundError(
                            f"Event ID {eid} does not exist."
                        )

                    current_regs = st.session_state.regs_df

                    match = current_regs[
                        (current_regs["student_id"] == sid) &
                        (current_regs["event_id"] == eid)
                    ]

                    if match.empty:

                        raise RegistrationNotFoundError(
                            "Registration record not found."
                        )

                    st.session_state.regs_df = current_regs[
                        ~(
                            (current_regs["student_id"] == sid) &
                            (current_regs["event_id"] == eid)
                        )
                    ].reset_index(drop=True)

                    save_data()

                    st.success(
                        "Student registration cancelled successfully."
                    )

                except Exception as e:

                    st.error(
                        f"Cancellation Error: {e}"
                    )


# =====================================================
# 19. FOOTER
# =====================================================

st.markdown("---")

st.caption("Campus Event Management & Feedback Analyzer")
st.caption("Event Management | Student Registration | Feedback Analytics")
