from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Email already registered"
        }), 409

    hashed_password = generate_password_hash(password)

    cursor.execute(
        """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """,
        (name, email, hashed_password)
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Account created successfully",
        "user": {
            "id": user_id,
            "name": name,
            "email": email
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name, email, password
        FROM users
        WHERE email = %s
        """,
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(user["password"], password):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200