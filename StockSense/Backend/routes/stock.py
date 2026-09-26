from flask import Blueprint, request, jsonify
from database import get_db_connection

stock_bp = Blueprint(
    "stock",
    __name__,
    url_prefix="/api/stock"
)


@stock_bp.route("", methods=["GET"])
def get_stock():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            s.id,
            s.product_id,
            p.name AS product,
            p.sku,
            s.location_id,
            l.name AS location,
            w.name AS warehouse,
            s.quantity
        FROM stock s
        JOIN products p ON s.product_id = p.id
        JOIN locations l ON s.location_id = l.id
        JOIN warehouses w ON l.warehouse_id = w.id
        ORDER BY s.id DESC
        """
    )

    stock = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "stock": stock
    }), 200


@stock_bp.route("", methods=["POST"])
def create_stock():
    data = request.get_json()

    product_id = data.get("product_id")
    location_id = data.get("location_id")
    quantity = data.get("quantity", 0)

    if not product_id or not location_id:
        return jsonify({
            "status": "error",
            "message": "Product and location are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id
        FROM stock
        WHERE product_id = %s AND location_id = %s
        """,
        (product_id, location_id)
    )

    existing_stock = cursor.fetchone()

    if existing_stock:
        cursor.execute(
            """
            UPDATE stock
            SET quantity = quantity + %s
            WHERE product_id = %s AND location_id = %s
            """,
            (quantity, product_id, location_id)
        )
    else:
        cursor.execute(
            """
            INSERT INTO stock (product_id, location_id, quantity)
            VALUES (%s, %s, %s)
            """,
            (product_id, location_id, quantity)
        )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Stock updated successfully"
    }), 200