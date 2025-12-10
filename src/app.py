import os
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error

from db import (
    create_customer,
    delete_customer,
    get_customer_by_id,
    init_db,
    list_customers,
    update_customer,
)

app = Flask(__name__)
CORS(app)

# Initialize DB on startup.
try:
    init_db()
except Error as exc:
    app.logger.error("DB init failed: %s", exc)
    raise

ALLOWED_GENDERS = {"male", "female"}


def validate_customer_payload(payload: Dict[str, Any]):
    errors = []
    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    gender = (payload.get("gender") or "").strip().lower()

    if not name:
        errors.append("姓名不能为空")
    if not phone:
        errors.append("联系电话不能为空")
    if gender not in ALLOWED_GENDERS:
        errors.append("性别只能是 male 或 female")

    return errors, {"name": name, "phone": phone, "gender": gender}


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/customers", methods=["POST"])
def add_customer():
    payload = request.get_json(force=True, silent=True) or {}
    errors, cleaned = validate_customer_payload(payload)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        customer_id = create_customer(cleaned)
        customer = get_customer_by_id(customer_id)
        return jsonify(customer), 201
    except Error as exc:
        app.logger.exception("Failed to create customer")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/customers", methods=["GET"])
def list_customers_route():
    try:
        page = max(1, int(request.args.get("page", 1)))
        page_size = int(request.args.get("page_size", 10))
        page_size = max(1, min(page_size, 100))
    except ValueError:
        return jsonify({"error": "分页参数必须是数字"}), 400

    try:
        rows, total = list_customers(page, page_size)
        return jsonify(
            {
                "data": rows,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size,
                },
            }
        )
    except Error as exc:
        app.logger.exception("Failed to list customers")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id: int):
    try:
        customer = get_customer_by_id(customer_id)
        if not customer:
            return jsonify({"error": "客户不存在"}), 404
        return jsonify(customer)
    except Error as exc:
        app.logger.exception("Failed to get customer")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
def update_customer_route(customer_id: int):
    payload = request.get_json(force=True, silent=True) or {}
    errors, cleaned = validate_customer_payload(payload)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        updated = update_customer(customer_id, cleaned)
        if not updated:
            return jsonify({"error": "客户不存在"}), 404
        customer = get_customer_by_id(customer_id)
        return jsonify(customer)
    except Error as exc:
        app.logger.exception("Failed to update customer")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer_route(customer_id: int):
    try:
        deleted = delete_customer(customer_id)
        if not deleted:
            return jsonify({"error": "客户不存在"}), 404
        return jsonify({"status": "deleted"})
    except Error as exc:
        app.logger.exception("Failed to delete customer")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
