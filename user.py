from DB import get_question_type, get_question, enter_single, enter_table, enter_subq, enter_anytable, get_answer_list, get_answer, delete_answer
import pandas as pd
from st_aggrid import AgGrid
import streamlit as st
from streamlit_option_menu import option_menu


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