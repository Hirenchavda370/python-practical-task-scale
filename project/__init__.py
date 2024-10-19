from flask import Flask, g, jsonify, request
import mysql.connector
import os
from datetime import timedelta
from project.user import user_bp
from project.authentication import authentication_bp
from project.role import role_bp
from project.access_module import access_module_bp
from flask_jwt_extended import JWTManager

# Initialize Flask application
app = Flask(__name__)

# Error handler for 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"message": "Method not allowed"}), 405

# Initialize JWT manager
jwt = JWTManager(app)

# Function to run before each request
@app.before_request
def before_request():
    try:
        # Establish a database connection
        g.db = mysql.connector.connect(
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            database=os.environ["MYSQL_DB"],
            host=os.environ["MYSQL_HOST"],
        )
        header = request.headers
        api_key = header.get('Api-Key')  # Retrieve the API key from headers
        
        if not api_key:
            return jsonify({'error': "Api key is not found"}), 404
        else:
            if os.environ['SECRET_KEY'] != api_key:
                return jsonify({'error': "Please enter a valid api key"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Return error if connection fails

# Function to run after each request
@app.after_request
def after_request(response):
    try:
        g.db.close()  # Close the database connection
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Return error if closing fails

# Configure JWT settings
app.config["JWT_SECRET_KEY"] = os.environ["SECRET_KEY"]  # Set the secret key for JWT
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)  # Set expiration for access token

# Register blueprints for different modules
app.register_blueprint(authentication_bp)
app.register_blueprint(role_bp)
app.register_blueprint(user_bp)
app.register_blueprint(access_module_bp)