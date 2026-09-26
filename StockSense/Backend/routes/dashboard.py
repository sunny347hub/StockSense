from flask import Blueprint, jsonify
from database import get_db_connection

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard_bp.route("", methods=["GET"])
def get_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_products FROM products")
    total_products = cursor.fetchone()["total_products"]

    cursor.execute("""
        SELECT COUNT(*) AS low_stock
        FROM products p
        LEFT JOIN (
            SELECT product_id, SUM(quantity) AS total_quantity
            FROM stock
            GROUP BY product_id
        ) s ON p.id = s.product_id
        WHERE COALESCE(s.total_quantity, 0) > 0
        AND COALESCE(s.total_quantity, 0) <= p.reorder_level
    """)
    low_stock = cursor.fetchone()["low_stock"]

    cursor.execute("""
        SELECT COUNT(*) AS out_of_stock
        FROM products p
        LEFT JOIN (
            SELECT product_id, SUM(quantity) AS total_quantity
            FROM stock
            GROUP BY product_id
        ) s ON p.id = s.product_id
        WHERE COALESCE(s.total_quantity, 0) = 0
    """)
    out_of_stock = cursor.fetchone()["out_of_stock"]

    cursor.execute("""
        SELECT COUNT(*) AS pending_receipts
        FROM receipts
        WHERE status != 'Done'
    """)
    pending_receipts = cursor.fetchone()["pending_receipts"]

    cursor.execute("""
        SELECT COUNT(*) AS pending_deliveries
        FROM deliveries
        WHERE status != 'Done'
    """)
    pending_deliveries = cursor.fetchone()["pending_deliveries"]

    cursor.execute("""
        SELECT COUNT(*) AS internal_transfers
        FROM transfers
        WHERE status != 'Done'
    """)
    internal_transfers = cursor.fetchone()["internal_transfers"]

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "dashboard": {
            "total_products": total_products,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "pending_receipts": pending_receipts,
            "pending_deliveries": pending_deliveries,
            "internal_transfers": internal_transfers
        }
    }), 200
