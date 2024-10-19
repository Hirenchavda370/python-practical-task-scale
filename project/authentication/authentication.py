from flask import Blueprint, jsonify, g, request, json
import os
from project.utills.check_json import json_validation
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_refresh_token, create_access_token

authentication_bp = Blueprint("auth",__name__)

@authentication_bp.post("/user-signup")
@json_validation
def user_signup(data):
    try:
        # Extract data from the request body
        role_id = data.get("role_id")
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        email = data.get("email")
        password = data.get("password")

        cursor = g.db.cursor(dictionary=True)

        # Validate required fields individually
        if not role_id:
            return jsonify({"error": "Role id is required"}), 400
        if not firstname:
            return jsonify({"error": "Firstname is required"}), 400
        if not lastname:
            return jsonify({"error": "Lastname is required"}), 400
        if not email:
            return jsonify({"error": "Email id is required"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400

        # Validate role_id (make sure it's active)
        sql = "SELECT * FROM tbl_role WHERE id = %s and active = %s"
        cursor.execute(sql, (role_id, 1))
        check_user = cursor.fetchone()
        if not check_user:
            return jsonify({"error": "Role id is invalid, please provide a valid role id"}), 400

        # Validate email format
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(email_pattern, email):
            return jsonify({"error": "The format of the email is invalid"}), 400

        # Check if the email already exists in the database
        sql = "SELECT * FROM tbl_user WHERE email = %s"
        cursor.execute(sql, (email,))
        check_user = cursor.fetchone()
        if check_user:
            return jsonify({"error": "User has already registered with this email address, try with a different email"}), 404

        # Validate password strength
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=<>?]).{8,}$'
        if not re.fullmatch(password_pattern, password):
            return jsonify({
                "error": "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character."
            }), 400

        # Generate password hash
        pwd_hash = generate_password_hash(password, method='scrypt', salt_length=8)

        # Insert new user into the database
        sql = "INSERT INTO tbl_user (role_id, firstName, lastName, email, password) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql, (role_id, firstname, lastname, email, pwd_hash))
        user_id = cursor.lastrowid  # Get the newly created user id
        g.db.commit()

        # Create a response containing the user data
        response = {
            "id": user_id,
            "role_id": role_id,
            "firstname": firstname,
            "lastname": lastname,
            "email": email
        }
        return jsonify({"message": "User create successfully", "data": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@authentication_bp.post("/user-signin")
@json_validation
def user_signin(data):
    try:
        email = data.get("email")
        password = data.get("password")
        
        cursor = g.db.cursor(dictionary=True)

        # Validate if email and password are provided
        if not email and not password:
            return jsonify({'error': 'Please provide required data: email, password'}), 400
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400

        sql = "SELECT * FROM tbl_user WHERE email = %s"
        cursor.execute(sql, (email,))
        user_id = cursor.lastrowid  # Capture the last inserted/affected row ID
        check_user = cursor.fetchone()  # Fetch the user's details

        # If the user is not found, return an error
        if not check_user:
            return jsonify({"error": "User not found"}), 404
        else:
            # Validate the provided password against the stored hashed password
            if not check_password_hash(check_user['password'], password):
                return jsonify({"error": "Invalid credentials"}), 400

        # Generate access and refresh tokens using user_id and secret key
        access_token = create_access_token(os.environ['SECRET_KEY'] + "/" + str(user_id))
        refresh_token = create_refresh_token(os.environ['SECRET_KEY'] + "/" + str(user_id))

        # Prepare response data with user id, email, access token, and refresh token
        response = {"id": user_id, "email": email, "access_token": access_token, "refresh_token": refresh_token}
        
        return jsonify({'message': 'User signed in successfully', "data": response}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
