from flask import Blueprint, request, jsonify
from database import get_db_connection

categories_bp = Blueprint(
    "categories",
    __name__,
    url_prefix="/api/categories"
)


@categories_bp.route("", methods=["POST"])
def create_category():
    data = request.get_json()

    name = data.get("name")

    if not name:
        return jsonify({
            "status": "error",
            "message": "Category name is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM categories WHERE name = %s",
        (name,)
    )

    existing_category = cursor.fetchone()

    if existing_category:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Category already exists"
        }), 409

    cursor.execute(
        "INSERT INTO categories (name) VALUES (%s)",
        (name,)
    )

    connection.commit()

    category_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Category created successfully",
        "category": {
            "id": category_id,
            "name": name
        }
    }), 201


@categories_bp.route("", methods=["GET"])
def get_categories():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name
        FROM categories
        ORDER BY name
        """
    )

    categories = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "categories": categories
    }), 200


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name
        FROM categories
        WHERE id = %s
        """,
        (category_id,)
    )

    category = cursor.fetchone()

    cursor.close()
    connection.close()

    if not category:
        return jsonify({
            "status": "error",
            "message": "Category not found"
        }), 404

    return jsonify({
        "status": "success",
        "category": category
    }), 200


@categories_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    data = request.get_json()

    name = data.get("name")

    if not name:
        return jsonify({
            "status": "error",
            "message": "Category name is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM categories WHERE id = %s",
        (category_id,)
    )

    category = cursor.fetchone()

    if not category:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Category not found"
        }), 404

    cursor.execute(
        """
        SELECT id
        FROM categories
        WHERE name = %s AND id != %s
        """,
        (name, category_id)
    )

    duplicate = cursor.fetchone()

    if duplicate:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Category already exists"
        }), 409

    cursor.execute(
        """
        UPDATE categories
        SET name = %s
        WHERE id = %s
        """,
        (name, category_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Category updated successfully"
    }), 200


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM categories WHERE id = %s",
        (category_id,)
    )

    category = cursor.fetchone()

    if not category:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Category not found"
        }), 404

    cursor.execute(
        "DELETE FROM categories WHERE id = %s",
        (category_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Category deleted successfully"
    }), 200