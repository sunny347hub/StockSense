from flask import Blueprint, request, jsonify
from database import get_db_connection

deliveries_bp = Blueprint("deliveries", __name__, url_prefix="/api/deliveries")


@deliveries_bp.route("", methods=["POST"])
def create_delivery():
    data = request.json

    customer = data.get("customer")
    location_id = data.get("location_id")
    items = data.get("items", [])

    conn = get_db_connection()
    cursor = conn.cursor()

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        cursor.execute(
            "SELECT id, quantity FROM stock WHERE product_id=%s AND location_id=%s",
            (product_id, location_id)
        )

        stock = cursor.fetchone()

        if not stock or stock[1] < quantity:
            cursor.close()
            conn.close()
            return jsonify({
                "status": "error",
                "message": "Insufficient stock"
            }), 400

    cursor.execute(
        "INSERT INTO deliveries (customer, location_id, status) VALUES (%s, %s, %s)",
        (customer, location_id, "Done")
    )

    delivery_id = cursor.lastrowid

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        cursor.execute(
            """INSERT INTO delivery_items
            (delivery_id, product_id, quantity)
            VALUES (%s, %s, %s)""",
            (delivery_id, product_id, quantity)
        )

        cursor.execute(
            """UPDATE stock
            SET quantity = quantity - %s
            WHERE product_id=%s AND location_id=%s""",
            (quantity, product_id, location_id)
        )

        cursor.execute(
            """INSERT INTO stock_ledger
            (product_id, location_id, movement_type, quantity, reference_type, reference_id)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (product_id, location_id, "OUT", quantity, "Delivery", delivery_id)
        )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Delivery created successfully"
    }), 201


@deliveries_bp.route("", methods=["GET"])
def get_deliveries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM deliveries ORDER BY id DESC")
    deliveries = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(deliveries)