from flask import Blueprint, jsonify, g, request, json
from project.utills.check_json import json_validation

access_module_bp = Blueprint("access_module",__name__)

@access_module_bp.patch("/access-update-modules/<role_id>")
@json_validation
def update_access_modules(data, role_id):
    try:
        new_modules = data.get("accessModules", [])

        # Validate that access modules are provided
        if not new_modules:
            return jsonify({"error": "Access modules are required"}), 400

        # Ensure unique values in the access modules
        unique_modules = list(set(new_modules))

        cursor = g.db.cursor(dictionary=True)
        
        # Check if the role exists and is active
        sql = "SELECT id FROM tbl_role WHERE id=%s and active=%s"
        cursor.execute(sql, (role_id, 1))
        role = cursor.fetchone()

        # Return an error if the role is not found
        if not role:
            return jsonify({"error": "Role not found"}), 404

        # Update the role's access modules in the database
        sql = "UPDATE tbl_role SET accessModules=%s WHERE id=%s"
        cursor.execute(sql, (json.dumps(unique_modules), role_id))
        g.db.commit()

        return jsonify({"message": "Access modules updated successfully", "modules": unique_modules}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@access_module_bp.patch("/access-remove-module/<role_id>")
def remove_access_module(role_id):
    try:
        data = request.json
        module_to_remove = data.get("module")

        if not module_to_remove:
            return jsonify({"error": "Module to remove is required"}), 400

        cursor = g.db.cursor(dictionary=True)

        # Query to fetch the role based on the role_id and check if it's active
        sql = "SELECT accessModules FROM tbl_role WHERE id=%s and active=%s"
        cursor.execute(sql, (role_id, 1))
        role = cursor.fetchone()

        # Check if the role exists
        if not role:
            return jsonify({"error": "Role not found"}), 404

        # Get existing access modules for the role
        access_modules = json.loads(role['accessModules'])

        # Check if the module to remove exists in the access list
        if module_to_remove not in access_modules:
            return jsonify({"error": "Module not found in the access list"}), 404

        # Remove the specified module from the list
        access_modules.remove(module_to_remove)

        # Update the role's accessModules in the database
        sql = "UPDATE tbl_role SET accessModules=%s WHERE id=%s"
        cursor.execute(sql, (json.dumps(access_modules), role_id))
        g.db.commit()

        return jsonify({"message": "Module removed successfully", "modules": access_modules}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400