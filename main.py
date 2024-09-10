import streamlit as st
import json
from streamlit_option_menu import option_menu
from admin import create_user, change_password, display_users_admin, display_logs
from DB import authenticate_user, get_user_role, get_question_type, get_question, enter_single, enter_table, enter_subq, enter_anytable, get_answer_list, get_answer, delete_answer, remove_access
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


def entry(selected, questions):
    headingNo = selected.split(" ")[1]

    st.markdown(f"<h2 style='text-align: left;'>{selected}</h2>", unsafe_allow_html=True)

    indicator = option_menu(None, ["Essential Indicator", "Leadership Indicator"],
                            menu_icon="punch", default_index=0, orientation="horizontal")

    subheadNo = "1"
    if indicator == "Essential Indicator":
        subheadNo = "1"
    elif indicator == "Leadership Indicator":
        subheadNo = "2"

    filtered_questions = [q for q in questions if q['headingNo'] == headingNo and q['subheadNo'] == subheadNo]

    for ans in get_answer_list(headingNo, subheadNo):
        if [int(headingNo), int(subheadNo), int(ans['Qno'])] not in st.session_state['saved_questions']:
            st.session_state['saved_questions'].append([int(headingNo), int(subheadNo), int(ans['Qno'])])

    print(st.session_state['saved_questions'])

    if not filtered_questions:
        st.error("No questions available for this principle.")
    else:
        with st.spinner(''):
            for question in filtered_questions:
                if [int(headingNo), int(subheadNo), int(question['Qno'])] not in st.session_state['saved_questions']:
                    type = get_question_type(headingNo, subheadNo, question['Qno'])
                    question_df = get_question(headingNo, subheadNo, question['Qno'])
                    if type == "single":
                        with st.form(key=str(question_df["_id"])):
                            st.write(question_df['Question'])
                            ans = st.text_input('Enter the answer:')
                            submit_reply = st.form_submit_button(label='Save')
                            if submit_reply:
                                on_click = enter_single(ans, question_df)
                                st.session_state['saved_questions'].append([headingNo, subheadNo, question['Qno']])
                                if on_click:
                                    st.success("Answer submitted successfully.")
                                else:
                                    st.error("An error occurred while submitting the answer.")

                    elif type == "table":
                        if 'Table' in question_df and 'any' in question_df['Table'] and question_df['Table']['any']:
                            if 'current_rows' not in st.session_state:
                                st.session_state['current_rows'] = 1
                            st.write(question_df['Question'])
                            columnName = question_df['Table']['Column']
                            list_of_list = [[0 for _ in range(len(columnName))] for _ in
                                            range(st.session_state['current_rows'])]
                            dataf = pd.DataFrame(list_of_list, columns=columnName)
                            dataf.index = dataf.index + 1
                            grid_response = AgGrid(dataf, height=int(st.session_state['current_rows'] * 70), editable=True,
                                                   fit_columns_on_grid_load=True)
                            col1, col2, col3, col4 = st.columns([1, 1, 1, 4])
                            with col1:
                                if st.button('Save'):
                                    st.session_state['saved_questions'].append([headingNo, subheadNo, question['Qno']])
                                    submit_reply = enter_anytable(grid_response, question_df)
                                    if submit_reply:
                                        st.success("Table submitted successfully.")
                                    else:
                                        st.error("An error occurred while submitting the table.")
                            with col2:
                                if st.button('Add Row'):
                                    st.session_state['current_rows'] += 1
                            with col3:
                                if st.button('Remove Row'):
                                    if st.session_state['current_rows'] > 1:
                                        st.session_state['current_rows'] -= 1
                            with col4:
                                st.write("")

                        else:
                            st.write(question_df['Question'])
                            columnName = question_df['Table']['Column']
                            rowName = question_df['Table']['Row']
                            list_of_list = [[0 for _ in range(len(columnName))] for _ in range(len(rowName))]
                            dataf = pd.DataFrame(list_of_list, columns=columnName, index=rowName)
                            dataf.insert(0, 'Row names', rowName)
                            grid_response = AgGrid(dataf, height=int(len(rowName) * 70), editable=True,
                                                   fit_columns_on_grid_load=True)
                            if st.button('Save', key=str(question_df["_id"])):
                                submit_reply = enter_table(grid_response['data'], question_df)
                                st.session_state['saved_questions'].append([headingNo, subheadNo, question['Qno']])
                                if submit_reply:
                                    st.success("Table submitted successfully.")
                                else:
                                    st.error("An error occurred while submitting the table.")


                    elif type == "subq":
                        with st.form(key=str(question_df["_id"])):
                            st.write(question_df['Question'])
                            answers = []
                            for q in question_df['Subquestions']['Questions']:
                                ans = st.text_input(q)
                                answers.append(ans)
                            submit_button = st.form_submit_button(label='Save')
                            if submit_button:
                                st.session_state['saved_questions'].append([headingNo, subheadNo, question['Qno']])
                                on_click = enter_subq(answers, question_df)
                                if on_click:
                                    st.success("Answer submitted successfully.")
                                else:
                                    st.error("An error occurred while submitting the answer.")
                    else:
                        print("will see kal, error hai ye")
                    st.divider()
                else:
                    pass

