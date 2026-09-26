from flask import Blueprint, request, jsonify
from database import get_db_connection

adjustments_bp = Blueprint("adjustments", __name__, url_prefix="/api/adjustments")


@adjustments_bp.route("", methods=["POST"])
def create_adjustment():
    data = request.json

    product_id = data.get("product_id")
    location_id = data.get("location_id")
    counted_quantity = data.get("counted_quantity")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, quantity FROM stock WHERE product_id=%s AND location_id=%s",
        (product_id, location_id)
    )

    stock = cursor.fetchone()

    if stock:
        current_quantity = stock[1]
        difference = counted_quantity - current_quantity

        cursor.execute(
            "UPDATE stock SET quantity=%s WHERE id=%s",
            (counted_quantity, stock[0])
        )
    else:
        difference = counted_quantity

        cursor.execute(
            """INSERT INTO stock
            (product_id, location_id, quantity)
            VALUES (%s, %s, %s)""",
            (product_id, location_id, counted_quantity)
        )

    cursor.execute(
        """INSERT INTO adjustments
        (product_id, location_id, counted_quantity, difference)
        VALUES (%s, %s, %s, %s)""",
        (product_id, location_id, counted_quantity, difference)
    )

    adjustment_id = cursor.lastrowid

    movement_type = "IN" if difference >= 0 else "OUT"

    cursor.execute(
        """INSERT INTO stock_ledger
        (product_id, location_id, movement_type, quantity, reference_type, reference_id)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            product_id,
            location_id,
            movement_type,
            abs(difference),
            "Adjustment",
            adjustment_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Stock adjustment completed",
        "difference": difference
    }), 201


@adjustments_bp.route("", methods=["GET"])
def get_adjustments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            a.id,
            p.name AS product,
            l.name AS location,
            a.counted_quantity,
            a.difference,
            a.created_at
        FROM adjustments a
        JOIN products p ON a.product_id = p.id
        JOIN locations l ON a.location_id = l.id
        ORDER BY a.id DESC
    """)

    adjustments = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(adjustments)