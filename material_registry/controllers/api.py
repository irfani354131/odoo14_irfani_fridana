# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request

# Helper: serialize record
def _material_to_dict(m):
    return {
        "id": m.id,
        "code": m.code,
        "name": m.name,
        "type": m.type,  # fabric/jeans/cotton
        "type_label": dict(m._fields["type"].selection).get(m.type),
        "buy_price": m.buy_price,
        "supplier_id": m.supplier_id.id if m.supplier_id else False,
        "supplier_name": m.supplier_id.name if m.supplier_id else False,
    }

class MaterialAPIController(http.Controller):
    # List + filter by type (e.g. ?type=fabric)
    @http.route("/api/materials", type="http", auth="user", methods=["GET"], csrf=False)
    def list_materials(self, **params):
        domain = []
        mat_type = params.get("type")
        if mat_type:
            domain.append(("type", "=", mat_type))
        records = request.env["material.material"].sudo().search(domain, order="id desc")
        data = [_material_to_dict(r) for r in records]
        return request.make_response(
            json.dumps({"count": len(data), "results": data}),
            headers=[("Content-Type", "application/json")],
        )

    # Get by id
    @http.route("/api/materials/<int:rec_id>", type="http", auth="user", methods=["GET"], csrf=False)
    def get_material(self, rec_id, **kw):
        rec = request.env["material.material"].sudo().browse(rec_id).exists()
        if not rec:
            return request.make_response(json.dumps({"error": "Not found"}), status=404)
        return request.make_response(
            json.dumps(_material_to_dict(rec)),
            headers=[("Content-Type", "application/json")],
        )

    # Create
    @http.route("/api/materials", type="json", auth="user", methods=["POST"], csrf=False)
    def create_material(self, **payload):
        vals = {
            "code": payload.get("code"),
            "name": payload.get("name"),
            "type": payload.get("type"),
            "buy_price": payload.get("buy_price"),
            "supplier_id": payload.get("supplier_id"),
        }
        rec = request.env["material.material"].sudo().create(vals)
        return _material_to_dict(rec)

    # Update (partial allowed)
    @http.route("/api/materials/<int:rec_id>", type="json", auth="user", methods=["PUT"], csrf=False)
    def update_material(self, rec_id, **payload):
        rec = request.env["material.material"].sudo().browse(rec_id).exists()
        if not rec:
            return {"error": "Not found"}
        allowed = {"code", "name", "type", "buy_price", "supplier_id"}
        vals = {k: v for k, v in payload.items() if k in allowed}
        rec.write(vals)
        rec.flush()  
        return _material_to_dict(rec)

    # Delete
    @http.route("/api/materials/<int:rec_id>", type="http", auth="user", methods=["DELETE"], csrf=False)
    def delete_material(self, rec_id, **kw):
        rec = request.env["material.material"].sudo().browse(rec_id).exists()
        if not rec:
            return request.make_response(json.dumps({"error": "Not found"}), status=404)
        rec.unlink()
        return request.make_response(json.dumps({"status": "ok"}), headers=[("Content-Type", "application/json")])
