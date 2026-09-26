from flask import Blueprint, request, jsonify
from database import get_db_connection

receipts_bp = Blueprint("receipts", __name__, url_prefix="/api/receipts")


@receipts_bp.route("", methods=["POST"])
def create_receipt():
    data = request.json

    supplier = data.get("supplier")
    location_id = data.get("location_id")
    items = data.get("items", [])

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO receipts (supplier, location_id, status) VALUES (%s, %s, %s)",
        (supplier, location_id, "Done")
    )

    receipt_id = cursor.lastrowid

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        cursor.execute(
            "INSERT INTO receipt_items (receipt_id, product_id, quantity) VALUES (%s, %s, %s)",
            (receipt_id, product_id, quantity)
        )

        cursor.execute(
            "SELECT id FROM stock WHERE product_id=%s AND location_id=%s",
            (product_id, location_id)
        )

        stock = cursor.fetchone()

        if stock:
            cursor.execute(
                "UPDATE stock SET quantity = quantity + %s WHERE id=%s",
                (quantity, stock[0])
            )
        else:
            cursor.execute(
                "INSERT INTO stock (product_id, location_id, quantity) VALUES (%s, %s, %s)",
                (product_id, location_id, quantity)
            )

        cursor.execute(
            """INSERT INTO stock_ledger
            (product_id, location_id, movement_type, quantity, reference_type, reference_id)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (product_id, location_id, "IN", quantity, "Receipt", receipt_id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Receipt created successfully"
    }), 201


@receipts_bp.route("", methods=["GET"])
def get_receipts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM receipts ORDER BY id DESC")
    receipts = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(receipts)