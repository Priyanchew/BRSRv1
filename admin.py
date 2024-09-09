import streamlit as st
import pandas as pd
from DB import create_new_user, get_logs, change_user_password, get_all_users


def create_user():
    with st.form(key="new_user_form"):
        new_email = st.text_input("Email", placeholder="Enter user email")
        new_password = st.text_input("Password", placeholder="Enter user password", type="password")
        new_role = st.selectbox("Assign Role", ["HR", "LAW", "FINANCE", "LEGAL", "ENVIRONMENT", "QC", "RnD", "SALES",
                                                "LOGISTICS", "SAFETY", "ADMIN", "PRODUCTION", "PURCHASE", "IT", "admin"])
        create_button = st.form_submit_button("Create User")

        if create_button:
            if not new_email or not new_password:
                st.warning("Please enter all the details.")
            else:
                try:
                    create_new_user(new_email, new_password, new_role)
                    st.success(f"User {new_email} created successfully with role {new_role}")
                except Exception as e:
                    st.error(f"Error creating user: {e}")


def display_logs():
    with st.spinner("Fetching logs..."):
        logs = get_logs()

        if len(list(logs)) > 0:
            df = pd.DataFrame(list(logs))  # Convert logs to a DataFrame
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
def display_users():
    with st.spinner("Fetching users..."):
        try:
            users = get_all_users()
            if users:
                df = pd.DataFrame(users)  # Assuming users is a list of dictionaries with 'email' and 'role'
                st.table(df)
            else:
                st.write("No users found.")
        except Exception as e:
            st.error(f"Error fetching users: {e}")
