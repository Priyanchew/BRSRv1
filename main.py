import streamlit as st
import json
from streamlit_option_menu import option_menu
from admin import create_user, change_password, display_users, display_logs
from DB import authenticate_user, get_user_role, get_question_type, get_question, enter_single, enter_table, enter_subq
import pandas as pd
from st_aggrid import AgGrid

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
                user_role = get_user_role(username)
                st.session_state['role'] = user_role
            else:
                st.error("Invalid username or password.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None

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

    selected = option_menu(None, ["Add User", "Change Password", "log", "Existing roles"],
                           icons=['plus', 'eraser', "journal-text", "person-fill"],
                           menu_icon="punch", default_index=0, orientation="horizontal")

    if selected == "Add User":
        st.markdown("<h2 style='text-align: left;'>Manage Users</h2>", unsafe_allow_html=True)
        create_user()
    elif selected == "Change Password":
        st.markdown("<h2 style='text-align: left;'>Change User Password</h2>", unsafe_allow_html=True)
        change_password()
    elif selected == "log":
        st.markdown("<h2 style='text-align: left;'>Activity Logs</h2>", unsafe_allow_html=True)
        display_logs()
    elif selected == "Existing roles":
        st.markdown("<h2 style='text-align: left;'>Existing Users</h2>", unsafe_allow_html=True)
        display_users()



def display_users(role):
    st.markdown(f"<h2 style='text-align: left;'>{role} Dashboard</h2>", unsafe_allow_html=True)

    if role in role_questions:
        questions = role_questions[role]
        with st.sidebar:
            selected = option_menu(None, ["Principle 1", "Principle 2", "Principle 3", "Principle 4",
                                      "Principle 5", "Principle 6", "Principle 7", "Principle 8", "Principle 9"],
                               icons=['1-square', '2-square', '3-square', '4-square', '5-square', '6-square', '7-square',
                                      '8-square', '9-square'],
                               menu_icon="punch", default_index=0, orientation="vertival")

        headingNo = selected.split(" ")[1]

        st.markdown(f"<h2 style='text-align: left;'>{selected}</h2>", unsafe_allow_html=True)

        indicator = option_menu(None, ["Essential Indicator","Leadership Indicator"],
                               menu_icon="punch", default_index=0, orientation="horizontal")

        subheadNo = "1"
        if indicator == "Essential Indicator":
            subheadNo = "1"
        elif indicator == "Leadership Indicator":
            subheadNo = "2"

        filtered_questions = [q for q in questions if q['headingNo'] == headingNo and q['subheadNo'] == subheadNo]

        if not filtered_questions:
            st.error("No questions available for this principle.")
        else:
            with st.spinner(''):
                for question in filtered_questions:
                    type = get_question_type(headingNo, subheadNo, question['Qno'])
                    question_df = get_question(headingNo, subheadNo, question['Qno'])
                    if type == "single":
                        with st.form(key=str(question_df["_id"])):
                            st.write(question_df['Question'])
                            ans = st.text_input('Enter the answer:')
                            submit_button = st.form_submit_button(label='Submit', on_click=enter_single(ans))
                    elif type == "table":
                        if 'Table' in question_df and 'any' in question_df['Table'] and question_df['Table']['any']:
                            if 'current_rows' not in st.session_state:
                                st.session_state['current_rows'] = 1
                            st.write(question_df['Question'])
                            columnName = question_df['Table']['Column']
                            list_of_list = [[0 for _ in range(len(columnName))] for _ in range(st.session_state['current_rows'])]
                            dataf = pd.DataFrame(list_of_list, columns=columnName)
                            dataf.index = dataf.index + 1
                            grid_response = AgGrid(dataf, height=int(st.session_state['current_rows']*50),editable=True, fit_columns_on_grid_load=True)
                            if st.button('Submit'):
                                enter_table(grid_response)
                            if st.button('Add Row'):
                                st.session_state['current_rows'] += 1
                        else:
                            st.write(question_df['Question'])
                            columnName = question_df['Table']['Column']
                            rowName = question_df['Table']['Row']
                            list_of_list = [[0 for _ in range(len(columnName))] for _ in range(len(rowName))]
                            dataf = pd.DataFrame(list_of_list, columns=columnName, index=rowName)
                            dataf.insert(0, 'Row names', rowName)
                            grid_response = AgGrid(dataf, height=int(len(rowName)*50),editable=True, fit_columns_on_grid_load=True)
                            if st.button('Submit', key=str(question_df["_id"])):
                                enter_table(grid_response)

                    elif type == "subq":
                        with st.form(key=str(question_df["_id"])):
                            st.write(question_df['Question'])
                            answers = []
                            for q in question_df['Subquestions']['Questions']:
                                ans = st.text_input(q)
                                answers.append(ans)
                            submit_button = st.form_submit_button(label='Submit', on_click=enter_subq(answers))
                    else:
                        print("will see kal, error hai ye")
                    st.divider()

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
                    with st.form(key="login_form"):
                        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
                        userName = st.text_input(label="Email:", value="", key="username",
                                                 placeholder="Enter your username")
                        password = st.text_input(label="Password:", value="", placeholder="Enter password",
                                                 type="password")
                        submit_button = st.form_submit_button("Login", type="primary", on_click=LoggedIn_Clicked,
                                                              args=(userName, password))

            with col3:
                st.write("")


if __name__ == "__main__":
    main()
