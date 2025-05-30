from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    organization_name = fields.Char(string="Organization")
    external_login = fields.Char(string="External login")
    external_password = fields.Char(string="External passwrd")
    external_api_key = fields.Char(string="External api key")
