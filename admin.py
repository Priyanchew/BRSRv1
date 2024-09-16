import streamlit as st
import pandas as pd
from DB import create_new_user, get_logs, change_user_password, get_all_users, submitted_q_by_email


def create_user():
    with st.form(key="new_user_form"):
        new_email = st.text_input("Email", placeholder="Enter user email")
        new_password = st.text_input("Password", placeholder="Enter user password", type="password")
        new_role = st.selectbox("Assign Dept. (Admin for that dept.)", ["HR", "LAW", "FINANCE", "LEGAL", "ENVIRONMENT", "QC", "RnD", "SALES",
                                                "LOGISTICS", "SAFETY", "ADMIN", "PRODUCTION", "PURCHASE", "IT", "admin"])
        create_button = st.form_submit_button("Create User")

        if create_button:
            if not new_email or not new_password:
                st.warning("Please enter all the details.")
            else:
                try:
                    create_new_user(new_email, new_password, new_role, True)
                    st.success(f"User {new_email} created successfully with role {new_role}")
                except Exception as e:
                    st.error(f"Error creating user: {e}")


def display_logs():
    with st.spinner("Fetching logs..."):
        logs = get_logs()
        logs_list = list(logs)
        if len(logs_list) > 0:
            df = pd.DataFrame(logs_list)
            df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            df = df[['action', 'user_email', 'details', 'timestamp']]  # Select relevant columns
            st.table(df)
        elif logs == -1:
            st.error("An error occurred while fetching logs.")
        else:
            st.error("No logs found.")


# Function to change a user's password
def change_password():
    with st.form(key="change_password_form"):
        email = st.text_input("Email", placeholder="Enter user email")
        new_password = st.text_input("New Password", placeholder="Enter new password", type="password")
        confirm_password = st.text_input("Confirm New Password", placeholder="Confirm new password", type="password")
        change_button = st.form_submit_button("Change Password")

        if change_button:
            if not email or not new_password or not confirm_password:
                st.warning("Please fill out all fields.")
            elif new_password != confirm_password:
                st.warning("Passwords do not match.")
            else:
                try:
                    change_user_password(email, new_password)
                    st.success(f"Password for {email} has been changed successfully.")
                except Exception as e:
                    st.error(f"Error changing password: {e}")


# Function to show existing users
def display_users_admin(role):
    with st.spinner("Fetching users..."):
        try:
            users = get_all_users(role)
            if users:
                df = pd.DataFrame(users)  # Assuming users is a list of dictionaries with 'email' and 'role'
                st.table(df)
            else:
                st.write("No users found.")
        except Exception as e:
            st.error(f"Error fetching users: {e}")

def review_entries():
    users = get_all_users()
    filtered_users = [user for user in users if user.get('access') == False]
    user_display = [f"{user['email']} ({user['role']})" for user in filtered_users]
    selected = st.selectbox("Select Dept.", user_display)
    if selected:
        st.write(f"Selected Dept.: {selected.split(' ')[0]}")
        answers = submitted_q_by_email(selected.split(" ")[0])
        for answer in answers:
            st.write(answer['answer'])
    else:
        st.warning("No Dept. selected.")


