from flask import Blueprint, jsonify, json, g, request
from project.utills.check_json import json_validation

role_bp = Blueprint("role",__name__)

@role_bp.post("/create-role")
@json_validation  # Ensures that the request data is in proper JSON format
def create_role(data):
    try:
        # Extracting 'role_name' and 'access_modules' from the request data
        role_name = data.get("role_name")
        access_modules = data.get("access_modules")
        
        # Validate that both 'role_name' and 'access_modules' are provided
        if not role_name and not access_modules:
            return jsonify({"error": "Role name and access modules are required"}), 400
        if not role_name:
            return jsonify({"error": "Role name is required"}), 400
        if not access_modules:
            return jsonify({"error": "Access module is required"}), 400
        
        # Remove any duplicate access modules using 'set'
        unique_access_modules = list(set(access_modules))  # Ensures access modules are unique
        
        # Prepare SQL statement to insert the new role into the database
        cursor = g.db.cursor(dictionary=True)
        sql = "INSERT INTO tbl_role (roleName, accessModules) VALUES (%s, %s)"
        
        # Execute the SQL command and commit the changes to the database
        cursor.execute(sql, (role_name, json.dumps(unique_access_modules)))  # Store access modules as JSON string
        g.db.commit()
        
        # Return success response with the newly created role's ID
        return jsonify({"message": "Role created successfully", "role_id": cursor.lastrowid}), 201
    except Exception as e:
        # If there's any exception, return an error response with the exception message
        return jsonify({"error": str(e)}), 400


@role_bp.get("/get-role/<role_id>")
def get_role(role_id):
    try:
        cursor = g.db.cursor(dictionary=True)
        
        # SQL query to select the role where id matches role_id and it's active
        sql = "SELECT * FROM tbl_role WHERE id=%s and active=%s"
        
        # Execute the query with role_id and active=1 as parameters (active role)
        cursor.execute(sql, (role_id, 1))
        
        role = cursor.fetchone()

        # If no matching role is found, return a 404 error response
        if not role:
            return jsonify({"error": "Role not found"}), 404

        # Convert the 'accessModules' field from JSON string to a list
        role["accessModules"] = json.loads(role["accessModules"])  # Convert to list
        
        return jsonify({"role": role}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@role_bp.get("/list-role-module")
def list_role_module():
    try:
        cursor = g.db.cursor(dictionary=True)

        # Define SQL query to fetch all active roles from the 'tbl_role' table
        list_sql = "SELECT * FROM tbl_role WHERE active = %s ORDER BY id DESC"

        # Execute the query with a parameter to filter active roles (where active = 1)
        cursor.execute(list_sql, (1,))

        list_roles = cursor.fetchall()

        # If no roles are found, return an empty list
        if not list_roles:
            list_roles = []

        return jsonify({"role_modules": list_roles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
@role_bp.patch("/role-update/<role_id>")
def update_role(role_id):
    try:
        # Retrieve the JSON data from the request
        data = request.json
        role_name = data.get("role_name")
        access_modules = data.get("access_modules", [])
        update_access_modules = list(set(access_modules))

        cursor = g.db.cursor(dictionary=True)

        # Fetch the existing role from the database using the role_id
        sql = "SELECT * FROM tbl_role WHERE id=%s"
        cursor.execute(sql, (role_id,))
        role = cursor.fetchone()

        # If the role doesn't exist, return an error message
        if not role:
            return jsonify({"error": "Role not found"}), 404

        # Update the role details in the database
        sql = "UPDATE tbl_role SET roleName=%s, accessModules=%s WHERE id=%s"
        cursor.execute(sql, (
            # If a new roleName is provided, update it; otherwise, use the existing roleName
            role_name if role_name else role["roleName"],
            # If new accessModules are provided, update them as a JSON string; otherwise, keep the existing value
            json.dumps(update_access_modules) if access_modules else role["accessModules"],
            role_id
        ))
        g.db.commit()  # Commit the changes to the database

        return jsonify({"message": "Role updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@role_bp.delete("/role-delete/<role_id>")
def delete_role(role_id):
    try:
        cursor = g.db.cursor(dictionary=True)
        
        # Check if the role exists in the 'tbl_role' table by querying its ID
        sql = "SELECT * FROM tbl_role WHERE id=%s and active=%s"
        cursor.execute(sql, (role_id,1))
        role = cursor.fetchone()

        # If the role does not exist, return a 404 error with a 'Role not found' message
        if not role:
            return jsonify({"error": "Role not found"}), 404

        # If the role exists, proceed to delete it from the 'tbl_role' table
        sql = "UPDATE tbl_role SET active=%s WHERE id=%s"
        cursor.execute(sql, (0, role_id))
        
        g.db.commit()

        return jsonify({"message": "Role deleted successfully"}), 200

    except Exception as e:
        # If any exception occurs during the process, return an error message with a 400 status code
        return jsonify({"error": str(e)}), 400