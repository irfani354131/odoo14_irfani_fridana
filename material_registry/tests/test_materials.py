# -*- coding: utf-8 -*-
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError
from psycopg2.errors import UniqueViolation
from odoo.tools.misc import mute_logger


class TestMaterial(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.Material = cls.env["material.material"]
        cls.supplier = cls.Partner.create({
            "name": "Supplier A",
        })

    def test_01_create_valid_material(self):
        rec = self.Material.create({
            "code": "MAT-001",
            "name": "Blue Fabric",
            "type": "fabric",
            "buy_price": 150.0,
            "supplier_id": self.supplier.id,
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.type, "fabric")
        self.assertGreaterEqual(rec.buy_price, 100.0)

    def test_02_price_constraint(self):
        with self.assertRaises(ValidationError):
            self.Material.create({
                "code": "MAT-002",
                "name": "Cheap Cotton",
                "type": "cotton",
                "buy_price": 50.0,
                "supplier_id": self.supplier.id,
            })

    def test_03_unique_code(self):
        self.Material.create({
            "code": "MAT-003",
            "name": "Jeans 1",
            "type": "jeans",
            "buy_price": 200.0,
            "supplier_id": self.supplier.id,
        })
        with self.assertRaises(UniqueViolation), mute_logger('odoo.sql_db'):
            self.Material.create({
                "code": "MAT-003",
                "name": "Jeans 2",
                "type": "jeans",
                "buy_price": 210.0,
                "supplier_id": self.supplier.id,
            })

    def test_04_filter_by_type(self):
        self.Material.create({
            "code": "MAT-010",
            "name": "Fab A",
            "type": "fabric",
            "buy_price": 120.0,
            "supplier_id": self.supplier.id,
        })
        self.Material.create({
            "code": "MAT-011",
            "name": "Cot B",
            "type": "cotton",
            "buy_price": 130.0,
            "supplier_id": self.supplier.id,
        })
        fabrics = self.Material.search([("type", "=", "fabric")])
        self.assertTrue(fabrics)
        for f in fabrics:
            self.assertEqual(f.type, "fabric")

    def test_05_update_delete(self):
        rec = self.Material.create({
            "code": "MAT-020",
            "name": "To Update",
            "type": "jeans",
            "buy_price": 180.0,
            "supplier_id": self.supplier.id,
        })
        rec.write({"name": "Updated Name", "buy_price": 250.0})
        self.assertEqual(rec.name, "Updated Name")
        self.assertEqual(rec.buy_price, 250.0)
        rec.unlink()
        self.assertFalse(rec.exists())
