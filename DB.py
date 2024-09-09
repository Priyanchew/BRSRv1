from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


# Connect to the MongoDB database
def connect_to_db():
    try:
        client = MongoClient(
            "mongodb+srv://priyanshu6beta:Rfamo6LNGANVH6t2@brsrcluster.wycfx0h.mongodb.net/?retryWrites=true&w=majority&appName=BRSRCluster"
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
            return user.get('role', 'user')
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
            "role": role
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
        users = users_collection.find({}, {"email": 1, "role": 1, "_id": 0})

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


def enter_single(ans):
    """
    Inserts a single entry into the collection.
    """
    db = connect_to_db()
    collection = db['CC']
    try:
        result = collection.insert_one({"answer": ans})
        return f"Inserted document with id: {result.inserted_id}"
    except Exception as e:
        return f"An error occurred: {e}"

def enter_table(list_of_list):
    """
    Inserts multiple entries from a list of lists into the collection.
    """
    db = connect_to_db()
    collection = db['CC']
    try:
        documents = [{"row": row} for row in list_of_list]
        result = collection.insert_many(documents)
        return f"Inserted {len(result.inserted_ids)} documents."
    except Exception as e:
        return f"An error occurred: {e}"

def enter_subq(list_of_subq):
    """
    Updates a collection or inserts sub-questions (list).
    This function assumes an update or insert-like behavior.
    """
    db = connect_to_db()
    collection = db['CC']
    try:
        for subq in list_of_subq:
            # You can specify a query and an update action
            query = {"sub_question": subq}
            update = {"$set": {"sub_question": subq}}
            collection.update_one(query, update, upsert=True)  # upsert=True to insert if it doesn't exist
        return "Sub-questions inserted or updated."
    except Exception as e:
        return f"An error occurred: {e}"