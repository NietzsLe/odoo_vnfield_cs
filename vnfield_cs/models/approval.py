# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Saneen K (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models, http
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class Approval(models.Model):
    _inherit = "vnfield.approval"

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
