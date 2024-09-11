import streamlit as st
import json
from streamlit_option_menu import option_menu
from admin import create_user, change_password, display_users_admin, display_logs, review_entries
from DB import authenticate_user, get_user_role, remove_access
from user import entry, saved

st.set_page_config(
    page_title="Carbon Crunch",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Load the JSON file with questions for each role
with open('roles.json', 'r') as f:
    role_questions = json.load(f)


def LoggedIn_Clicked(username, password):
    if not username or not password:
        st.warning("Please enter both username and password.")
    else:
        try:
            if authenticate_user(username, password):
                st.session_state['loggedIn'] = True
                user_role, access = get_user_role(username)
                st.session_state['role'] = user_role
                st.session_state['email'] = username
                st.session_state['access'] = access
            else:
                st.error("Invalid username or password.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def submit_Clicked(email, password):
    if not email or not password:
        st.warning("Please enter both username and password.")
    else:
        try:
            if authenticate_user(email, password):
                remove_access(email)
                st.session_state['access'] = False
                st.success("Your answers have been submitted successfully. Your access will be removed.")
            else:
                st.error("Invalid username or password.")
        except Exception as e:
            st.error(f"An error occurred: {e}")



if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'saved_questions' not in st.session_state:
    st.session_state['saved_questions'] = []
if 'email' not in st.session_state:
    st.session_state['email'] = None
if 'access' not in st.session_state:
    st.session_state['access'] = None

st.markdown("""
    <style>
        .reportview-container .main .block-container {
            max-width: 100%;
            padding-top: 0rem;
            padding-right: 0rem;
            padding-left: 0rem;
            padding-bottom: 0rem;
        }
        .reportview-container .main {
            color: dark;
            background-color: white;
        }
        div[data-testid="stVerticalBlock"] > div:first-child {
            overflow: hidden;
        }
        .element-container img {
            width: 100%;
            height: 100vh;
            object-fit: cover;
        }
        .stApp {
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)




def admin_page():
    st.title("Admin Dashboard")

    selected = option_menu(None, ["Add User", "Change Password", "Review", "log", "Existing roles"],
                           icons=['plus', 'eraser', "", "journal-text", "person-fill"],
                           menu_icon="punch", default_index=0, orientation="horizontal")

    if selected == "Add User":
        st.markdown("<h2 style='text-align: left;'>Manage Users</h2>", unsafe_allow_html=True)
        create_user()
    elif selected == "Change Password":
        st.markdown("<h2 style='text-align: left;'>Change User Password</h2>", unsafe_allow_html=True)
        change_password()
    elif selected == "Review":
        st.markdown("<h2 style='text-align: left;'>Review Entries</h2>", unsafe_allow_html=True)
        review_entries()
    elif selected == "log":
        st.markdown("<h2 style='text-align: left;'>Activity Logs</h2>", unsafe_allow_html=True)
        display_logs()
    elif selected == "Existing roles":
        st.markdown("<h2 style='text-align: left;'>Existing Users</h2>", unsafe_allow_html=True)
        display_users_admin()



def display_users(role):
    st.markdown(f"<h2 style='text-align: left;'>{role} Dashboard</h2>", unsafe_allow_html=True)

    if role in role_questions:
        questions = role_questions[role]
        with st.sidebar:
            selected2 = option_menu(None, ["Entry","Saved", "Submit", "Logout"],
                                    icons=["pencil-square",'floppy2-fill', 'upload', 'box-arrow-right'],
                                    menu_icon="punch", default_index=0, orientation="vertical")

            selected = option_menu(None, ["Principle 1", "Principle 2", "Principle 3", "Principle 4",
                                      "Principle 5", "Principle 6", "Principle 7", "Principle 8", "Principle 9"],
                               icons=['1-square', '2-square', '3-square', '4-square', '5-square', '6-square', '7-square',
                                      '8-square', '9-square'],
                               menu_icon="punch", default_index=0, orientation="vertical")
        if selected2 == "Entry":
            if st.session_state['access']:
                entry(selected, questions)
            else:
                st.error("Your answers are already submitted. Please wait while admin reviews them.")
        elif selected2 == "Saved":
            if st.session_state['access']:
                saved(selected, questions)
            else:
                st.error("Your answers are already submitted. Please wait while admin reviews them.")
        elif selected2 == "Submit":
            if st.session_state['access']:
                st.markdown(f"<h2 style='text-align: left;'>Submit all the Entries</h2>", unsafe_allow_html=True)
                st.write("Please make sure you have entered all the answers before submitting. Your access will be removed after submission.")
                email = st.text_input(label="Email:", value="", key="email",
                                      placeholder="Enter your email")
                password = st.text_input(label="Password:", value="", placeholder="Enter password",
                                         type="password")
                submit_button = st.button("Login", type="primary", on_click=submit_Clicked,
                                          args=(email, password))
            else:
                st.error("Your answers are already submitted. Please wait while admin reviews them.")
        elif selected2 == "Logout":
            st.markdown("<h2 style='text-align: left;'>Log out</h2>", unsafe_allow_html=True)
            if st.button("Logout"):
                st.session_state['loggedIn'] = False
                st.session_state['role'] = None
                st.session_state['email'] = None
                st.session_state['access'] = None
                st.session_state['saved_questions'] = []
                st.success("Logged out successfully.")
                st.rerun()

    else:
        st.error("No questions available for this role.")


def main():
    # Page routing based on role
    if st.session_state['loggedIn']:
        if st.session_state['role'] == 'admin':
            admin_page()
        else:
            # Other roles get their specific questions
            display_users(st.session_state['role'])
    else:
        # Show login page if not logged in
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                st.write("")

            with col2:
                if not st.session_state['loggedIn']:
                    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
                    email = st.text_input(label="Email:", value="", key="email",
                                                 placeholder="Enter your email")
                    password = st.text_input(label="Password:", value="", placeholder="Enter password",
                                                 type="password")
                    submit_button = st.button("Login", type="primary", on_click=LoggedIn_Clicked,
                                                              args=(email, password))

            with col3:
                st.write("")


if __name__ == "__main__":
    main()