def saved(selected, questions):
    st.markdown(f"<h2 style='text-align: left;'>Saved Entries</h2>", unsafe_allow_html=True)

    headingNo = selected.split(" ")[1]

    st.markdown(f"<h2 style='text-align: left;'>{selected}</h2>", unsafe_allow_html=True)

    indicator = option_menu(None, ["Essential Indicator", "Leadership Indicator"],
                            menu_icon="punch", default_index=0, orientation="horizontal")

    subheadNo = "1"
    if indicator == "Essential Indicator":
        subheadNo = "1"
    elif indicator == "Leadership Indicator":
        subheadNo = "2"

    filtered_questions = [q for q in questions if q['headingNo'] == headingNo and q['subheadNo'] == subheadNo]
    answers = st.session_state['saved_questions']

    # Create a list of question numbers that have corresponding answers
    answer_qnos = [str(answer[2]) for answer in answers]

    # Remove questions from filtered_questions if their Qno is not in the answers list
    filtered_questions = [q for q in filtered_questions if str(q['Qno']) in answer_qnos]

    if not filtered_questions:
        st.error("No questions available for this principle.")
    else:
        with st.spinner(''):
            for question in filtered_questions:
                answer_df = get_answer(headingNo, subheadNo, question['Qno'])
                question_df = get_question(headingNo, subheadNo, question['Qno'])
                if not question_df["hasSubquestions"] and not question_df["isTable"]:
                    st.write(question_df['Question'])
                    st.write(f"Answer: {answer_df['answer']}")
                elif question_df["isTable"]:
                    st.write(question_df['Question'])
                    if 'Table' in question_df and 'any' in question_df['Table'] and question_df['Table']['any']:
                        columnName = question_df['Table']['Column']
                        dataf = pd.DataFrame(answer_df['answer'], columns=columnName)
                        dataf.index = dataf.index + 1
                        st.write(f"Answer:")
                        st.write(dataf)
                    else:
                        columnName = question_df['Table']['Column']
                        rowName = question_df['Table']['Row']
                        dataf = pd.DataFrame(answer_df['answer'], columns=columnName, index=rowName)
                        st.write(f"Answer:")
                        st.write(dataf)
                elif question_df["hasSubquestions"]:
                    st.write(question_df['Question'])
                    for i, q in enumerate(question_df['Subquestions']['Questions']):
                        st.write(f"{q}: {answer_df['answer'][i]}")
                if st.button("Delete", key=str(question_df["_id"])):
                    delete_answer(headingNo, subheadNo, question['Qno'])
                    st.session_state['saved_questions'].remove([int(headingNo), int(subheadNo), int(question['Qno'])])
                    st.success("Answer deleted successfully.")
                st.divider()

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
        if st.session_state['access']:
            if selected2 == "Entry":
                entry(selected, questions)
            elif selected2 == "Saved":
                saved(selected, questions)
            elif selected2 == "Submit":
                st.markdown(f"<h2 style='text-align: left;'>Submit all the Entries</h2>", unsafe_allow_html=True)
                st.write("Please make sure you have entered all the answers before submitting. Your access will be removed after submission.")
                email = st.text_input(label="Email:", value="", key="email",
                                      placeholder="Enter your email")
                password = st.text_input(label="Password:", value="", placeholder="Enter password",
                                         type="password")
                submit_button = st.button("Login", type="primary", on_click=submit_Clicked,
                                          args=(email, password))
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
            st.error("Your answers are already submitted. Please wait while admin reviews them.")

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
