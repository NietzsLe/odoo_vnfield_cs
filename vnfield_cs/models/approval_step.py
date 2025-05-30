from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError, UserError


class ApprovalStep(models.Model):
    _inherit = "vnfield.approval.step"

    external_id = fields.Integer()

    def to_dict(self):
        self.ensure_one()
        result = {}
        for field in self._fields:
            if field in ["id", "__last_update", "create_date", "write_date"]:
                continue
            f = self._fields[field]
            if isinstance(f, fields.Many2one):
                result[field] = self[field].id  # ID thôi, không phải dict
            elif isinstance(f, fields.Many2many):
                result[field] = [(6, 0, self[field].ids)]  # Command format
            elif isinstance(f, fields.One2many):
                result[field] = [(0, 0, line.to_dict()) for line in self[field]]
            else:
                result[field] = self[field]
        return result
