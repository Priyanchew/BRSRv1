from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import streamlit as st
from dotenv import load_dotenv
import os
load_dotenv()

database_pass = os.getenv('DATABASE_PASS')
uri=f"mongodb+srv://priyanshu6beta:{database_pass}@brsrcluster.wycfx0h.mongodb.net/?retryWrites=true&w=majority&appName=BRSRCluster"


# Connect to the MongoDB database
def connect_to_db():
    try:
        client = MongoClient(
            uri
        )
        db = client["Carbon-crunch"]
        return db
    except ConnectionFailure:
        raise Exception("Failed to connect to MongoDB. Please check your connection settings.")
    except PyMongoError as e:
        raise Exception(f"An error occurred while connecting to the database: {e}")


# Authenticate a user by verifying email and password
def authenticate_user(email, password):
    try:
        db = connect_to_db()
        users_collection = db["UsersCred"]

        user = users_collection.find_one({"email": email})

        if user:
            # Check if the password matches the hashed password
            if check_password_hash(user["password"], password):
                return True
            else:
                return False
        else:
            return False
    except PyMongoError as e:
        raise Exception(f"An error occurred while querying the database: {e}")


# Fetch the role of a user based on email
def get_user_role(email):
    try:
        db = connect_to_db()
        users_collection = db['UsersCred']

        user = users_collection.find_one({"email": email})
        if user:
            return user.get('role', 'user'), user['access']
        return None
    except PyMongoError as e:
        raise Exception(f"An error occurred while fetching the user's role: {e}")


def get_logs():
    try:
        db = connect_to_db()
        logs_collection = db['Logs']

        logs = logs_collection.find().sort("timestamp", -1)  # Sort by most recent logs

        if logs:
            return logs
        else:
            return False
    except PyMongoError as e:
        raise -1


# Create a new user in the database
def create_new_user(email, password, role):
    try:
        db = connect_to_db()
        users_collection = db['UsersCred']

        # Check if the user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            raise Exception(f"User with email {email} already exists.")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user
        user_data = {
            "email": email,
            "password": hashed_password,
            "role": role,
            "access": True
        }
        users_collection.insert_one(user_data)

        log_action("create_user", email, f"User with role {role} was created.")
    except PyMongoError as e:
        raise Exception(f"An error occurred while creating the user: {e}")


# Fetch all users and their roles from the database
def get_all_users():
    try:
        db = connect_to_db()
        users_collection = db['UsersCred']

        # Find all users and return a list of dictionaries containing email and role
        users = users_collection.find({}, {"email": 1, "role": 1, "access": 1, "_id": 0})

        return list(users)
    except PyMongoError as e:
        raise Exception(f"An error occurred while fetching all users: {e}")


# Change a user's password
def change_user_password(email, new_password):
    try:
        db = connect_to_db()
        users_collection = db['UsersCred']

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update the user's password
        result = users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

        if result.modified_count == 0:
            raise Exception(f"Password update failed for {email}. User may not exist.")

        log_action("change_password", email, "Password was updated.")
    except PyMongoError as e:
        raise Exception(f"An error occurred while updating the password: {e}")


def log_action(action, user_email, details):
    try:
        db = connect_to_db()
        logs_collection = db['Logs']

        log_entry = {
            "action": action,  # e.g., "create_user", "change_password", "update_role"
            "user_email": user_email,  # email of the user who triggered the action
            "details": details,  # Additional details about the action
            "timestamp": datetime.datetime.now()  # Timestamp of the action
        }

        logs_collection.insert_one(log_entry)
    except PyMongoError as e:
        raise Exception(f"An error occurred while logging the action: {e}")


def get_question_type(headingNo, subheadNo, Qno):
    try:
        db = connect_to_db()
        questions_collection = db['BRSRquestions']
        headingNo = int(headingNo)
        subheadNo = int(subheadNo)
        Qno = int(Qno)
        question = questions_collection.find_one({"headingNo": headingNo, "subheadNo": subheadNo, "Qno": Qno})
        if question:
            is_table = question.get('isTable', False)
            has_subquestions = question.get('hasSubquestions', False)
            if not is_table and not has_subquestions:
                return 'single'
            elif is_table and not has_subquestions:
                return 'table'
            elif not is_table and has_subquestions:
                return 'subq'
            else:
                return 'BhagwanHaiKya'
        return None
    except PyMongoError as e:
        raise Exception(f"An error occurred while fetching the question type: {e}")


