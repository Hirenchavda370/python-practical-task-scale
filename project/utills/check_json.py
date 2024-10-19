from flask import request, jsonify
from functools import wraps


def json_validation(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            if request.content_type == "application/json":
                data = request.get_json()
            else:
                data = request.form.to_dict()
        except:
            return jsonify({"error": "Invalid JSON format"}), 400

        return func(data, *args, **kwargs)

    return decorated_function
