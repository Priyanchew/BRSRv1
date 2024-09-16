import streamlit as st

def create_user_dept(role):
    from DB import create_new_user
    with st.form(key="new_user_form"):
        new_email = st.text_input("Email", placeholder="Enter user email")
        new_password = st.text_input("Password", placeholder="Enter user password", type="password")
        questions = st.selectbox("Assign all the questions to this user", ["Yes", "No"])
        if questions == "No":
            st.write("You have chosen No, to assign specific questions visit assign questions tab.")
        else:
            st.write("You have chosen Yes, all the questions will be assigned to this user.")
        create_button = st.form_submit_button("Create User")
        if create_button:
            if not new_email or not new_password:
                st.warning("Please enter all the details.")
            else:
                try:
                    create_new_user(new_email, new_password, role, False)
                    st.success(f"User {new_email} created successfully for your Dept. {role}")
                except Exception as e:
                    st.error(f"Error creating user: {e}")
