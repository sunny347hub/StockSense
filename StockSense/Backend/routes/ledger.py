from flask import Blueprint, jsonify
from database import get_db_connection

ledger_bp = Blueprint(
    "ledger",
    __name__,
    url_prefix="/api/ledger"
)


@ledger_bp.route("", methods=["GET"])
def get_ledger():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sl.id,
            p.name AS product,
            p.sku,
            l.name AS location,
            sl.movement_type,
            sl.quantity,
            sl.reference_type,
            sl.reference_id,
            sl.created_at
        FROM stock_ledger sl
        JOIN products p
            ON sl.product_id = p.id
        JOIN locations l
            ON sl.location_id = l.id
        ORDER BY sl.id DESC
    """)

    ledger = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "ledger": ledger
    }), 200