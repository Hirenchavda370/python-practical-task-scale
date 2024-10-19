from flask import Blueprint, jsonify, g, request, json
import os
from project.utills.check_json import json_validation
import re
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint("user", __name__)


@user_bp.get("/user-list")
def user_list():
    try:
        cursor = g.db.cursor(dictionary=True)
        
        # Get the search term from query parameters, default is an empty string
        search_term = request.args.get('search', '')  
        
        # Base SQL query to select user details and their roles
        sql = """
            SELECT u.id, u.firstName, u.lastName, u.email, r.roleName, r.accessModules 
            FROM tbl_user u 
            LEFT JOIN tbl_role r ON u.role_id = r.id 
            WHERE r.active = %s 
        """
        
        # If a search term is provided, add conditions to the SQL query
        if search_term:
            search_term = f"%{search_term}%"
            sql += "AND (u.firstName LIKE %s OR u.lastName LIKE %s OR u.email LIKE %s) "
            params = (1, search_term, search_term, search_term)  # 1 indicates active role
        else:
            # Only include the active role condition if no search term is provided
            params = (1,)
        
        # Append ordering clause to sort results by user ID in descending order
        sql += "ORDER BY u.id DESC;"  
        
        cursor.execute(sql, params)
        user_list = cursor.fetchall()
        
        if not user_list:
            user_list = []
        
        return jsonify({"user_list": user_list}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.patch("/user-update")
@json_validation
def user_update(data):
    try:
        cursor = g.db.cursor(dictionary=True)
        users = data.get("users")
        
        # Validate that the 'users' data is present and is a list
        if not users or not isinstance(users, list):
            return jsonify({"error": "Please provide a list of users with required data"}), 400

        # Iterate through each user data provided in the request
        for user_data in users:
            user_id = user_data.get("user_id")  # Get user_id from user_data

            # Check if user_id is provided
            if not user_id:
                return jsonify({"error": "User ID is required for each user"}), 400
            
            # Fetch user by id from the database
            sql = 'SELECT id FROM tbl_user WHERE id=%s'
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()  # Fetch user record
            
            # Return error if user is not found
            if not user:
                return jsonify({'error': f'User with id {user_id} not found'}), 404

            # Prepare fields and values for dynamic update
            fields = []
            values = []

            # Update role_id if provided in the request
            role_id = user_data.get("role_id")
            if role_id:
                # Validate that the role_id exists and is active
                sql = "SELECT * FROM tbl_role WHERE id = %s and active = %s"
                cursor.execute(sql, (role_id, 1))
                check_role = cursor.fetchone()
                # Return error if role_id is invalid
                if not check_role:
                    return jsonify({"error": f'Role id {role_id} is invalid for user with id {user_id}, please provide a valid role id'}), 400
                fields.append("role_id = %s")
                values.append(role_id)

            # Update firstname if provided
            firstname = user_data.get("firstname")
            if firstname:
                fields.append("firstName = %s")
                values.append(firstname)

            # Update lastname if provided
            lastname = user_data.get("lastname")
            if lastname:
                fields.append("lastName = %s")
                values.append(lastname)

            # Update email if provided
            email = user_data.get("email")
            if email:
                # Validate email format using regex
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
                if not re.fullmatch(email_pattern, email):
                    return jsonify({"error": f"The email format is invalid for user with id {user_id}"}), 400
                fields.append("email = %s")
                values.append(email)

            # Update password if provided
            password = user_data.get("password")
            if password:
                # Validate password format using regex
                password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=<>?]).{8,}$'
                if not re.fullmatch(password_pattern, password):
                    return jsonify({"error": f"Password for user with id {user_id} must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character."}), 400
                # Hash the password
                pwd_hash = generate_password_hash(password, method='scrypt', salt_length=8)
                fields.append("password = %s")
                values.append(pwd_hash)

            # If no fields to update, skip to the next user
            if not fields:
                continue

            # Prepare the SQL update query dynamically
            values.append(user_id)  # Add user_id to the values list for the WHERE clause
            sql = f"UPDATE tbl_user SET {', '.join(fields)} WHERE id = %s"
            cursor.execute(sql, values)  # Execute the update query

        g.db.commit()

        return jsonify({"message": "Users updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.delete("/user-delete/<user_id>")
def user_delete(user_id):
    try:
        cursor = g.db.cursor(dictionary=True)
        
        # SQL query to check if the user exists
        sql = 'SELECT id FROM tbl_user WHERE id=%s'
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()

        # Check if the user exists
        if user:
            # SQL query to delete the user from the database
            sql = "DELETE FROM tbl_user WHERE id=%s"
            cursor.execute(sql, (user_id,))
            g.db.commit()
            return jsonify({'message': "User deleted successfully"}), 200
        else:
            return jsonify({'error': 'User not found'}), 404  # Return error if user does not exist
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.get("/user-has-access/<user_id>")
def check_user_access(user_id):
    try:
        module_to_check = request.args.get('module')

        if not module_to_check:
            return jsonify({"error": "Module is required"}), 400

        cursor = g.db.cursor(dictionary=True)
        
        # SQL query to fetch the user's role and their accessible modules
        sql = """
        SELECT u.role_id, r.accessModules 
        FROM tbl_user u 
        LEFT JOIN tbl_role r ON u.role_id = r.id 
        WHERE u.id = %s AND r.active = %s
        """
        cursor.execute(sql, (user_id, 1))  # Execute the query with user_id and active status
        user_role = cursor.fetchone()

        # Check if the user or role was found
        if not user_role:
            return jsonify({"error": "User or role not found"}), 404

        # Parse the access modules from JSON format
        access_modules = json.loads(user_role['accessModules'])

        # Check if the requested module is in the user's access list
        if module_to_check in access_modules:
            return jsonify({"message": "User has access to the module", "module": module_to_check}), 200
        else:
            return jsonify({"message": "User does not have access to the module", "module": module_to_check}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 400
