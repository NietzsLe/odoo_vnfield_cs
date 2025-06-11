from odoo import api, fields, models, _, exceptions
from odoo.tools.float_utils import float_compare


class Task(models.Model):
    _inherit = "vnfield.task"
    external_id = fields.Integer()
    changed_by_is = fields.Boolean()

    def to_dict(self):
        self.ensure_one()
        result = {}
        for field in self._fields:
            if field in [
                "__last_update",
                "create_date",
                "write_date",
                "external_id",
                "id",
                "changed_by_is",
            ]:
                continue
            f = self._fields[field]
            if (
                not isinstance(f, fields.Many2one)
                and not isinstance(f, fields.Many2many)
                and not isinstance(f, fields.One2many)
                and self[field]
            ):
                result[field] = self[field]
        return result
