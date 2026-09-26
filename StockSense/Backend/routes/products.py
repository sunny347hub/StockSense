from flask import Blueprint, request, jsonify
from database import get_db_connection

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.route("", methods=["POST"])
def create_product():
    data = request.get_json()

    name = data.get("name")
    sku = data.get("sku")
    category_id = data.get("category_id")
    unit = data.get("unit")
    initial_stock = data.get("initial_stock", 0)
    reorder_level = data.get("reorder_level", 0)

    if not name or not sku or not unit:
        return jsonify({
            "status": "error",
            "message": "Name, SKU and unit are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM products WHERE sku = %s",
        (sku,)
    )

    existing_product = cursor.fetchone()

    if existing_product:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "SKU already exists"
        }), 409

    cursor.execute(
        """
        INSERT INTO products
        (name, sku, category_id, unit, initial_stock, reorder_level)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            sku,
            category_id,
            unit,
            initial_stock,
            reorder_level
        )
    )

    connection.commit()
    product_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Product created successfully",
        "product": {
            "id": product_id,
            "name": name,
            "sku": sku,
            "category_id": category_id,
            "unit": unit,
            "initial_stock": initial_stock,
            "reorder_level": reorder_level
        }
    }), 201


@products_bp.route("", methods=["GET"])
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            p.id,
            p.name,
            p.sku,
            p.category_id,
            c.name AS category,
            p.unit,
            p.initial_stock,
            p.reorder_level,
            p.created_at
        FROM products p
        LEFT JOIN categories c
        ON p.category_id = c.id
        ORDER BY p.id DESC
        """
    )

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "products": products
    }), 200


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            p.id,
            p.name,
            p.sku,
            p.category_id,
            c.name AS category,
            p.unit,
            p.initial_stock,
            p.reorder_level,
            p.created_at
        FROM products p
        LEFT JOIN categories c
        ON p.category_id = c.id
        WHERE p.id = %s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if not product:
        return jsonify({
            "status": "error",
            "message": "Product not found"
        }), 404

    return jsonify({
        "status": "success",
        "product": product
    }), 200


@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()

    name = data.get("name")
    sku = data.get("sku")
    category_id = data.get("category_id")
    unit = data.get("unit")
    initial_stock = data.get("initial_stock", 0)
    reorder_level = data.get("reorder_level", 0)

    if not name or not sku or not unit:
        return jsonify({
            "status": "error",
            "message": "Name, SKU and unit are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Product not found"
        }), 404

    cursor.execute(
        """
        SELECT id
        FROM products
        WHERE sku = %s AND id != %s
        """,
        (sku, product_id)
    )

    duplicate_sku = cursor.fetchone()

    if duplicate_sku:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "SKU already exists"
        }), 409

    cursor.execute(
        """
        UPDATE products
        SET name = %s,
            sku = %s,
            category_id = %s,
            unit = %s,
            initial_stock = %s,
            reorder_level = %s
        WHERE id = %s
        """,
        (
            name,
            sku,
            category_id,
            unit,
            initial_stock,
            reorder_level,
            product_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Product updated successfully"
    }), 200


@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Product not found"
        }), 404

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (product_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Product deleted successfully"
    }), 200