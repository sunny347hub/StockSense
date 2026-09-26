from flask import Blueprint, request, jsonify
from database import get_db_connection

warehouses_bp = Blueprint(
    "warehouses",
    __name__,
    url_prefix="/api/warehouses"
)


@warehouses_bp.route("", methods=["POST"])
def create_warehouse():
    data = request.get_json()

    name = data.get("name")
    location = data.get("location")

    if not name:
        return jsonify({
            "status": "error",
            "message": "Warehouse name is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "INSERT INTO warehouses (name, location) VALUES (%s, %s)",
        (name, location)
    )

    connection.commit()
    warehouse_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Warehouse created successfully",
        "warehouse": {
            "id": warehouse_id,
            "name": name,
            "location": location
        }
    }), 201


@warehouses_bp.route("", methods=["GET"])
def get_warehouses():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name, location, created_at
        FROM warehouses
        ORDER BY id DESC
        """
    )

    warehouses = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "warehouses": warehouses
    }), 200


@warehouses_bp.route("/<int:warehouse_id>/locations", methods=["POST"])
def create_location(warehouse_id):
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({
            "status": "error",
            "message": "Location name is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM warehouses WHERE id = %s",
        (warehouse_id,)
    )

    warehouse = cursor.fetchone()

    if not warehouse:
        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Warehouse not found"
        }), 404

    cursor.execute(
        """
        INSERT INTO locations (warehouse_id, name)
        VALUES (%s, %s)
        """,
        (warehouse_id, name)
    )

    connection.commit()
    location_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "message": "Location created successfully",
        "location": {
            "id": location_id,
            "warehouse_id": warehouse_id,
            "name": name
        }
    }), 201


@warehouses_bp.route("/<int:warehouse_id>/locations", methods=["GET"])
def get_locations(warehouse_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, warehouse_id, name
        FROM locations
        WHERE warehouse_id = %s
        ORDER BY id DESC
        """,
        (warehouse_id,)
    )

    locations = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        "status": "success",
        "locations": locations
    }), 200