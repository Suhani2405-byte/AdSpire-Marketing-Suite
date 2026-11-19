"""Brand profiles: saved product/brand presets that pre-fill the campaign form."""
from flask import Blueprint, request, jsonify, g

from services import database_service as db
from services.auth_service import login_required

brand_bp = Blueprint("brands", __name__)

FIELDS = {"name": 150, "industry": 100, "tone": 100, "audience": 300, "description": 3000}


def _clean(data):
    return {k: str(data.get(k) or "").strip()[:limit] for k, limit in FIELDS.items()}


@brand_bp.route("", methods=["GET"])
@login_required
def list_brands():
    return jsonify({"success": True, "brands": db.list_brands(g.user.id)}), 200


@brand_bp.route("", methods=["POST"])
@login_required
def create_brand():
    fields = _clean(request.get_json(silent=True) or {})
    if not fields["name"]:
        return jsonify({"success": False, "error": "Brand name is required."}), 400
    return jsonify({"success": True, "brand": db.create_brand(g.user.id, **fields)}), 201


@brand_bp.route("/<int:brand_id>", methods=["PUT"])
@login_required
def update_brand(brand_id):
    fields = _clean(request.get_json(silent=True) or {})
    if not fields["name"]:
        return jsonify({"success": False, "error": "Brand name is required."}), 400
    brand = db.update_brand(brand_id, g.user.id, **fields)
    if not brand:
        return jsonify({"success": False, "error": "Brand not found."}), 404
    return jsonify({"success": True, "brand": brand}), 200


@brand_bp.route("/<int:brand_id>", methods=["DELETE"])
@login_required
def delete_brand(brand_id):
    if not db.delete_brand(brand_id, g.user.id):
        return jsonify({"success": False, "error": "Brand not found."}), 404
    return jsonify({"success": True}), 200