def get_question(headingNo, subheadNo, Qno):
    try:
        db = connect_to_db()
        questions_collection = db['BRSRquestions']
        headingNo = int(headingNo)
        subheadNo = int(subheadNo)
        Qno = int(Qno)
        question = questions_collection.find_one({"headingNo": headingNo, "subheadNo": subheadNo, "Qno": Qno})
        return question
    except PyMongoError as e:
        raise Exception(f"An error occurred while fetching the question type: {e}")


def enter_single(ans, question_df):
    """
    Inserts a single entry into the collection.
    """
    db = connect_to_db()
    collection = db['CC']
    try:
        query = {"headingNo": question_df['headingNo'], "subheadNo": question_df['subheadNo'],
                 "Qno": question_df['Qno'], "user_email": st.session_state['email']}
        update = {"$set": {"answer": ans}}
        collection.update_one(query, update, upsert=True)
        return "Answer inserted."
    except Exception as e:
        return False


def enter_table(list_of_df, question_df):
    """
    Inserts multiple entries from a list of df into the collection.
    """
    db = connect_to_db()
    collection = db['CC']
    arr = list_of_df.values
    arr = arr[:, 1:]
    arr = arr.tolist()
    try:
        query = {"headingNo": question_df['headingNo'], "subheadNo": question_df['subheadNo'],
                 "Qno": question_df['Qno'], "user_email": st.session_state['email']}
        update = {"$set": {"answer": arr}}
        collection.update_one(query, update, upsert=True)
        return "Table inserted."
    except Exception as e:
        print(e)
        return False


def enter_anytable(list_of_df, question_df):
    """
        Inserts multiple entries from a list of df into the collection.
        """
    db = connect_to_db()
    collection = db['CC']
    arr = list_of_df.values
    arr = arr.tolist()
    try:
        query = {"headingNo": question_df['headingNo'], "subheadNo": question_df['subheadNo'],
                 "Qno": question_df['Qno'], "user_email": st.session_state['email']}
        update = {"$set": {"answer": arr}}
        collection.update_one(query, update, upsert=True)
        return "Table inserted."
    except Exception as e:
        print(e)
        return False


def enter_subq(list_of_subq, question_df):
    """
    Updates a collection or inserts sub-questions (list).
    This function assumes an update or insert-like behavior.
    """
    db = connect_to_db()
    collection = db['CC']
    try:
        print(list_of_subq)
        query = {"headingNo": question_df['headingNo'], "subheadNo": question_df['subheadNo'],
                 "Qno": question_df['Qno'], "user_email": st.session_state['email']}
        update = {"$set": {"answer": list_of_subq}}
        collection.update_one(query, update, upsert=True)
        return "Sub-questions inserted."
    except Exception as e:
        return False


def get_answer_list(headingNo, subheadNo):
    try:
        db = connect_to_db()
        collection = db['CC']
        headingNo = int(headingNo)
        subheadNo = int(subheadNo)
        query = {"headingNo": headingNo, "subheadNo": subheadNo}
        answer_list = collection.find(query)
        return answer_list
    except PyMongoError as e:
        raise Exception(f"An error occurred while fetching all questions: {e}")


def get_answer(headingNo, subheadNo, Qno):
    try:
        db = connect_to_db()
        collection = db['CC']
        headingNo = int(headingNo)
        subheadNo = int(subheadNo)
        Qno = int(Qno)
        query = {"headingNo": headingNo, "subheadNo": subheadNo, "Qno": Qno}
        answer = collection.find_one(query)
        return answer
    except PyMongoError as e:
        raise Exception(f"An error occurred while fetching all questions: {e}")


def delete_answer(headingNo, subheadNo, Qno):
    try:
        db = connect_to_db()
        collection = db['CC']
        headingNo = int(headingNo)
        subheadNo = int(subheadNo)
        Qno = int(Qno)
        query = {"headingNo": headingNo, "subheadNo": subheadNo, "Qno": Qno}
        collection.delete_one(query)
        return "Answer deleted."
    except PyMongoError as e:
        raise Exception(f"An error occurred while deleting the answer: {e}")


def remove_access(email):
    try:
        db = connect_to_db()
        users_collection = db['UsersCred']
        query = {"email": email}
        update = {"$set": {"access": False}}
        users_collection.update_one(query, update, upsert=True)
        log_action("Submitted", email, f"User of role {st.session_state['role']} with email {email} has submitted their part of the report.")
        return "User removed."
    except PyMongoError as e:
        raise Exception(f"An error occurred while removing the user: {e}")

def submitted_q_by_email(email):
    try:
        db = connect_to_db()
        collection = db['CC']
        query = {"user_email": email}
        answer_list = collection.find(query)
        return list(answer_list)
    except PyMongoError as e:
        raise Exception(f"An error occurred while fetching all questions: {e}")
