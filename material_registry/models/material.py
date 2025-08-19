# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Material(models.Model):
    _name = "material.material"
    _description = "Material"
    _rec_name = "name"
    _order = "create_date desc"

    code = fields.Char("Material Code", required=True, index=True)
    name = fields.Char("Material Name", required=True)
    type = fields.Selection(
        [
            ("fabric", "Fabric"),
            ("jeans", "Jeans"),
            ("cotton", "Cotton"),
        ],
        string="Material Type",
        required=True, 
        index=True,
    )
    buy_price = fields.Float("Material Buy Price", required=True)
    supplier_id = fields.Many2one(
        "res.partner",
        string="Related Supplier",
        domain=[("supplier_rank", ">", 0)],
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        ("code_unique", "unique(code)", "Material Code must be unique."),
    ]

    @api.constrains("buy_price")
    def _check_buy_price(self):
        for rec in self:
            if rec.buy_price is None:
                raise ValidationError(_("Material Buy Price is required."))
            if rec.buy_price < 100:
                raise ValidationError(_("Material Buy Price must be >= 100."))
