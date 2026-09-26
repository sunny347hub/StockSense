from flask import Blueprint, request, jsonify
from database import get_db_connection

transfers_bp = Blueprint("transfers", __name__, url_prefix="/api/transfers")


@transfers_bp.route("", methods=["POST"])
def create_transfer():
    data = request.json

    product_id = data.get("product_id")
    from_location = data.get("from_location")
    to_location = data.get("to_location")
    quantity = data.get("quantity")

    if not product_id or not from_location or not to_location or not quantity:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    if from_location == to_location:
        return jsonify({
            "status": "error",
            "message": "Source and destination cannot be the same"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, quantity
        FROM stock
        WHERE product_id=%s AND location_id=%s""",
        (product_id, from_location)
    )

    source_stock = cursor.fetchone()

    if not source_stock or source_stock[1] < quantity:
        cursor.close()
        conn.close()

        return jsonify({
            "status": "error",
            "message": "Insufficient stock at source location"
        }), 400

    cursor.execute(
        """INSERT INTO transfers
        (source_location_id, destination_location_id, status)
        VALUES (%s, %s, %s)""",
        (from_location, to_location, "Done")
    )

    transfer_id = cursor.lastrowid

    cursor.execute(
        """INSERT INTO transfer_items
        (transfer_id, product_id, quantity)
        VALUES (%s, %s, %s)""",
        (transfer_id, product_id, quantity)
    )

    cursor.execute(
        """UPDATE stock
        SET quantity = quantity - %s
        WHERE product_id=%s AND location_id=%s""",
        (quantity, product_id, from_location)
    )

    cursor.execute(
        """SELECT id
        FROM stock
        WHERE product_id=%s AND location_id=%s""",
        (product_id, to_location)
    )

    destination_stock = cursor.fetchone()

    if destination_stock:
        cursor.execute(
            """UPDATE stock
            SET quantity = quantity + %s
            WHERE id=%s""",
            (quantity, destination_stock[0])
        )
    else:
        cursor.execute(
            """INSERT INTO stock
            (product_id, location_id, quantity)
            VALUES (%s, %s, %s)""",
            (product_id, to_location, quantity)
        )

    cursor.execute(
        """INSERT INTO stock_ledger
        (product_id, location_id, movement_type, quantity, reference_type, reference_id)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            product_id,
            from_location,
            "OUT",
            quantity,
            "Transfer",
            transfer_id
        )
    )

    cursor.execute(
        """INSERT INTO stock_ledger
        (product_id, location_id, movement_type, quantity, reference_type, reference_id)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            product_id,
            to_location,
            "IN",
            quantity,
            "Transfer",
            transfer_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Stock transferred successfully",
        "transfer_id": transfer_id
    }), 201


@transfers_bp.route("", methods=["GET"])
def get_transfers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.id,
            t.source_location_id AS from_location,
            t.destination_location_id AS to_location,
            t.status,
            t.created_at
        FROM transfers t
        ORDER BY t.id DESC
    """)

    transfers = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(transfers)