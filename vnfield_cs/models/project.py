from odoo import api, fields, models, exceptions
from odoo.tools.float_utils import float_compare


class Project(models.Model):
    _inherit = "vnfield.project"
    external_id = fields.Integer()
    changed_by_is = fields.Boolean()
