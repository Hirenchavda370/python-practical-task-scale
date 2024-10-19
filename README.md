# python-practical-task-scale

# User and Role Management API

# Introduction
This project is a User and Role Management System built using Python Flask. It allows you to manage user accounts and roles, including access control for specific modules within the application. The API supports essential user management features like role-based access control, login/signup, and user searches. It is designed with modular functionality, implementing CRUD operations for users, roles, and access modules.

# Features
1. User and Role CRUD: Create, retrieve, update, and delete users and roles.
2. Login and Signup: APIs for user authentication (sign-in and sign-up).
3. Role-Based Access Control: Assign roles to users and manage their access to different modules.
4. Access Module Management: Handle the list of accessible modules for each role.
5. Bulk User Updates: Update multiple users in one request.
6. Search Functionality: Search for users with partial matching.

# Python Version
Python 3.8+ required

# Dependencies
To run this project, you will need to install the following Python libraries:

1. Flask==3.0.3: For building the web framework
2. Flask-JWT-Extended==4.6.0: For handling authentication via JSON Web Tokens
3. mysql-connector-python==9.1.0: For MySQL database connection
4. python-dotenv==1.0.1: For loading environment variables from a .env file
5. Werkzeug==3.0.4: A comprehensive WSGI web application library

# Install all dependencies using the following command:
pip install -r requirements.txt


# Project Structure

app/
│
├── authentication/
│   ├── __init__.py
│   ├── authentication.py   # Handles user signup and signin
│
├── role/
│   ├── __init__.py
│   ├── role.py   # CRUD operations for Role module
│
├── user/
│   ├── __init__.py
│   ├── user.py   # CRUD and search functionality for users
│
├── access_module/
│   ├── __init__.py
│   ├── access_module.py   # CRUD operations for access modules
│
├── config.py       # Configuration settings (database, secret key, etc.)
├── app.py          # Main application startup
├── extensions.py   # Flask extensions setup
└── requirements.txt

# Database Configuration
The application uses a MySQL database, and the credentials are stored in a .env file. You need to create this file in the root directory and include the following variables:

1. MYSQL_HOST=<your-mysql-host>
2. MYSQL_USER=<your-mysql-username>
3. MYSQL_PASSWORD=<your-mysql-password>
4. MYSQL_DB=<your-mysql-database-name>

# Running the Project Locally
1. Environment Setup
Ensure you have Python 3.8+ installed on your machine. Create a virtual environment using the following command:

python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

2. Dependency Installation
Install the necessary dependencies with:

pip install -r requirements.txt

3. Database Setup
Ensure you have MySQL installed and running. Configure the credentials in the .env file as mentioned above.

4. Running the Application
flask run
