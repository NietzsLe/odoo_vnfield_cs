from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"
    external_id = fields.Integer()
    changed_by_is = fields.Boolean()

    organization_name = fields.Char(string="Organization")
    external_login = fields.Char(string="External login")
    external_password = fields.Char(string="External password")
    external_api_key = fields.Char(string="External api key")
    external_id = fields.Integer(string="External id")
